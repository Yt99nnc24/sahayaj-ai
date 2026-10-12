import sqlite3,json
from backend import create_app
from import_legacy import import_legacy
from test_workflow import request,signup,login

def test_separate_portals_and_role_login(app):
    c=app.test_client();html=c.get('/').data
    assert b'/patient/login' in html and b'/doctor/login' in html
    assert b'patient app' in html
    assert c.get('/patient').status_code==302
    assert c.get('/patient/login').status_code==200;assert c.get('/doctor/login').status_code==200
    signup(c,'p@example.test')
    assert request(c,'/api/doctor/login',data={'login_id':'p@example.test','password':'SyntheticPass!23'}).status_code==401
    assert request(c,'/api/patient/login',data={'login_id':'p@example.test','password':'SyntheticPass!23'}).status_code==200
    assert b'patient-app' in c.get('/patient').data
    assert c.get('/doctor').status_code==403
    assert c.get('/api/doctor/queue').status_code==404
    assert c.get('/patient.html').status_code==302

def test_signup_alias_and_doctor_shell(app):
    c=app.test_client()
    assert request(c,'/api/register',data={'role':'doctor','name':'Doctor Demo','email':'d@example.test','password':'SyntheticPass!23','code':'invite','alias':'STAFF-1'}).status_code==201
    assert request(c,'/api/doctor/login',data={'staff_id':'STAFF-1','password':'SyntheticPass!23'}).status_code==200
    assert b'clinical-sidebar' in c.get('/doctor').data
    assert c.get('/patient').status_code==403

def test_legacy_import_backups_idempotence_ownership_and_auth(app,tmp_path):
    from werkzeug.security import generate_password_hash
    source=tmp_path/'original.db'
    with sqlite3.connect(source) as c:
        c.executescript('CREATE TABLE patients(id INTEGER,full_name TEXT,email TEXT,identifier TEXT,password TEXT);CREATE TABLE doctors(id INTEGER,full_name TEXT,email TEXT,staff_id TEXT,password TEXT);CREATE TABLE intakes(id INTEGER,timestamp TEXT,patient_id TEXT,patient_name TEXT,chief_complaint TEXT,duration TEXT,severity INTEGER,agni_status TEXT,koshtha_status TEXT,dietary_fruits TEXT,notes TEXT,is_emergency INTEGER,doctor_diagnosis TEXT,doctor_prescription TEXT,status TEXT);')
        pw=generate_password_hash('SyntheticPass!23')
        c.execute('INSERT INTO patients VALUES(1,?,?,?,?)',('Synthetic Legacy Patient','shared-legacy@example.test','HEALTH-1',pw));c.execute('INSERT INTO doctors VALUES(1,?,?,?,?)',('Synthetic Legacy Doctor','shared-legacy@example.test','DOC-1',pw))
        c.execute('INSERT INTO intakes VALUES(1,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',('2026-10-01 12:00:00','HEALTH-1','Synthetic Legacy Patient','Original complaint','3 days',3,'Original agni','Original koshtha','[]','Original notes',0,'Original assessment','Original advice','COMPLETED'))
    before=source.read_bytes();report=import_legacy(source,app);assert report['accounts_imported']==2;assert report['cases_imported']==1;assert source.read_bytes()==before
    assert list((tmp_path/'backups').glob('legacy-source-*.db'));assert list((tmp_path/'backups').glob('before-import-*.db'))
    assert import_legacy(source,app)['already_imported']==1
    c=app.test_client();assert request(c,'/api/patient/login',data={'login_id':'HEALTH-1','password':'SyntheticPass!23'}).status_code==200
    row=c.get('/api/cases').json[0];detail=c.get('/api/cases/'+str(row['id'])).json;assert detail['assessment']=='Original assessment';assert detail['recommendations']=='Original advice'
    other=app.test_client();signup(other,'outsider@example.test');login(other,'outsider@example.test');assert other.get('/api/cases/'+str(row['id'])).status_code==403
    doctor=app.test_client();assert request(doctor,'/api/doctor/login',data={'staff_id':'DOC-1','password':'SyntheticPass!23'}).status_code==200;assert len(doctor.get('/api/cases').json)==1
