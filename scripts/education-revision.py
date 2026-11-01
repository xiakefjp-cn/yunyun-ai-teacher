"""Revisit an actual model draft; retain a reproducible educational review."""
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core import Engine, seed_stats
from app.runner import run_case

original = json.loads(Path('demo_evidence/live/first-result.json').read_text('utf-8'))
engine = Engine(Path('demo_evidence/education-revision'))
engine.state['current'] = copy.deepcopy(original)
engine.state['revisions'] = [copy.deepcopy(original)]
engine.save()
request = ('审核上一版真实模型教案：分层练习环节只说“基础必做，进阶先手算后编码；挑战选做并解释边界”，'
           '无法指导教师现场检查；“让学生写变量追踪表再运行”也缺少具体问题和预期答案。'
           '请修订这两个环节：activity内明确教师提问、学生可观察产物、预期答案、检查标准与未达标后的补救动作。'
           '变量追踪必须给n=3时i与累计值的具体序列；说明n=0的预期。'
           '保留原有2个示例和3道分层题的代码与测试，不改变40分钟总时长。返回完整协议JSON。')
print('Reviewing a real model draft and requesting concrete classroom actions...', flush=True)
current = engine.generate(request, '初中', seed_stats(), live=True)['current']
assert current['verified'], 'Revised code did not pass'
before = original['bundle']['items'][0]
after = current['bundle']['items'][0]
assert before['segments'] != after['segments'], 'Lesson was not revised'
assert sum(s['minutes'] for s in after['segments']) == 40
preserved = all(a.get('code') == b.get('code') and a.get('tests') == b.get('tests')
                for a, b in zip(original['bundle']['items'][1:], current['bundle']['items'][1:]))
result = dict(request=request, before=before, after=after, verified=current['verified'],
              code_and_tests_preserved=preserved,
              cases=sum(len(r['cases']) for r in current['reports']),
              model_calls=[{k: a.get(k) for k in ('model','request_id','usage')} for a in current['attempts']],
              scope='Synthetic class statistics; educational specificity review, not a naturally occurring code failure.')
target = Path('docs/evidence/education-revision.json')
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(result, ensure_ascii=False, indent=2), 'utf-8')
print(json.dumps(dict(verified=True, code_and_tests_preserved=preserved, cases=result['cases'], evidence=str(target))))
repair = ('上一轮教案的人工核对发现具体错误，代码测试通过也没有发现它：'
          '基础题是输出2到n的偶数，所以n=0、1均无输出，n=2只有2，不能说n=1单值、n=2双值。'
          '进阶while累加中i初始化为1，每轮末i+=1，故n=0、1、5退出后的(s,i)应为(0,1)、(1,2)、(15,6)，'
          '你写的(0,0)、(1,1)、(15,5)混淆了进入本轮与退出时状态。'
          '请纠正lesson内全部相关叙述，明确表格记录的是进入循环时还是更新后、退出时。'
          '保留全部代码和测试以及40分钟。仅返回完整协议JSON。')
fixed = engine.generate(repair, '初中', seed_stats(), live=True)['current']
assert fixed['verified']
result['repair_request'] = repair
result['fixed'] = fixed['bundle']['items'][0]
result['fixed_verified'] = fixed['verified']
result['fixed_cases'] = sum(len(r['cases']) for r in fixed['reports'])
result['repair_model_calls'] = [{k:a.get(k) for k in ('model','request_id','usage')} for a in fixed['attempts']]
advanced = next(x for x in fixed['bundle']['items'] if x['id'] == 'advanced')
result['independent_exit_state_checks'] = [run_case(advanced['code'] + '\nprint(s, i)\n',
    dict(stdin=str(n)+'\n', expected=expected)) for n, expected in
    [(0, '0\n0 1'), (1, '1\n1 2'), (5, '15\n15 6')]]
assert all(c['passed'] for c in result['independent_exit_state_checks'])
target.write_text(json.dumps(result, ensure_ascii=False, indent=2), 'utf-8')
print('Repair evidence saved; human review of lesson statements is still required.', flush=True)
