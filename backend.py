import os, re, json, sqlite3, secrets, shutil, functools, time, hashlib
from pathlib import Path
from datetime import datetime, timezone
import fitz
from PIL import Image
from flask import Flask, request, session, jsonify, render_template, send_file, abort, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from assistant_service import load_env, ask_offline, BRANCHES, LANGUAGES

ROOT = Path(__file__).parent
FIELDS = ['name','age','sex','complaint','duration','severity','history','medications','allergies','observations','agni','koshtha','prakriti','digestion','sleep','diet','lifestyle','medical_branch','specialty']
def now(): return datetime.now(timezone.utc).isoformat()
def extract(path):
    pages=[]; method='selectable PDF text'; status='completed'
    try:
        if path.suffix=='.pdf':
            with fitz.open(stream=path.read_bytes(),filetype='pdf') as doc:
                if len(doc)>40: raise ValueError('Maximum 40 pages per report')
                for i,p in enumerate(doc):
                    txt=p.get_text()
                    if not txt.strip():
                        try:
                            import pytesseract
                            pix=p.get_pixmap(matrix=fitz.Matrix(1.5,1.5))
                            txt=pytesseract.image_to_string(Image.frombytes('RGB',[pix.width,pix.height],pix.samples),timeout=20)
                            method='OCR; manual verification required'
                        except Exception: txt=''; status='manual_review_required'
                    pages.append((i+1,txt))
        else:
            method='OCR; manual verification required'
            try:
                import pytesseract
                with Image.open(path) as im: pages=[(1,pytesseract.image_to_string(im,timeout=20))]
            except Exception: status='manual_review_required'
        findings=[]
        for page,txt in pages:
            for line in txt.splitlines():
                if re.match(r'\s*(date|age|patient|name|report|id|sex|sample)\b',line,re.I): continue
                m=re.match(r'^\s*([A-Za-z][A-Za-z ()-]{2,50}?)\s*[:\s]\s*(\d+(?:\.\d+)?)\s*([A-Za-zµ/%0-9.^-]+)?(?:\s+(.*))?$',line)
                if m:
                    findings.append(dict(test_name=m[1].strip(),value=m[2],unit=m[3] or '',reference_range=m[4] or '',source_text=line,page=page,review_required=True))
        return dict(status=status,method=method,pages=[dict(page=p,text=t) for p,t in pages],findings=findings,dates=re.findall(r'\b\d{1,4}[-/]\d{1,2}[-/]\d{1,4}\b','\n'.join(t for _,t in pages)))
    except Exception as e: return dict(status='failed',error=str(e),pages=[],findings=[],dates=[])

def flags(data):
    result=[]; text=(data.get('complaint','')+' '+data.get('observations','')).lower()
    for phrase in ['chest pain','difficulty breathing','loss of consciousness','severe bleeding']:
        if phrase in text: result.append(dict(category='Immediate Human Assessment Recommended',trigger=phrase,source='Patient complaint / observations',reviewed=False))
    if int(data.get('severity') or 0)>=8: result.append(dict(category='Priority Review',trigger='Self-reported severity ≥ 8; clinician context required',source='Patient severity',reviewed=False))
    return result

