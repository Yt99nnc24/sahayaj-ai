import sys, io, sqlite3
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest, fitz
from backend import create_app, extract

@pytest.fixture
def app(tmp_path):
    return create_app({'TESTING':True,'SECRET_KEY':'test-secret','DATABASE':str(tmp_path/'db.sqlite'),'UPLOAD_FOLDER':str(tmp_path/'reports'),'DOCTOR_CODE':'invite'})
def request(client,url,method='post',data=None,**kw):
    token=client.get('/api/session').json['csrf']
    return getattr(client,method)(url,json=data,headers={'X-CSRF-Token':token},**kw)
def signup(client,email,role='patient'):
    return request(client,'/api/register',data=dict(name='Fictional User',email=email,password='SyntheticPass!23',role=role,code='invite'))
def login(client,email): return request(client,'/api/login',data=dict(email=email,password='SyntheticPass!23'))
def intake(): return dict(name='Fictional Patient',age='30',complaint='Digestive discomfort',duration='3 days',severity='4',agni='Manda',allergies='None reported')
def pdf():
    d=fitz.open(); p=d.new_page();p.insert_text((40,40),'FICTIONAL LAB REPORT\nHemoglobin 12.5 g/dL 12.0-16.0\nDate: 2026-10-12');b=d.tobytes();d.close();return b
def upload(client,cid,content=None,name='sample.pdf'):
    token=client.get('/api/session').json['csrf'];return client.post(f'/api/cases/{cid}/reports',data={'file':(io.BytesIO(content or pdf()),name)},headers={'X-CSRF-Token':token})

def test_auth_roles_csrf_and_invalid_credentials(app):
    c=app.test_client(); assert c.get('/api/cases').status_code==401
    assert c.post('/api/register',json={}).status_code==403
    assert signup(c,'p@example.test').status_code==201
    assert signup(c,'d@example.test','doctor').status_code==201
    assert signup(c,'p@example.test').status_code==409
    assert request(c,'/api/login',data=dict(email='p@example.test',password='wrong')).status_code==401
    assert login(c,'p@example.test').status_code==200
    assert request(c,'/api/cases/1/review',method='put',data={}).status_code==403
    assert request(c,'/api/profile',method='put',data={'name':'Updated'}).status_code==200
    assert c.get('/api/session').json['user']['name']=='Updated'
    assert request(c,'/api/logout').status_code==200
    assert c.get('/api/cases').status_code==401

def test_full_workflow_ownership_evidence_and_persistence(app):
    p=app.test_client();d=app.test_client();other=app.test_client();otherdoc=app.test_client()
    for c,email,role in [(p,'p@example.test','patient'),(d,'d@example.test','doctor'),(other,'other@example.test','patient'),(otherdoc,'otherdoc@example.test','doctor')]:
        assert signup(c,email,role).status_code==201; assert login(c,email).status_code==200
    r=request(p,'/api/cases',data=intake()); assert r.status_code==201;cid=r.json['id']
    assert len(d.get('/api/cases').json)==1; assert other.get('/api/cases').json==[]; assert otherdoc.get('/api/cases').json==[]
    assert other.get(f'/api/cases/{cid}').status_code==403;assert otherdoc.get(f'/api/cases/{cid}').status_code==403
    assert upload(p,cid,name='unsafe.exe').status_code==415
    assert upload(p,cid,b'not a PDF').status_code==415
    u=upload(p,cid); assert u.status_code==201;rid=u.json['id'];assert u.json['extraction']['findings'][0]['value']=='12.5'
    assert other.get(f'/api/reports/{rid}').status_code==403;assert otherdoc.get(f'/api/reports/{rid}').status_code==403
    assert d.get(f'/api/reports/{rid}').status_code==200
    case=d.get(f'/api/cases/{cid}').json;fid=case['reports'][0]['findings'][0]['id']
    assert len(case['reports'][0]['findings'])==1
    assert '2026-10-12' in case['reports'][0]['extraction']['dates']
    assert 'Hemoglobin: 12.5' in case['summary']
    review=dict(summary='Verified intake and source report.',assessment='Fictional clinician assessment',recommendations='Fictional clinician-authored advice',flags_reviewed=True,finalize=True)
    assert request(d,f'/api/cases/{cid}/review',method='put',data=review).status_code==400
    assert request(p,f'/api/findings/{fid}',method='put',data={'status':'accepted'}).status_code==403
    assert request(d,f'/api/findings/{fid}',method='put',data={'status':'corrected','corrected':'Hemoglobin 12.5 g/dL; source verified'}).status_code==200
    review['finalize']=False;assert request(d,f'/api/cases/{cid}/review',method='put',data=review).status_code==200
    assert p.get(f'/api/cases/{cid}').json['assessment']==''
    assert upload(p,cid).status_code==409
    review['finalize']=True;assert request(d,f'/api/cases/{cid}/review',method='put',data=review).status_code==200
    case=p.get(f'/api/cases/{cid}').json; assert case['status']=='Completed';assert case['assessment']==review['assessment']
    exported=p.get(f'/api/cases/{cid}/export');assert exported.status_code==200
    with fitz.open(stream=exported.data,filetype='pdf') as doc: assert 'Fictional clinician assessment' in ''.join(x.get_text() for x in doc)
    assert request(d,f'/api/cases/{cid}/review',method='put',data=review).status_code==409
    assert request(d,f'/api/findings/{fid}',method='put',data={'status':'rejected'}).status_code==409
    newapp=create_app(dict(app.config));newclient=newapp.test_client();login(newclient,'p@example.test');assert newclient.get('/api/cases').json[0]['status']=='Completed'
    with sqlite3.connect(app.config['DATABASE']) as conn: assert conn.execute('SELECT count(*) FROM audit').fetchone()[0]>=5

