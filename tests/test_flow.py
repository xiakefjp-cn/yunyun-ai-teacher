import io
import json
import tempfile
import threading
import unittest
import urllib.request
import zipfile
from pathlib import Path
from app.core import Engine, seed_stats, template, validate_bundle
from app.runner import run_case
from app.server import create_server

class Flow(unittest.TestCase):
    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            e=Engine(d); e.generate('循环结构','初中',seed_stats()); self.assertTrue(e.state['current']['verified'])
            good=e.state['current']['id']
            with self.assertRaises(ValueError): e.archive()
            for x in e.state['current']['bundle']['items']: e.review(x['id'],True)
            archive=e.archive(); self.assertIn('manifest.json',zipfile.ZipFile(io.BytesIO(archive)).namelist())
            preview=e.publish(); self.assertTrue(preview['changes']); self.assertFalse((Path(d)/'published/lesson.md').exists())
            e.publish(True); self.assertTrue((Path(d)/'published/lesson.md').exists())
            e.generate('故意失败','初中',seed_stats()); self.assertFalse(e.state['current']['verified'])
            self.assertTrue(any(c['error'] for r in e.state['current']['reports'] for c in r['cases']))
            with self.assertRaises(ValueError): e.review('lesson',True)
            with self.assertRaises(ValueError): e.archive()
            e.rollback(good); self.assertEqual(e.state['accepted'],[])
            resumed=Engine(d); self.assertEqual(resumed.state['current']['id'],good)
            self.assertEqual(len(resumed.state['messages']),4)
    def test_guard(self):
        for code in ['import os','print(open("x"))','print((1).__class__)','print("a" * 1000000)']:
            self.assertFalse(run_case(code,{'stdin':'','expected':''})['passed'])
        self.assertIn('超限',run_case('while True:\n    pass',{'stdin':'','expected':''})['error'])
    def test_adaptation(self):
        a=template('初中',seed_stats()); b=template('大学',dict(total=40,missing=0,infinite_loop=0,boundary=0))
        self.assertNotEqual(a['items'][0]['segments'],b['items'][0]['segments'])
        for bundle in (a,b): validate_bundle(bundle)
    def test_http(self):
        with tempfile.TemporaryDirectory() as d:
            s=create_server(d,port=0); threading.Thread(target=s.serve_forever,daemon=True).start()
            base=f'http://127.0.0.1:{s.server_port}'
            try:
                landing=urllib.request.urlopen(base).read().decode()
                self.assertIn('体验产品能力',landing)
                html=urllib.request.urlopen(base+'/studio.html').read().decode(); import re
                token=re.search("const TOKEN='([^']+)'",html)[1]
                req=urllib.request.Request(base+'/api/generate',data=json.dumps(dict(request='循环',stage='初中',stats=seed_stats())).encode(),headers={'X-Yunyun-Token':token,'Content-Type':'application/json'})
                state=json.load(urllib.request.urlopen(req)); self.assertTrue(state['current']['verified'])
            finally: s.shutdown(); s.server_close()

if __name__=='__main__': unittest.main()
