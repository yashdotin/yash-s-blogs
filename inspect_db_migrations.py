import sqlite3
import os
from pathlib import Path
db = Path('db.sqlite3')
if not db.exists():
    print('No db.sqlite3 found in project root.')
else:
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    try:
        cur.execute('SELECT app, name FROM django_migrations ORDER BY id')
        rows = cur.fetchall()
        if not rows:
            print('No applied migrations recorded.')
        else:
            print('Applied migrations:')
            for r in rows:
                print(r)
    except Exception as e:
        print('Error querying django_migrations:', e)
    conn.close()
