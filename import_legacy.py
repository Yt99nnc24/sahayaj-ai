"""Copy legacy MOA records into the new schema. Source is strictly read-only."""
import argparse,sqlite3,json
from pathlib import Path
from datetime import datetime,timezone
from backend import create_app, FIELDS, flags, now

def import_legacy(source,app,doctor_email=None):
    source=Path(source).resolve()
    if not source.is_file(): raise ValueError('Legacy database not found')
    if source==Path(app.config['DATABASE']).resolve(): raise ValueError('Source and target must be different databases')
    target=Path(app.config['DATABASE'])
    backup_dir=target.parent/'backups';backup_dir.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    old=sqlite3.connect(source.as_uri()+'?mode=ro',uri=True);old.row_factory=sqlite3.Row
    new=sqlite3.connect(target);new.row_factory=sqlite3.Row
    try:
        required={'patients','doctors','intakes'}
        tables={r[0] for r in old.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not required.issubset(tables): raise ValueError('Expected the original MOA patients/doctors/intakes schema')
        with sqlite3.connect(backup_dir/('legacy-source-'+stamp+'.db')) as backup: old.backup(backup)
        with sqlite3.connect(backup_dir/('before-import-'+stamp+'.db')) as backup: new.backup(backup)
        report={'accounts_imported':0,'cases_imported':0,'already_imported':0,'unmatched_cases_preserved_in_backup':0}
        key=str(source)
        def mapped(entity,id):
            r=new.execute('SELECT new_id FROM legacy_imports WHERE source=? AND entity=? AND legacy_id=?',(key,entity,id)).fetchone()
            return r['new_id'] if r else None
        def map_record(entity,id,newid): new.execute('INSERT INTO legacy_imports(source,entity,legacy_id,new_id) VALUES(?,?,?,?)',(key,entity,id,newid))
        with new:
            patients={};doctors=[]
            for table,role,alias_col in [('patients','patient','identifier'),('doctors','doctor','staff_id')]:
                for r in old.execute('SELECT * FROM '+table):
                    uid=mapped(table,r['id'])
                    if uid is None:
                        email=r['email'].strip().lower()
                        collision=new.execute('SELECT id FROM users WHERE email=? AND role=?',(email,role)).fetchone()
                        if collision: raise ValueError('An existing account email collides with a legacy account. Import into an empty initialized database or resolve the collision explicitly.')
                        uid=new.execute('INSERT INTO users(email,password,role,name) VALUES(?,?,?,?)',(email,r['password'],role,r['full_name'])).lastrowid
                        new.execute('INSERT INTO account_aliases(alias,role,user_id) VALUES(?,?,?)',(r[alias_col].strip().lower(),role,uid))
                        map_record(table,r['id'],uid);report['accounts_imported']+=1
                    if role=='patient':
                        patients[str(r['identifier'])]=uid
                        patients.setdefault(str(r['id']),uid)
                    else: doctors.append(uid)
            if doctor_email:
                doc=new.execute("SELECT id FROM users WHERE email=? AND role='doctor'",(doctor_email.lower().strip(),)).fetchone()
                if not doc: raise ValueError('Assigned doctor email was not found')
                doctor_id=doc['id']
            elif len(doctors)==1: doctor_id=doctors[0]
            else: raise ValueError('Legacy cases have no doctor assignment. Select --doctor-email explicitly when there is not exactly one legacy doctor.')
            for r in old.execute('SELECT * FROM intakes ORDER BY id'):
                if mapped('intakes',r['id']) is not None: report['already_imported']+=1;continue
                uid=patients.get(str(r['patient_id']))
                if uid is None:
                    report['unmatched_cases_preserved_in_backup']+=1;continue
                d={k:'' for k in FIELDS};d.update(name=r['patient_name'] or '',complaint=r['chief_complaint'] or '',duration=r['duration'] or '',severity=str(r['severity'] or 0),agni=r['agni_status'] or '',koshtha=r['koshtha_status'] or '',diet=r['dietary_fruits'] or '',observations=r['notes'] or '')
                completed=r['status']=='COMPLETED';f=flags(d)
                if completed:
                    for flag in f:flag['reviewed']=True
                status='Completed' if completed else ('Priority Review' if f else 'Awaiting Review')
                summary='Historical intake imported from original MOA records. Unspecified fields remain missing.\n'+'\n'.join(k+': '+v+' [source: legacy intake/'+k+']' for k,v in d.items() if v)
                cid=new.execute('INSERT INTO cases(patient_id,doctor_id,created,status,intake,flags,summary,assessment,recommendations,finalized) VALUES(?,?,?,?,?,?,?,?,?,?)',(uid,doctor_id,r['timestamp'] or now(),status,json.dumps(d),json.dumps(f),summary,r['doctor_diagnosis'] or '',r['doctor_prescription'] or '',r['timestamp'] if completed else None)).lastrowid
                map_record('intakes',r['id'],cid)
                new.execute('INSERT INTO audit(user_id,case_id,action,details,created) VALUES(?,?,?,?,?)',(None,cid,'legacy consultation imported',json.dumps({'legacy_id':r['id'],'legacy_status':r['status'],'assignment':'explicit import clinician; original system recorded no clinician ID','historical_notes':'copied verbatim; not newly generated or clinically verified'}),now()))
                report['cases_imported']+=1
        return report
    finally:old.close();new.close()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('--doctor-email');p.add_argument('--target',help='Optional target SQLite path');args=p.parse_args()
    config={'DATABASE':str(Path(args.target).resolve())} if args.target else None
    print(json.dumps(import_legacy(args.source,create_app(config),args.doctor_email),indent=2))
