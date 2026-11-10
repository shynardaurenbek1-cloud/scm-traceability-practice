import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class Traceability:
    def __init__(self,db):
        self.conn=sqlite3.connect(db)
        self.conn.row_factory=sqlite3.Row
        self.conn.executescript("""CREATE TABLE IF NOT EXISTS items(id TEXT PRIMARY KEY,path TEXT NOT NULL,version TEXT NOT NULL,sha256 TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS requests(id TEXT PRIMARY KEY,description TEXT,decision TEXT NOT NULL DEFAULT 'pending',commit_hash TEXT,test_name TEXT);
        CREATE TABLE IF NOT EXISTS baselines(id TEXT PRIMARY KEY,created_at TEXT NOT NULL,items TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS links(request_id TEXT,baseline_id TEXT,PRIMARY KEY(request_id,baseline_id));""")
        self.conn.commit()

    def register(self,id,path,version):
        data=Path(path).read_bytes();sha=hashlib.sha256(data).hexdigest()
        self.conn.execute('INSERT INTO items VALUES(?,?,?,?)',(id,str(path),version,sha));self.conn.commit();return sha

    def request(self,id,description):
        self.conn.execute('INSERT INTO requests(id,description) VALUES(?,?)',(id,description));self.conn.commit()

    def decide(self,id,approved):
        cur=self.conn.execute('UPDATE requests SET decision=? WHERE id=? AND decision=?',('approved' if approved else 'rejected',id,'pending'))
        self.conn.commit()
        if not cur.rowcount:raise ValueError('Сұрау жоқ/шешім бар')

    def apply(self,request_id,item_id,version,commit_hash,test_name):
        row=self.conn.execute('SELECT decision FROM requests WHERE id=?',(request_id,)).fetchone()
        if not row or row[0]!='approved':raise PermissionError('Алдымен өзгерісті мақұлдау қажет')
        item=self.conn.execute('SELECT path FROM items WHERE id=?',(item_id,)).fetchone()
        if item is None:raise KeyError('CI жоқ')
        sha=hashlib.sha256(Path(item[0]).read_bytes()).hexdigest()
        with self.conn:
            self.conn.execute('UPDATE items SET version=?,sha256=? WHERE id=?',(version,sha,item_id))
            self.conn.execute('UPDATE requests SET commit_hash=?,test_name=? WHERE id=?',(commit_hash,test_name,request_id))

    def baseline(self,id):
        items=[dict(row) for row in self.conn.execute('SELECT * FROM items ORDER BY id')]
        self.conn.execute('INSERT INTO baselines VALUES(?,?,?)',(id,datetime.now(timezone.utc).isoformat(),json.dumps(items)))
        self.conn.commit();return items

    def link(self,request_id,baseline_id):
        req=self.conn.execute('SELECT decision,commit_hash,test_name FROM requests WHERE id=?',(request_id,)).fetchone()
        base=self.conn.execute('SELECT 1 FROM baselines WHERE id=?',(baseline_id,)).fetchone()
        if not req or req[0]!='approved' or not req[1] or not req[2] or not base:
            raise ValueError('Толық дәлел жоқ')
        self.conn.execute('INSERT INTO links VALUES(?,?)',(request_id,baseline_id));self.conn.commit()

    def audit(self,id):
        row=self.conn.execute('SELECT items FROM baselines WHERE id=?',(id,)).fetchone()
        if row is None:raise KeyError('Baseline жоқ')
        findings=[]
        for item in json.loads(row[0]):
            path=Path(item['path'])
            valid=path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256']
            findings.append({'id':item['id'],'valid':valid})
        return findings

    def report(self):
        rows=self.conn.execute('SELECT r.id,r.decision,r.commit_hash,r.test_name,l.baseline_id FROM requests r LEFT JOIN links l ON r.id=l.request_id').fetchall()
        return {'traceability':[dict(x) for x in rows], 'processes':[
            {'process':'Identification','rule':'SCMP §1','function':'register','test':'test_register','status':'implemented'},
            {'process':'Change control','rule':'SCMP §2','function':'decide/apply','test':'test_unapproved','status':'implemented'},
            {'process':'Status accounting','rule':'SCMP §3','function':'report','test':'test_report','status':'implemented'},
            {'process':'Audit','rule':'SCMP §4','function':'audit','test':'test_audit','status':'partial'},
            {'process':'Release','rule':'SCMP §5','function':'baseline/link','test':'test_link','status':'partial'}]}


def main():
    p=argparse.ArgumentParser();p.add_argument('--db',default='trace.sqlite3');p.add_argument('--out',default='report.json');a=p.parse_args()
    t=Traceability(a.db);Path(a.out).write_text(json.dumps(t.report(),ensure_ascii=False,indent=2),encoding='utf-8');print(a.out)


if __name__=='__main__':main()
