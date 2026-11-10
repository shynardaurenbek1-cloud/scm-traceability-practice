import sqlite3
import pytest

from app import Traceability


@pytest.fixture
def t(tmp_path):return Traceability(tmp_path/'db.sqlite3')
@pytest.fixture
def sample(tmp_path):
    f=tmp_path/'code.py';f.write_text('print(1)');return f

def test_register(t,sample):assert len(t.register('CI-1',sample,'1.0.0'))==64
def test_version(t,sample):
    t.register('CI-1',sample,'1.0.0');t.request('CR-1','edit');t.decide('CR-1',True)
    t.apply('CR-1','CI-1','1.1.0','abc','test_code')
    assert t.conn.execute('SELECT version FROM items').fetchone()[0]=='1.1.0'
def test_approve(t):t.request('CR-1','edit');t.decide('CR-1',True)
def test_reject(t,sample):
    t.register('CI-1',sample,'1.0.0');t.request('CR-1','edit');t.decide('CR-1',False)
    with pytest.raises(PermissionError):t.apply('CR-1','CI-1','1.1.0','abc','test_code')
def test_unapproved(t,sample):
    t.register('CI-1',sample,'1.0.0');t.request('CR-1','edit')
    with pytest.raises(PermissionError):t.apply('CR-1','CI-1','1.1.0','abc','test_code')
def test_baseline(t,sample):
    t.register('CI-1',sample,'1.0.0');assert t.baseline('BL-1')[0]['id']=='CI-1'
def test_immutable(t):
    t.baseline('BL-1')
    with pytest.raises(sqlite3.IntegrityError):
        t.baseline('BL-1')
def test_audit(t,sample):
    t.register('CI-1',sample,'1.0.0');t.baseline('BL-1');assert t.audit('BL-1')[0]['valid']
def test_audit_detect(t,sample):
    t.register('CI-1',sample,'1.0.0');t.baseline('BL-1');sample.write_text('modified')
    assert not t.audit('BL-1')[0]['valid']
def test_link(t,sample):
    t.register('CI-1',sample,'1.0.0');t.request('CR-1','edit');t.decide('CR-1',True)
    t.apply('CR-1','CI-1','1.1.0','abc','test_code');t.baseline('BL-1');t.link('CR-1','BL-1')
    assert t.report()['traceability'][0]['baseline_id']=='BL-1'
def test_unapproved_link(t):
    t.request('CR-1','edit');t.baseline('BL-1')
    with pytest.raises(ValueError):t.link('CR-1','BL-1')
def test_report(t):assert len(t.report()['processes'])==5