def test_validation_flags_and_extraction_fallback(app,tmp_path):
    c=app.test_client();signup(c,'p@example.test');login(c,'p@example.test')
    assert request(c,'/api/cases',data=intake()).status_code==409
    signup(c,'d@example.test','doctor')
    bad=intake();bad['age']='200';assert request(c,'/api/cases',data=bad).status_code==400
    data=intake();data['complaint']='Chest pain';r=request(c,'/api/cases',data=data);assert r.json['flags'][0]['category']=='Immediate Human Assessment Recommended'
    from PIL import Image
    im=Image.new('RGB',(100,100),'white');b=io.BytesIO();im.save(b,format='PNG')
    result=upload(c,r.json['id'],b.getvalue(),'scan.png');assert result.status_code==201;assert result.json['extraction']['status']=='manual_review_required'
    assert c.get(f'/api/cases/{r.json["id"]}/export').status_code==409
    path=tmp_path/'bad.pdf';path.write_bytes(b'bad');assert extract(path)['status']=='failed'

def test_doctor_invitation_and_password_hash(app):
    c=app.test_client();assert request(c,'/api/register',data=dict(name='Doctor',email='d@example.test',role='doctor',password='SyntheticPass!23',code='wrong')).status_code==403
    signup(c,'p@example.test')
    with sqlite3.connect(app.config['DATABASE']) as conn: assert 'SyntheticPass!23' not in conn.execute('SELECT password FROM users').fetchone()[0]

def test_size_limit_and_login_throttle(app):
    c=app.test_client();signup(c,'p@example.test');signup(c,'d@example.test','doctor');login(c,'p@example.test');cid=request(c,'/api/cases',data=intake()).json['id']
    assert upload(c,cid,b'x'*(13*1024*1024),'big.pdf').status_code==413
    for _ in range(10): assert request(c,'/api/login',data={'email':'unknown@example.test','password':'wrong'}).status_code==401
    assert request(c,'/api/login',data={'email':'unknown@example.test','password':'wrong'}).status_code==429

def test_initialization_backup_and_template(app,tmp_path):
    legacy=tmp_path/'legacy.db'
    with sqlite3.connect(legacy) as c:
        c.execute('CREATE TABLE old_records(id INTEGER, note TEXT)');c.execute("INSERT INTO old_records VALUES(1,'fictional retained record')")
    create_app({'TESTING':True,'DATABASE':str(legacy),'UPLOAD_FOLDER':str(tmp_path/'private'),'SECRET_KEY':'test'})
    assert list(tmp_path.glob('legacy.db.backup-*'))
    with sqlite3.connect(legacy) as c: assert c.execute('SELECT note FROM old_records').fetchone()[0]=='fictional retained record'
    client=app.test_client();response=client.get('/');assert response.status_code==200
    assert b'SAHAYAJ AI' in response.data;assert "default-src 'self'" in response.headers['Content-Security-Policy']
    assert client.get('/static/portal.js').status_code==200
