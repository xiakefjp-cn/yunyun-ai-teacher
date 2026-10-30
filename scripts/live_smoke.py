"""Live API acceptance; prints only non-secret result metrics."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.core import Engine, seed_stats

root=Path('demo_evidence/live')
engine=Engine(root)
request='给初二备一节40分钟的循环结构课，刚学完条件语句；40人中5人未提交、3人写了死循环、6人有边界错误。按协议输出教案、2个示例、3道分层题及参考答案评分点。'
if '--followup' in sys.argv:
    request='继续修改上一版：挑战题改成校园读书打卡累计页数场景，仍只用循环、条件和累加；保留基础与进阶题。教案增加先手算再运行的变量追踪活动，总时间仍为40分钟。'
print('Calling qwen-plus; waiting for generation and real code verification...',flush=True)
state=engine.generate(request,'初中',seed_stats(),live=True)
rev=state['current']
path=root/('followup-result.json' if '--followup' in sys.argv else 'first-result.json')
path.write_text(json.dumps(rev,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps(dict(source=rev['source'],verified=rev['verified'],revision=rev['id'],items=len(rev['bundle']['items']),cases=sum(len(r['cases']) for r in rev['reports']),passed=sum(c['passed'] for r in rev['reports'] for c in r['cases']),attempts=len(rev['attempts']),usage=[a.get('usage') for a in rev['attempts']],evidence=str(path)),ensure_ascii=True),flush=True)
if not rev['verified']: raise SystemExit(1)
