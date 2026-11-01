import copy
import io
import json
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from app.core import Engine, seed_stats, template
from app.questions import builtin_questions, empty_contract, normalize_model_text


class Response:
    def __init__(self,bundle): self.bundle=bundle
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self):return json.dumps(dict(choices=[dict(message=dict(content=json.dumps(self.bundle)))],model='test',id='test')).encode()


class Questions(unittest.TestCase):
    def test_normalize_only_text_format_not_answers(self):
        b={'items':[{'id':'basic','answer':['答案甲','答案乙'],'code':['不能自动转换代码']}]}
        normalize_model_text(b)
        self.assertEqual(b['items'][0]['answer'],'答案甲\n答案乙')
        self.assertIsInstance(b['items'][0]['code'],list)
        self.assertIn('未修改内容',b['format_adjustments'][0])

    def test_model_contract_has_no_worked_answers(self):
        sample=template('初中',seed_stats())
        blank=empty_contract(sample)
        self.assertNotIn('输出1至n的偶数',json.dumps(blank,ensure_ascii=False))
        self.assertEqual(blank['items'][3]['code'],'')
        with tempfile.TemporaryDirectory() as directory:
            e=Engine(directory);payloads=[]
            def respond(request,**kwargs):
                payloads.append(json.loads(request.data));return Response({'items':{'bad':'wrong shape'}} if len(payloads)==1 else sample)
            with (patch('app.core.read_local_env',return_value=dict(YUNYUN_API_KEY='test',YUNYUN_API_BASE='https://example.invalid',YUNYUN_MODEL='test')),
                 patch('app.core.urllib.request.urlopen',side_effect=respond)):
                rev=e.generate('设计校园排队新题','初中',seed_stats(),live=True,question_mode='model')['current']
            prompt=json.loads(payloads[0]['messages'][1]['content'])
            self.assertEqual(prompt['selected_questions'],[])
            self.assertEqual(prompt['contract']['items'][3]['code'],'')
            self.assertEqual(len(rev['attempts']),2)
            self.assertEqual(rev['bundle']['question_sources']['basic']['kind'],'model_generated')
            self.assertTrue(rev['bundle']['question_sources']['basic']['exact_bank_match'])

    def test_bank_preserved_and_edited_provenance_exported(self):
        with tempfile.TemporaryDirectory() as directory:
            e=Engine(directory)
            rev=e.generate('循环结构','初中',seed_stats(),question_mode='bank')['current']
            item=rev['bundle']['items'][3]
            record=next(r for r in builtin_questions() if r['id']==rev['bundle']['question_sources'][item['id']]['bank_id'])
            self.assertEqual(item['prompt'],record['item']['prompt'])
            self.assertEqual(item['code'],record['item']['code'])
            e.edit(item['id'],code=item['code']+'\n')
            self.assertEqual(e.state['current']['bundle']['question_sources'][item['id']]['kind'],'teacher_edited')
            for x in e.state['current']['bundle']['items']:e.review(x['id'],True)
            self.assertTrue(all(s['teacher_reviewed'] for s in e.state['current']['bundle']['question_sources'].values()))
            archive=zipfile.ZipFile(io.BytesIO(e.archive()))
            self.assertIn('question-sources.json',archive.namelist())
            exported=archive.read('basic.md').decode()
            self.assertIn('解题思路',exported);self.assertIn('```python',exported)
            e.edit('basic',solution='先手算，再逐行解释代码。',estimated_minutes=7,participation='选做')
            self.assertEqual(e.state['current']['bundle']['items'][3]['estimated_minutes'],7)
            self.assertEqual(e.state['accepted'],[])
            self.assertTrue(all(not s['teacher_reviewed'] for s in e.state['current']['bundle']['question_sources'].values()))

    def test_mixed_protects_bank_and_fills_other_levels(self):
        chosen=next(r for r in builtin_questions() if r['subject']=='信息科技' and r['level']=='基础')
        sample=template('初中',seed_stats())
        sample['items'][3]['prompt']='模型试图改写题库题'
        with tempfile.TemporaryDirectory() as directory:
            e=Engine(directory)
            with (patch('app.core.read_local_env',return_value=dict(YUNYUN_API_KEY='test',YUNYUN_API_BASE='https://example.invalid')),
                 patch('app.core.urllib.request.urlopen',return_value=Response(sample))):
                rev=e.generate('循环结构','初中',seed_stats(),live=True,question_mode='mixed',bank_ids=[chosen['id']])['current']
            self.assertEqual(rev['bundle']['items'][3]['prompt'],chosen['item']['prompt'])
            self.assertEqual(rev['bundle']['question_sources']['basic']['kind'],'question_bank')
            self.assertEqual(rev['bundle']['question_sources']['advanced']['kind'],'model_generated')

    def test_import_selection_and_persistence(self):
        record=copy.deepcopy(builtin_questions()[0]);record['id']='custom-test'
        with tempfile.TemporaryDirectory() as directory:
            e=Engine(directory);self.assertEqual(e.import_questions([record])['imported'],1)
            with self.assertRaises(ValueError):e.import_questions([record])
            resumed=Engine(directory)
            self.assertIn('custom-test',[r['id'] for r in resumed.questions('信息科技','初中','循环结构')['questions']])
            with self.assertRaises(ValueError):resumed.generate('新课题','初中',seed_stats(),topic='完全没有收录的课题',question_mode='bank')
            with self.assertRaises(ValueError):resumed.generate('循环','初中',seed_stats(),question_mode='model',live=False)
            with self.assertRaises(ValueError):resumed.generate('循环','初中',seed_stats(),question_mode='bank',bank_ids=[])


if __name__=='__main__':unittest.main()
