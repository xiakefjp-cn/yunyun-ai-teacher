"""Paid real-model acceptance; prints no credentials."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.core import Engine,seed_stats
from app.subjects import general_stats
from app.questions import builtin_questions

p=argparse.ArgumentParser();p.add_argument('--mode',choices=['model','mixed'],default='model');p.add_argument('--subject',choices=['信息科技','语文','数学'],default='信息科技');args=p.parse_args()
subject=args.subject
stage='初中' if subject=='信息科技' else '小学'
topic={'信息科技':'循环结构','语文':'汉语拼音 j q x','数学':'乘法的初步认识'}[subject]
request={
 '信息科技':'为初二准备40分钟循环结构课，刚学条件语句。请自行设计校园图书馆或晨跑情境的两个示例和三道分层题，给出完整解题思路、参考代码和边界测试。不要沿用输出偶数、1到n求和、累加首次达到目标这三道示例题。示例与进阶题不要只是同题照抄；进阶可补全或改错，挑战选做。每题估计用时；明确课堂提问、学生任务和检查标准。只用运行器允许的语法，不用乘法。',
 '语文':'一年级jqx第一课时40分钟。请自行设计寻找字母、两拼和三拼卡牌练习，不要沿用空泛模板。两个示范、三道分层活动都给出参考回应和教师观察点，挑战也不能使用下一课时的ü省点规则。没有语音和图片识别，发音、口型和书写由老师判断。',
 '数学':'二年级乘法初步认识40分钟，自行设计教室摆椅子、每组同样多的情境，给两个示范和三种难度练习。每题有答案、解题步骤和教师检查点，计算核对只列纯整数四则算式，不用Python代码。不要直接复制原来的苹果、小棒或铅笔题。'
}[subject]
bank_ids=None
if args.mode=='mixed':
 bank_ids=[next(r['id'] for r in builtin_questions() if r['subject']==subject and r['level']=='基础' and stage in r['stages'] and r['topic']==topic)]
 request+=' 本轮基础题明确使用选中的题库原题，其余两种难度由模型自行设计。'
root=Path('demo_evidence/question-modes')/(subject+'-'+args.mode)
e=Engine(root/"workspace")
print('Calling configured model with an empty output contract...',flush=True)
r=e.generate(request,stage,seed_stats() if subject=='信息科技' else general_stats(),live=True,subject=subject,topic=topic,question_mode=args.mode,bank_ids=bank_ids)['current']
(root/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf-8')
summary=dict(subject=subject,mode=args.mode,verified=r['verified'],attempts=len(r['attempts']),
 checks=sum(len(x['cases']) for x in r['reports']),teacher_approved=False,
 questions=[dict(id=x['id'],title=x['title'],solution_present=bool(x.get('solution') or x.get('answer')),
  estimated_minutes=x['estimated_minutes'],origin=r['bundle']['question_sources'][x['id']]) for x in r['bundle']['items'] if x['kind']=='exercise'])
(root/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps(dict(subject=subject,mode=args.mode,verified=r['verified'],checks=summary['checks'],attempts=summary['attempts']),ensure_ascii=True),flush=True)
if not r['verified']:raise SystemExit(1)
