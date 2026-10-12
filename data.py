"""Print schema and row counts without printing patient records."""
import sqlite3
from backend import create_app
app=create_app()
with sqlite3.connect(app.config['DATABASE']) as c:
    for name,sql in c.execute("SELECT name,sql FROM sqlite_master WHERE type='table'"):
        print(sql)
        print('Rows:',c.execute('SELECT count(*) FROM "'+name.replace('"','""')+'"').fetchone()[0])
