"""Private SQLite state; transactions and an append-only event log."""
import json
from pathlib import Path
import sqlite3
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]

def now():
    return datetime.now(timezone.utc).isoformat()

def private_path(path):
    path = Path(path).expanduser().resolve()
    if path == ROOT or ROOT in path.parents:
        raise ValueError('Workspace must be outside the repository')
    return path

class Workspace:
    def __init__(self, path, create=False, city=None, minimum_bedrooms=2):
        self.path = private_path(path)
        if create:
            if self.path.exists() and any(self.path.iterdir()): raise ValueError('Workspace directory must be empty; no overwrite')
            if minimum_bedrooms < 0: raise ValueError('Bedrooms must be nonnegative')
            self.path.mkdir(parents=True, exist_ok=True)
            self.path.chmod(0o700)
        elif not (self.path/'state.db').is_file():
            raise ValueError('Workspace not initialized; run init first')
        self.db = sqlite3.connect(str(self.path/'state.db'),timeout=10)
        (self.path/'state.db').chmod(0o600)
        self.db.execute('CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY, body TEXT NOT NULL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, at TEXT, kind TEXT, body TEXT)')
        if create:
            data={'schema_version':1,'preferences':{'city':city,'minimum_bedrooms':minimum_bedrooms,'timezone':'UTC','holidays':[],'followup_hours':48},'sources':[],'properties':[],'conversations':[],'costs':[]}
            self.db.execute('INSERT INTO state VALUES (1,?)',(json.dumps(data),))
            self.db.commit()
    def read(self):
        return json.loads(self.db.execute('SELECT body FROM state WHERE id=1').fetchone()[0])
    def change(self, kind, function):
        try:
            self.db.execute('BEGIN IMMEDIATE')
            data=self.read(); result=function(data)
            self.db.execute('UPDATE state SET body=? WHERE id=1',(json.dumps(data,ensure_ascii=False),))
            self.db.execute('INSERT INTO events(at,kind,body) VALUES (?,?,?)',(now(),kind,json.dumps(result,ensure_ascii=False)))
            self.db.commit(); return result
        except Exception:
            self.db.rollback(); raise
    def close(self): self.db.close()
