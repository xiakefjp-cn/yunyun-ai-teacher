"""Real model checks for the selected subject; no credentials printed."""
import argparse
import base64
import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.core import Engine, seed_stats
from app.reference import import_reference
from app.subjects import general_stats

parser=argparse.ArgumentParser()
parser.add_argument('--subject',choices=['语文','数学','信息科技'],required=True)
parser.add_argument('--reference',type=Path)
args=parser.parse_args()
subject=args.subject
requests={
 '语文':('小学','汉语拼音 j q x','给一年级准备《jqx》第一课时40分钟。参考上传资料的卡牌热身、小院认读、四线三格书写、两拼三拼。第二课时的ü省点只预告，不作为本课必会。提供两个文字示范和三道适龄分层活动、答案与教师观察点。读音和书写不能由程序判分。原资料“8个声母”和列举数量不一致，请提醒老师核对，不照抄个人信息。'),
 '数学':('小学','乘法的初步认识','给二年级准备40分钟《乘法的初步认识》。用3盘苹果每盘4个引入，先画图再列式，区别几个几，不使用Python。两个示范和三种难度练习都给出答案、理由与独立可算的算式检查，题意和单位仍由老师检查。'),
 '信息科技':('初中','循环结构','给初二备40分钟循环结构课，刚学过条件语句。保留2个可运行Python示例与3道分层题，考虑缺交、死循环和边界错误，按contract返回完整备课包。')
}
stage,topic,request=requests[subject]
reference=''
if args.reference:
    reference=import_reference(args.reference.name,base64.b64encode(args.reference.read_bytes()).decode())['text']
root=Path('demo_evidence/multisubject')/subject
engine=Engine(root)
print(f'Calling configured model: {subject}; reference={bool(reference)}',flush=True)
rev=engine.generate(request,stage,seed_stats() if subject=='信息科技' else general_stats(),live=True,
                    subject=subject,topic=topic,minutes=40,reference=reference)['current']
(root/'result.json').write_text(json.dumps(rev,ensure_ascii=False,indent=2),'utf-8')
summary=dict(subject=subject,source=rev['source'],kind=rev['verification_kind'],verified=rev['verified'],
             items=len(rev['bundle']['items']),checks=sum(len(r['cases']) for r in rev['reports']),
             minutes=sum(s['minutes'] for s in rev['bundle']['items'][0]['segments']),attempts=len(rev['attempts']))
(root/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps(summary,ensure_ascii=True),flush=True)
if not rev['verified']: raise SystemExit(1)