def create_app(config=None):
    load_env(ROOT/'.env')
    app=Flask(__name__); private=ROOT/'instance'; private.mkdir(exist_ok=True)
    secret=os.environ.get('SAHAYAJ_SECRET')
    if not secret:
        secret_path=private/'session.key'
        if not secret_path.exists(): secret_path.write_text(secrets.token_hex(32))
        secret=secret_path.read_text()
    app.config.update(SECRET_KEY=secret,DATABASE=os.environ.get('SAHAYAJ_DATABASE',str(private/'database.db')),UPLOAD_FOLDER=str(private/'reports'),MAX_CONTENT_LENGTH=12*1024*1024,SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE='Lax',SESSION_COOKIE_SECURE=os.environ.get('SAHAYAJ_SECURE_COOKIE')=='1',DOCTOR_CODE=os.environ.get('SAHAYAJ_DOCTOR_CODE',''))
    if config: app.config.update(config)
    app.config['SESSION_COOKIE_NAME']='sahayaj_'+hashlib.sha256(str(Path(app.config['DATABASE']).resolve()).encode()).hexdigest()[:12]
    app.config.setdefault('AI_MODE',os.environ.get('SAHAYAJ_AI_MODE','auto'))
    app.config.setdefault('LOCAL_MODEL',os.environ.get('SAHAYAJ_LOCAL_MODEL','qwen2.5:1.5b'))
    login_attempts={}
    chat_attempts={}
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True,exist_ok=True)
    def db():
        c=sqlite3.connect(app.config['DATABASE']); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); return c
    with db() as c:
        exists=c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        user_schema=c.execute("SELECT sql FROM sqlite_master WHERE name='users'").fetchone()
        if user_schema and 'email TEXT UNIQUE' in user_schema[0]:
            shutil.copy2(app.config['DATABASE'],app.config['DATABASE']+'.backup-role-emails-'+datetime.now().strftime('%Y%m%d%H%M%S'))
            c.executescript('''PRAGMA foreign_keys=OFF; BEGIN;
            CREATE TABLE users_role_migration(id INTEGER PRIMARY KEY,email TEXT NOT NULL,password TEXT NOT NULL,role TEXT NOT NULL,name TEXT NOT NULL,UNIQUE(email,role));
            INSERT INTO users_role_migration SELECT id,email,password,role,name FROM users;
            DROP TABLE users; ALTER TABLE users_role_migration RENAME TO users; COMMIT; PRAGMA foreign_keys=ON;''')
        if exists and not c.execute("SELECT name FROM sqlite_master WHERE name='schema_version'").fetchone():
            shutil.copy2(app.config['DATABASE'],app.config['DATABASE']+'.backup-'+datetime.now().strftime('%Y%m%d%H%M%S'))
        c.executescript('''CREATE TABLE IF NOT EXISTS schema_version(version INTEGER); INSERT INTO schema_version SELECT 1 WHERE NOT EXISTS(SELECT 1 FROM schema_version);
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, email TEXT NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL, name TEXT NOT NULL,UNIQUE(email,role));
        CREATE TABLE IF NOT EXISTS cases(id INTEGER PRIMARY KEY, patient_id INTEGER REFERENCES users(id), doctor_id INTEGER REFERENCES users(id), created TEXT, status TEXT, intake TEXT, flags TEXT, summary TEXT, assessment TEXT DEFAULT '', recommendations TEXT DEFAULT '', finalized TEXT);
        CREATE TABLE IF NOT EXISTS reports(id INTEGER PRIMARY KEY, case_id INTEGER REFERENCES cases(id), filename TEXT, stored TEXT, extraction TEXT);
        CREATE TABLE IF NOT EXISTS findings(id INTEGER PRIMARY KEY, report_id INTEGER REFERENCES reports(id), original TEXT, corrected TEXT, review_status TEXT DEFAULT 'pending');
        CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,user_id INTEGER,case_id INTEGER,action TEXT,details TEXT,created TEXT);
        CREATE TABLE IF NOT EXISTS account_aliases(alias TEXT,role TEXT,user_id INTEGER REFERENCES users(id),UNIQUE(alias,role));
        CREATE TABLE IF NOT EXISTS legacy_imports(source TEXT,entity TEXT,legacy_id INTEGER,new_id INTEGER,UNIQUE(source,entity,legacy_id));
        UPDATE schema_version SET version=2;''')
        c.execute('CREATE TABLE IF NOT EXISTS clinician_profiles(user_id INTEGER PRIMARY KEY REFERENCES users(id),medical_branch TEXT NOT NULL)')
    def audit(c,cid,action,details=''): c.execute('INSERT INTO audit(user_id,case_id,action,details,created) VALUES(?,?,?,?,?)',(session.get('uid'),cid,action,details,now()))
    def auth(role=None):
        def wrap(fn):
            @functools.wraps(fn)
            def inner(*args,**kw):
                if not session.get('uid'): abort(401)
                if role and session.get('role')!=role: abort(403)
                return fn(*args,**kw)
            return inner
        return wrap
    def owned(c,cid):
        row=c.execute('SELECT cases.*,users.name patient_name FROM cases JOIN users ON users.id=patient_id WHERE cases.id=?',(cid,)).fetchone()
        if not row: abort(404)
        if (session['role']=='patient' and row['patient_id']!=session['uid']) or (session['role']=='doctor' and row['doctor_id']!=session['uid']): abort(403)
        return dict(row)
    @app.before_request
    def csrf():
        if request.method in ['POST','PUT','DELETE'] and not secrets.compare_digest(request.headers.get('X-CSRF-Token',''),session.get('csrf','missing')): abort(403,description='Session expired. Refresh the page and try again.')
    @app.after_request
    def headers(r):
        r.headers['X-Content-Type-Options']='nosniff'; r.headers['Cache-Control']='no-store'; r.headers['Content-Security-Policy']="default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; frame-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'self'"; return r
    @app.errorhandler(400)
    @app.errorhandler(401)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(409)
    @app.errorhandler(413)
    @app.errorhandler(415)
    @app.errorhandler(429)
    @app.errorhandler(502)
    @app.errorhandler(503)
    def error(e): return jsonify(error=e.description),e.code
    @app.get('/')
    def index(): return render_template('landing.html')
    @app.get('/<role>/login')
    def portal_login(role):
        if role not in ['patient','doctor']: abort(404)
        return render_template('login.html',portal=role)
    @app.get('/patient')
    @app.get('/doctor')
    def portal():
        role=request.path[1:]
        if not session.get('uid'): return redirect('/'+role+'/login')
        if session.get('role')!=role: abort(403)
        return render_template('portal.html',portal=role,fields=FIELDS)
    @app.get('/login')
    @app.get('/login.html')
    def login_redirect(): return redirect('/')
    @app.get('/patient.html')
    @app.get('/doctor.html')
    def old_portal_redirect(): return redirect(request.path.removesuffix('.html'))
    @app.get('/api/session')
    def state():
        session.setdefault('csrf',secrets.token_hex(24))
        with db() as c:
            branch=c.execute('SELECT medical_branch FROM clinician_profiles WHERE user_id=?',(session.get('uid'),)).fetchone()
            demos=[r[0] for r in c.execute("SELECT role FROM users WHERE email=role||'@example.test'")]
        return jsonify(csrf=session['csrf'],user=dict(id=session['uid'],role=session['role'],name=session['name'],medical_branch=branch[0] if branch else BRANCHES[0]) if session.get('uid') else None,demo_roles=demos,assistant_configured=True,assistant_mode=app.config['AI_MODE'],assistant_model=app.config['LOCAL_MODEL'],branches=BRANCHES,languages=LANGUAGES)
    @app.post('/api/register')
    def register():
        d=request.get_json() or {}; role=d.get('role'); email=d.get('email','').strip().lower(); name=d.get('name','').strip(); pw=d.get('password','')
        if role not in ['patient','doctor'] or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email) or not 1<=len(name)<=100 or not 10<=len(pw)<=200: abort(400,description='Valid name, email, role and password (10+ characters) required')
        if role=='doctor' and not app.config['DOCTOR_CODE']: abort(403,description='Doctor registration is not configured. Set SAHAYAJ_DOCTOR_CODE in the local .env file and restart the server. Demo sign-in does not require a code.')
        if role=='doctor' and not secrets.compare_digest(d.get('code',''),app.config['DOCTOR_CODE']): abort(403,description='Invitation code does not match. Use the code configured by your clinic administrator.')
        branch=d.get('medical_branch',BRANCHES[0])
        if branch not in BRANCHES: abort(400,description='Choose a supported medical branch')
        try:
            with db() as c:
                uid=c.execute('INSERT INTO users(email,password,role,name) VALUES(?,?,?,?)',(email,generate_password_hash(pw),role,name)).lastrowid
                if role=='doctor': c.execute('INSERT INTO clinician_profiles VALUES(?,?)',(uid,branch))
                alias=d.get('alias','').strip()
                if alias:
                    if len(alias)>100: abort(400)
                    c.execute('INSERT INTO account_aliases(alias,role,user_id) VALUES(?,?,?)',(alias.lower(),role,uid))
        except sqlite3.IntegrityError: abort(409,description='Email already registered')
        return jsonify(ok=True),201
    @app.post('/api/login')
    @app.post('/api/patient/login')
    @app.post('/api/doctor/login')
    def login():
        d=request.get_json() or {}
        role=request.path.split('/')[2] if request.path!='/api/login' else d.get('role')
        identifier=d.get('email',d.get('login_id',d.get('staff_id',''))).lower().strip()
        key=(request.remote_addr,identifier); stamp=time.monotonic()
        attempts=[t for t in login_attempts.get(key,[]) if stamp-t<300]
        if len(attempts)>=10: abort(429,description='Too many login attempts. Try again in five minutes.')
        login_attempts[key]=attempts+[stamp]
        with db() as c:
            u=c.execute('SELECT * FROM users WHERE email=? AND (? IS NULL OR role=?)',(identifier,role,role)).fetchone()
            if not u and role in ['patient','doctor']:
                u=c.execute('SELECT users.* FROM users JOIN account_aliases ON users.id=account_aliases.user_id WHERE lower(alias)=? AND account_aliases.role=?',(identifier,role)).fetchone()
        if u and role and u['role']!=role: abort(401,description='This account belongs to the other portal. Use the correct sign-in page.')
        if not u or not check_password_hash(u['password'],d.get('password','')): abort(401,description='Invalid credentials')
        login_attempts.pop(key,None)
        session.clear(); session.update(uid=u['id'],role=u['role'],name=u['name'],csrf=secrets.token_hex(24)); return jsonify(ok=True,csrf=session['csrf'])
    @app.post('/api/logout')
    def logout(): session.clear(); return jsonify(ok=True)
    @app.put('/api/profile')
    @auth()
    def profile():
        data=request.get_json() or {}; name=data.get('name','').strip()
        if not 1<=len(name)<=100: abort(400)
        branch=data.get('medical_branch')
        if branch is not None and (session['role']!='doctor' or branch not in BRANCHES): abort(400)
        with db() as c:
            c.execute('UPDATE users SET name=? WHERE id=?',(name,session['uid']))
            if branch is not None: c.execute('INSERT INTO clinician_profiles VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET medical_branch=excluded.medical_branch',(session['uid'],branch))
        session['name']=name; return jsonify(ok=True)
    @app.post('/api/chat')
    @auth()
    def chat():
        data=request.get_json() or {}
        language=data.get('language','en'); messages=data.get('messages')
        if language not in LANGUAGES or not isinstance(messages,list) or not 1<=len(messages)<=12: abort(400,description='Choose a supported language and send 1–12 conversation messages.')
        if any(not isinstance(m,dict) or m.get('role') not in ['user','assistant'] or not isinstance(m.get('content'),str) or not 1<=len(m['content'].strip())<=4000 for m in messages) or messages[-1].get('role')!='user': abort(400,description='Invalid conversation format or message length (maximum 4,000).')
        messages=[{'role':m['role'],'content':m['content']} for m in messages]
        if sum(len(m['content']) for m in messages)>18000: abort(400,description='Conversation too long. Clear chat and start again.')
        context={}; cid=data.get('case_id')
        if cid is not None:
            if type(cid) is not int or cid<1: abort(400,description='Invalid consultation identifier')
            if session['role']!='doctor': abort(403)
            with db() as c:
                row=owned(c,cid); intake=json.loads(row['intake'])
                # Explicit clinician opt-in sends only selected fields; no identity or raw report files.
                context={'intake':{k:v for k,v in intake.items() if k!='name'},'findings':[]}
                for f in c.execute('SELECT findings.* FROM findings JOIN reports ON reports.id=report_id WHERE case_id=?',(cid,)):
                    original=json.loads(f['original'])
                    context['findings'].append({'test_name':original.get('test_name'),'value':original.get('value'),'unit':original.get('unit'),'reference_range':original.get('reference_range'),'review_status':f['review_status'],'correction':f['corrected']})
        stamp=time.monotonic(); recent=[t for t in chat_attempts.get(session['uid'],[]) if stamp-t<60]
        if len(recent)>=6: abort(429,description='Please wait a minute before asking more questions.')
        chat_attempts[session['uid']]=recent+[stamp]
        try: answer=ask_offline(app.config['AI_MODE'],app.config['LOCAL_MODEL'],session['role'],language,messages,context)
        except RuntimeError as exc: abort(502,description=str(exc))
        with db() as c: audit(c,cid,'assistant request',answer['provider']+'; role='+session['role']+'; language='+language+'; case context='+str(cid is not None))
        return jsonify(**answer,review_required=True)
    @app.get('/api/cases')
    @auth()
    def cases():
        col='patient_id' if session['role']=='patient' else 'doctor_id'
        with db() as c: rows=c.execute(f'SELECT cases.*,users.name patient_name FROM cases JOIN users ON users.id=patient_id WHERE {col}=? ORDER BY cases.id DESC',(session['uid'],)).fetchall()
        return jsonify([dict(id=r['id'],patient_name=r['patient_name'],created=r['created'],status=r['status'],intake=json.loads(r['intake']),flags=json.loads(r['flags'])) for r in rows])
    @app.post('/api/cases')
    @auth('patient')
    def submit():
        raw=request.get_json() or {}; d={k:str(raw.get(k,'')).strip() for k in FIELDS}
        d['medical_branch']=d['medical_branch'] or BRANCHES[0]
        if d['medical_branch'] not in BRANCHES: abort(400,description='Choose a supported medical branch')
        if d['medical_branch']!='Ayurveda':
            for key in ['agni','koshtha','prakriti']: d[key]=''
        if any(len(v)>4000 for v in d.values()) or not d['complaint'] or not d['duration']: abort(400,description='Complaint and duration required; maximum 4,000 characters per field')
        try:
            if not 0<=int(d['severity'])<=10 or not 0<=int(d['age'])<=120: raise ValueError()
        except ValueError: abort(400,description='Age must be 0–120; severity 0–10')
        f=flags(d); summary='Documentation draft — clinician review required.\n'+'\n'.join(f'{k}: {v} [source: patient intake/{k}]' for k,v in d.items() if v)+'\nMissing information: '+', '.join(k for k,v in d.items() if not v and (d['medical_branch']=='Ayurveda' or k not in ['agni','koshtha','prakriti']))+'\nClarify patient-reported observations and verify all report fields. No diagnosis inferred.'
        with db() as c:
            doc=c.execute("SELECT users.id FROM users LEFT JOIN clinician_profiles ON users.id=clinician_profiles.user_id WHERE role='doctor' AND COALESCE(medical_branch,?)=? ORDER BY users.id LIMIT 1",(BRANCHES[0],d['medical_branch'])).fetchone()
            if not doc: abort(409,description='No clinician is registered for this branch yet. Ask your clinic to add one, or choose General / unsure for a general consultation.')
            cid=c.execute('INSERT INTO cases(patient_id,doctor_id,created,status,intake,flags,summary) VALUES(?,?,?,?,?,?,?)',(session['uid'],doc['id'],now(),'Priority Review' if f else 'Awaiting Review',json.dumps(d),json.dumps(f),summary)).lastrowid; audit(c,cid,'case submitted')
        return jsonify(id=cid,flags=f),201
    @app.get('/api/cases/<int:cid>')
    @auth()
    def detail(cid):
        with db() as c:
            row=owned(c,cid)
            for k in ['intake','flags']: row[k]=json.loads(row[k])
            row['reports']=[]
            for r in c.execute('SELECT * FROM reports WHERE case_id=?',(cid,)):
                rp=dict(r); rp.pop('stored'); rp['extraction']=json.loads(rp['extraction']); rp['findings']=[dict(f) for f in c.execute('SELECT * FROM findings WHERE report_id=?',(r['id'],))]; row['reports'].append(rp)
            if session['role']=='patient' and row['status']!='Completed':
                for k in ['summary','assessment','recommendations']: row[k]=''
            row['audit']=[dict(a) for a in c.execute('SELECT action,details,created FROM audit WHERE case_id=? ORDER BY id',(cid,))] if session['role']=='doctor' else []
            row['history']=[dict(h) for h in c.execute("SELECT id,created,status FROM cases WHERE patient_id=? AND id!=? AND doctor_id=? ORDER BY id DESC",(row['patient_id'],cid,row['doctor_id']))]
        return jsonify(row)
    @app.post('/api/cases/<int:cid>/reports')
    @auth('patient')
    def upload(cid):
        with db() as c:
            row=owned(c,cid)
            if row['status'] in ['In Progress','Completed']: abort(409,description='Reports are locked once review starts')
            if c.execute('SELECT count(*) FROM reports WHERE case_id=?',(cid,)).fetchone()[0]>=5: abort(400,description='Maximum 5 reports')
            file=request.files.get('file'); suffix=Path(file.filename or '').suffix.lower() if file else ''
            if suffix not in ['.pdf','.jpg','.jpeg','.png']: abort(415,description='PDF, JPG or PNG required')
            path=Path(app.config['UPLOAD_FOLDER'])/(secrets.token_hex(20)+suffix); file.save(path)
            try:
                if suffix=='.pdf':
                    with fitz.open(stream=path.read_bytes(),filetype='pdf') as pdf:
                        if not pdf.is_pdf or pdf.is_encrypted or len(pdf)>40: raise ValueError()
                else:
                    with Image.open(path) as im:
                        if im.format not in ['JPEG','PNG']: raise ValueError()
                        im.verify()
            except Exception: path.unlink(missing_ok=True); abort(415,description='Invalid, encrypted or oversized document')
            result=extract(path); rid=c.execute('INSERT INTO reports(case_id,filename,stored,extraction) VALUES(?,?,?,?)',(cid,Path(file.filename).name,str(path),json.dumps(result))).lastrowid
            for f in result['findings']: c.execute('INSERT INTO findings(report_id,original) VALUES(?,?)',(rid,json.dumps(f)))
            evidence='\nReport evidence — unverified extraction; clinician review required:\n'+'\n'.join(f'{f["test_name"]}: {f["value"]} {f["unit"]}; printed range: {f["reference_range"] or "not supplied"} [source: report {rid}, page {f["page"]}; text: {f["source_text"]}]' for f in result['findings'])
            if not result['findings']: evidence+=f'No structured findings extracted from report {rid}. Inspect original document manually.'
            c.execute('UPDATE cases SET summary=summary || ? WHERE id=?',(evidence,cid))
            audit(c,cid,'report uploaded',json.dumps(dict(report_id=rid,status=result['status'])))
        return jsonify(id=rid,extraction=result),201
    @app.get('/api/reports/<int:rid>')
    @auth()
    def document(rid):
        with db() as c:
            r=c.execute('SELECT * FROM reports WHERE id=?',(rid,)).fetchone()
            if not r: abort(404)
            owned(c,r['case_id'])
        return send_file(r['stored'],download_name=r['filename'])
    @app.put('/api/findings/<int:fid>')
    @auth('doctor')
    def finding(fid):
        d=request.get_json() or {}
        if d.get('status') not in ['accepted','rejected','corrected']: abort(400)
        corrected=d.get('corrected','')
        if not isinstance(corrected,str) or len(corrected)>4000: abort(400)
        if d['status']=='corrected' and not corrected.strip(): abort(400)
        with db() as c:
            f=c.execute('SELECT findings.*,reports.case_id FROM findings JOIN reports ON reports.id=report_id WHERE findings.id=?',(fid,)).fetchone()
            if not f: abort(404)
            row=owned(c,f['case_id'])
            if row['status']=='Completed': abort(409)
            c.execute('UPDATE findings SET corrected=?,review_status=? WHERE id=?',(corrected,d['status'],fid)); audit(c,f['case_id'],'finding reviewed',json.dumps(dict(finding_id=fid,original=f['original'],correction=corrected,status=d['status'])))
        return jsonify(ok=True)
    @app.put('/api/cases/<int:cid>/review')
    @auth('doctor')
    def review(cid):
        d=request.get_json() or {}; final=d.get('finalize') is True
        if any(not isinstance(d.get(k,''),str) or len(d.get(k,''))>20000 for k in ['summary','assessment','recommendations']): abort(400)
        with db() as c:
            row=owned(c,cid)
            if row['status']=='Completed': abort(409,description='Finalized consultations are immutable')
            pending=c.execute("SELECT count(*) FROM findings JOIN reports ON report_id=reports.id WHERE case_id=? AND review_status='pending'",(cid,)).fetchone()[0]
            if final and (pending or not d.get('assessment','').strip() or not d.get('recommendations','').strip() or not d.get('flags_reviewed')): abort(400,description='Review every finding and flag; assessment and recommendations required')
            f=json.loads(row['flags'])
            if d.get('flags_reviewed'):
                for x in f: x['reviewed']=True
            c.execute('UPDATE cases SET summary=?,assessment=?,recommendations=?,status=?,flags=?,finalized=? WHERE id=?',(d.get('summary',row['summary']),d.get('assessment',''),d.get('recommendations',''),'Completed' if final else 'In Progress',json.dumps(f),now() if final else None,cid)); audit(c,cid,'consultation finalized' if final else 'draft saved',json.dumps(d))
        return jsonify(ok=True)
    @app.get('/api/cases/<int:cid>/export')
    @auth()
    def export(cid):
        with db() as c: row=owned(c,cid)
        if row['status']!='Completed': abort(409)
        from io import BytesIO
        doc=fitz.open(); text=f'SAHAYAJ AI | Clinician-approved consultation\nCase {cid} | {row["patient_name"]}\nFinalized: {row["finalized"]}\n\n'+row['summary']+'\n\nClinician assessment\n'+row['assessment']+'\n\nApproved recommendations\n'+row['recommendations']
        import textwrap
        lines=[]
        for line in text.splitlines(): lines.extend(textwrap.wrap(line,85) or [''])
        for start in range(0,len(lines),48): doc.new_page().insert_text((40,40),'\n'.join(lines[start:start+48]),fontsize=10)
        content=doc.tobytes(); doc.close(); return send_file(BytesIO(content),mimetype='application/pdf',as_attachment=True,download_name=f'consultation-{cid}.pdf')
    return app

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--init',action='store_true'); p.add_argument('--demo',action='store_true'); args=p.parse_args(); app=create_app()
    if args.demo:
        with sqlite3.connect(app.config['DATABASE']) as c:
            for email,role,name in [('patient@example.test','patient','Aarav Demo'),('doctor@example.test','doctor','Dr. Meera Demo')]: c.execute('INSERT OR IGNORE INTO users(email,password,role,name) VALUES(?,?,?,?)',(email,generate_password_hash('DemoPassword!2026'),role,name))
        sample=ROOT/'demo'; sample.mkdir(exist_ok=True); doc=fitz.open(); page=doc.new_page(); page.insert_text((60,60),'FICTIONAL DEMO - NOT A REAL MEDICAL REPORT\nDate: 2026-10-12\nHemoglobin 12.5 g/dL 12.0-16.0\nGlucose 95 mg/dL 70-100'); (sample/'synthetic-report.pdf').write_bytes(doc.tobytes()); doc.close(); print('Demo accounts ready. Patient/doctor: patient@example.test / doctor@example.test; password: DemoPassword!2026')
    elif not args.init: app.run(host='127.0.0.1',port=int(os.environ.get('SAHAYAJ_PORT','5000')),debug=False)
