import json
import pytest
import assistant_service as service
from offline_knowledge import basic_reply
from test_workflow import request, signup, login

def message(text='How do I upload a report?'):
    return [{'role':'user','content':text}]

def test_basic_mode_never_contacts_a_model(monkeypatch):
    def forbidden(*args,**kwargs): raise AssertionError('Basic mode attempted networking')
    monkeypatch.setattr(service,'local_request',forbidden)
    answer=service.ask_offline('basic','qwen2.5:1.5b','patient','en',message(),{})
    assert 'Upload report' in answer['reply']
    assert answer['provider']=='Basic offline helper'
    for language,expected in [('hi','रिपोर्ट'),('pa','ਰਿਪੋਰਟ')]:
        assert expected in service.ask_offline('basic','qwen2.5:1.5b','patient',language,message(),{})['reply']

def test_urgent_message_does_not_wait_for_model(monkeypatch):
    monkeypatch.setattr(service,'ask_local',lambda *args: (_ for _ in ()).throw(AssertionError('Model called')))
    answer=service.ask_offline('ollama','qwen2.5:1.5b','patient','en',message('chest pain and cannot breathe'),{})
    assert 'immediate in-person' in answer['reply']
    assert answer['provider']=='Basic offline helper'

def test_unknown_and_medication_questions_do_not_invent_answers():
    assert 'limited knowledge' in basic_reply('patient','en',message('Solve quantum physics'),{})
    assert 'cannot select a medicine' in basic_reply('patient','en',message('Give me a tablet dose'),{})
    result=basic_reply('doctor','en',message('Review this case'),{'intake':{'name':'PRIVATE NAME','complaint':'PRIVATE TEXT'}})
    assert 'review checklist' in result
    assert 'PRIVATE' not in result

def test_local_model_contract(monkeypatch):
    calls=[]
    def fake(path,body,timeout):
        calls.append((path,body,timeout))
        if path=='/api/show': return {'details':{'parameter_size':'1.5B'}}
        return {'message':{'content':'Fictional review checklist.'},'done':True}
    monkeypatch.setattr(service,'local_request',fake)
    answer=service.ask_offline('ollama','qwen2.5:1.5b','doctor','hi',message('Review missing history'),{'intake':{'age':'30'}})
    assert answer['provider'].startswith('Ollama local model')
    path,body,timeout=calls[-1]
    assert path=='/api/chat' and body['stream'] is False
    assert body['options']['num_predict']==600 and timeout==90
    assert body['messages'][0]['role']=='system'
    assert 'Hindi' in body['messages'][0]['content']
    assert 'Do not diagnose' in body['messages'][0]['content']

def test_no_cloud_models_or_remote_model_aliases(monkeypatch):
    calls=[]
    monkeypatch.setattr(service,'local_request',lambda *args: calls.append(args) or {'remote_model':'cloud-secret','remote_host':'https://remote.example'})
    with pytest.raises(RuntimeError,match='Cloud'): service.ask_local('qwen2.5:1.5b','patient','en',message(),{})
    assert len(calls)==1 and calls[0][0]=='/api/show'
    with pytest.raises(RuntimeError,match='Cloud'): service.ask_local('some-model:cloud','patient','en',message(),{})
    assert len(calls)==1

def test_runtime_failure_fallback_is_labeled(monkeypatch):
    def unavailable(*args): raise OSError('provider details must not escape')
    monkeypatch.setattr(service,'ask_local',unavailable)
    answer=service.ask_offline('auto','qwen2.5:1.5b','patient','en',message(),{})
    assert answer['fallback'] is True and 'limited bundled guidance' in answer['notice']
    with pytest.raises(RuntimeError,match='Local model unavailable') as exc:
        service.ask_offline('ollama','qwen2.5:1.5b','patient','en',message(),{})
    assert 'provider details' not in str(exc.value)

def test_loopback_only_transport_disables_proxies_and_redirects(monkeypatch):
    calls=[]
    class Response:
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def read(self,size): return b'{"done":true}'
    class Opener:
        def open(self,req,timeout):
            calls.append(req)
            assert timeout==3
            return Response()
    def opener(*handlers):
        assert handlers[0].proxies=={}
        assert isinstance(handlers[1],service.NoRedirect)
        return Opener()
    monkeypatch.setattr(service,'build_opener',opener)
    service.local_request('/api/show',{'model':'qwen2.5:1.5b'},3)
    assert calls[0].full_url=='http://127.0.0.1:11434/api/show'
    assert not calls[0].has_header('Authorization')
    with pytest.raises(RuntimeError,match='redirects'):
        service.NoRedirect().redirect_request(None,None,302,'',{},'https://external.example')

def test_chat_runs_without_key_or_cloud_consent(app,monkeypatch):
    p=app.test_client()
    signup(p,'offline@example.test');login(p,'offline@example.test')
    app.config['AI_MODE']='basic'
    monkeypatch.setattr(service,'local_request',lambda *args: (_ for _ in ()).throw(AssertionError('Network request')))
    result=request(p,'/api/chat',data={'language':'hi','messages':message()})
    assert result.status_code==200
    assert result.json['provider']=='Basic offline helper'
    assert 'रिपोर्ट' in result.json['reply']
    assert app.test_client().get('/api/session').json['assistant_configured'] is True
