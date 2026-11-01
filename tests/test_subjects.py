import base64
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from app.core import Engine, validate_bundle
from app.reference import import_reference
from app.subjects import arithmetic_case, general_stats, material_template


class Subjects(unittest.TestCase):
    def test_language_review_and_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = Engine(directory)
            current = engine.generate('一年级jqx第一课时', '小学', general_stats(),
                                      subject='语文', topic='jqx')['current']
            self.assertEqual(current['verification_kind'], 'completeness')
            self.assertTrue(current['verified'])
            self.assertTrue(all(r['kind']=='completeness' for r in current['reports']))
            self.assertNotIn('code', current['bundle']['items'][1])
            with self.assertRaises(ValueError): engine.archive()
            for item in current['bundle']['items']: engine.review(item['id'], True)
            engine.edit(current['bundle']['items'][1]['id'], content='由老师示范并听辨。')
            self.assertEqual(engine.state['accepted'], [])
            for item in current['bundle']['items']: engine.review(item['id'], True)
            archive=zipfile.ZipFile(io.BytesIO(engine.archive()))
            self.assertIn('lesson.md', archive.namelist())
            self.assertFalse(any(name.endswith('.py') for name in archive.namelist()))
            self.assertIn('由老师示范', archive.read('example_1.md').decode())
            engine.publish(True)
            self.assertTrue((Path(directory)/'published/lesson.md').is_file())
            resumed=Engine(directory)
            self.assertEqual(resumed.state['current']['bundle']['subject'], '语文')
            with self.assertRaises(ValueError): engine.edit('basic', answer='')

    def test_math_failure_gate_and_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            engine=Engine(directory)
            good=engine.generate('乘法', '小学', general_stats(), subject='数学')['current']
            self.assertTrue(good['verified'])
            for item in good['bundle']['items']: engine.review(item['id'],True)
            bad=engine.edit('basic',answer='4个3是13',calculations=[dict(expression='4*3',expected='13')])['current']
            self.assertFalse(bad['verified'])
            self.assertEqual(engine.state['accepted'],[])
            with self.assertRaises(ValueError): engine.review('basic',True)
            with self.assertRaises(ValueError): engine.archive()
            engine.rollback(good['id'])
            self.assertTrue(engine.state['current']['verified'])

    def test_bounded_exact_arithmetic(self):
        self.assertTrue(arithmetic_case(dict(expression='1/3+1/6',expected='1/2'))['passed'])
        for expression in ['__import__("os")', '2**100000000', '1/0', 'x+1', '9'*100, '[1]']:
            self.assertFalse(arithmetic_case(dict(expression=expression,expected='1'))['passed'])

    def test_templates_and_duration(self):
        for subject in ('语文','数学'):
            for stage in ('小学','初中'):
                for minutes in (20,40,80,120):
                    bundle=material_template(subject,stage,general_stats(),'漫画老师' if subject=='语文' else '',minutes)
                    validate_bundle(bundle,subject,minutes)
                    self.assertEqual(sum(s['minutes'] for s in bundle['items'][0]['segments']),minutes)
        with self.assertRaises(ValueError): validate_bundle(bundle,'信息科技',120)

    def test_word_import_and_privacy_line(self):
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as z:
            z.writestr('word/document.xml', '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>执教人：测试姓名</w:t></w:r></w:p><w:p><w:r><w:t>学习jqx</w:t></w:r></w:p></w:body></w:document>')
        result=import_reference('lesson.docx',base64.b64encode(stream.getvalue()).decode())
        self.assertIn('学习jqx',result['text'])
        self.assertNotIn('测试姓名',result['text'])
        self.assertIn('图片',result['note'])
        with self.assertRaises(ValueError): import_reference('lesson.docx','!!!')


if __name__=='__main__': unittest.main()
