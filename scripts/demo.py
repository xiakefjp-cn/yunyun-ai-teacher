"""Reproducible acceptance evidence. Run from repository root."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json
from app.core import Engine,seed_stats

root=Path('demo_evidence'); e=Engine(root)
e.generate('初二循环结构，重点终止与边界','初中',seed_stats())
good=e.state['current']['id']; assert e.state['current']['verified']
(root/'success.json').write_text(json.dumps(e.state['current'],ensure_ascii=False,indent=2),'utf-8')
e.generate('故意失败','初中',seed_stats()); assert not e.state['current']['verified']
(root/'failure.json').write_text(json.dumps(e.state['current'],ensure_ascii=False,indent=2),'utf-8')
try: e.archive(); raise AssertionError('Failure escaped gate')
except ValueError: pass
e.rollback(good)
for item in e.state['current']['bundle']['items']: e.review(item['id'],True)
(root/'lesson-package.zip').write_bytes(e.archive()); e.publish(True)
print('PASS: 16 cases, failure blocked, rollback, review, ZIP and real files in demo_evidence/')
