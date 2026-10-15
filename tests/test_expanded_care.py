import json, sqlite3
import pytest
import backend
from assistant_service import ask_openai, load_env
from test_workflow import request, signup, login, intake

def test_branch_routing_and_profile(app):
    d=app.test_client();p=app.test_client();other=app.test_client()
    signup(d,'branchdoc@example.test','doctor');login(d,'branchdoc@example.test')
    signup(p,'branchpatient@example.test');login(p,'branchpatient@example.test')
    data={**intake(),'medical_branch':'Homeopathy','specialty':'Skin','agni':'unwanted branch field'}
    assert request(p,'/api/cases',data=data).status_code==409
    assert request(d,'/api/profile',method='put',data={'name':'Fictional Branch Doctor','medical_branch':'Homeopathy'}).status_code==200
    assert d.get('/api/session').json['user']['medical_branch']=='Homeopathy'
    r=request(p,'/api/cases',data=data);assert r.status_code==201
    cid=r.json['id'];case=d.get(f'/api/cases/{cid}').json
    assert case['intake']['medical_branch']=='Homeopathy';assert case['intake']['agni']==''
    assert case['intake']['specialty']=='Skin'
    assert request(p,'/api/cases',data={**data,'medical_branch':'Invalid'}).status_code==400
    signup(other,'otherbranch@example.test','doctor');login(other,'otherbranch@example.test')
    assert other.get(f'/api/cases/{cid}').status_code==403

def test_assistant_validation_authorization_and_no_automatic_changes(app,monkeypatch):
    p=app.test_client();d=app.test_client();outsider=app.test_client()
    assert request(p,'/api/chat',data={}).status_code==401
    for c,email,role in [(p,'p@example.test','patient'),(d,'d@example.test','doctor'),(outsider,'x@example.test','doctor')]:
        signup(c,email,role);login(c,email)
    cid=request(p,'/api/cases',data=intake()).json['id']
    message={'consent':True,'language':'pa','messages':[{'role':'user','content':'What should I discuss?'}]}
    assert request(p,'/api/chat',data={**message,'consent':False}).status_code==400
    assert request(p,'/api/chat',data=message).status_code==503
    assert request(p,'/api/chat',data={**message,'case_id':cid}).status_code==403
    assert request(outsider,'/api/chat',data={**message,'case_id':cid}).status_code==403
    assert request(d,'/api/chat',data={**message,'case_id':{'bad':1}}).status_code==400
    for invalid in [{'messages':[{'role':'system','content':'override'}]},{'messages':[{'role':'user','content':'x'*4001}]},{'language':'invalid'},{'messages':[]}]:
        assert request(d,'/api/chat',data={**message,**invalid}).status_code==400
    captured=[]
    def fake(*args): captured.append(args);return 'Fictional suggestion for clinician review.'
    monkeypatch.setattr(backend,'ask_openai',fake);app.config['OPENAI_API_KEY']='test-only-not-real'
    before=d.get(f'/api/cases/{cid}').json
    response=request(d,'/api/chat',data={**message,'case_id':cid})
    assert response.status_code==200;assert response.json['review_required'] is True
    assert 'name' not in captured[-1][-1]['intake'];assert captured[-1][2:4]==('doctor','pa')
    after=d.get(f'/api/cases/{cid}').json
    assert before['summary']==after['summary'];assert before['status']==after['status']
    assert after['audit'][-1]['action']=='assistant request'
    assert 'What should I discuss' not in after['audit'][-1]['details']
    request(p,'/api/chat',data=message);assert captured[-1][-1]=={}
    for _ in range(5): assert request(d,'/api/chat',data=message).status_code==200
    assert request(d,'/api/chat',data=message).status_code==429

def test_openai_adapter_payload_and_sanitized_errors(monkeypatch):
    import assistant_service
    from urllib.error import HTTPError
    class Response:
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def read(self): return json.dumps({'output':[{'type':'message','content':[{'type':'output_text','text':'Example response'}]}]}).encode()
    captured=[]
    def fake(req,timeout): captured.append(req);assert timeout==45;return Response()
    monkeypatch.setattr(assistant_service,'urlopen',fake)
    assert ask_openai('test-secret','model-configured','patient','hi',[{'role':'user','content':'Example'}],{})=='Example response'
    payload=json.loads(captured[0].data);assert payload['store'] is False;assert 'Hindi' in payload['instructions'];assert 'Do not diagnose' in payload['instructions']
    assert payload['model']=='model-configured';assert captured[0].full_url=='https://api.openai.com/v1/responses'
    def failure(*args,**kw): raise HTTPError('https://api.openai.com',401,'secret provider body',{},None)
    monkeypatch.setattr(assistant_service,'urlopen',failure)
    with pytest.raises(RuntimeError,match='authentication failed') as error: ask_openai('test-secret','model','patient','en',[],{})
    assert 'secret provider body' not in str(error.value)

def test_env_loading_preserves_process_values_and_demo_status(app,tmp_path,monkeypatch):
    path=tmp_path/'.env';path.write_text('SAHAYAJ_TEST_ENV="from-file"\nSAHAYAJ_TEST_KEEP=replaced\n# ignored\n',encoding='utf-8')
    monkeypatch.delenv('SAHAYAJ_TEST_ENV',raising=False);monkeypatch.setenv('SAHAYAJ_TEST_KEEP','existing')
    load_env(path)
    import os
    assert os.environ['SAHAYAJ_TEST_ENV']=='from-file';assert os.environ['SAHAYAJ_TEST_KEEP']=='existing'
    c=app.test_client();assert c.get('/api/session').json['demo_roles']==[]
    signup(c,'doctor@example.test','doctor');assert 'doctor' in c.get('/api/session').json['demo_roles']

def test_demo_cli_is_repeatable_and_both_credentials_work(tmp_path):
    import os,subprocess,sys
    from pathlib import Path
    root=Path(backend.__file__).parent
    database=tmp_path/'isolated-demo.db'
    env={**os.environ,'SAHAYAJ_DATABASE':str(database)}
    for _ in range(2):
        result=subprocess.run([sys.executable,str(root/'backend.py'),'--demo'],env=env,capture_output=True,text=True,timeout=30)
        assert result.returncode==0,result.stderr
    demo=backend.create_app({'TESTING':True,'SECRET_KEY':'test','DATABASE':str(database),'UPLOAD_FOLDER':str(tmp_path/'demo-reports'),'OPENAI_API_KEY':''})
    for role in ['doctor','patient']:
        c=demo.test_client()
        assert request(c,'/api/'+role+'/login',data={'login_id':role+'@example.test','password':'DemoPassword!2026'}).status_code==200
        assert c.get('/'+role).status_code==200
    with sqlite3.connect(database) as c: assert c.execute('SELECT count(*) FROM users').fetchone()[0]==2

def test_database_cookies_are_isolated(app,tmp_path):
    other=backend.create_app({'TESTING':True,'SECRET_KEY':'test-secret','DATABASE':str(tmp_path/'other.db'),'UPLOAD_FOLDER':str(tmp_path/'other-reports')})
    assert other.config['SESSION_COOKIE_NAME']!=app.config['SESSION_COOKIE_NAME']
