"""Exercise the actual container over HTTP; never print credentials."""
import argparse
import io
import json
import re
import urllib.request
import zipfile
from pathlib import Path

parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8765');parser.add_argument('--live',action='store_true');parser.add_argument('--resume',action='store_true');args=parser.parse_args()
html=urllib.request.urlopen(args.url+'/studio.html',timeout=10).read().decode()
token=re.search("const TOKEN='([^']+)'",html)[1]
def call(route,data=None):
    request=urllib.request.Request(args.url+'/api/'+route,data=json.dumps(data).encode() if data is not None else None,headers={'X-Yunyun-Token':token,'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=300) as response:
        return response.read() if route=='download' else json.load(response)
evidence=Path('deliverables/docker-acceptance.json');evidence.parent.mkdir(exist_ok=True)
if args.resume:
    expected=json.loads(evidence.read_text('utf-8'));current=call('state')['state']
    assert current['current']['id']==expected['revision'] and len(current['accepted'])==6
    assert Path('teacher_workspace/published/lesson.md').is_file()
    expected['restart_persistence']=True;evidence.write_text(json.dumps(expected,indent=2),'utf-8')
    print('PASS: container restart restored revision, 6 accepted items and host files')
else:
    print('Generating and running Python in Docker...',flush=True)
    state=call('generate',dict(request='给初二备一节40分钟的循环结构课，刚学完条件语句；40人中5人未提交、3人写了死循环、6人有边界错误。按协议输出教案、2个示例、3道分层题及参考答案评分点。',stage='初中',stats=dict(total=40,missing=5,infinite_loop=3,boundary=6),live=args.live))
    good=state['current'];assert good['verified'];revision=good['id']
    code=next(x for x in good['bundle']['items'] if x['kind']=='example')
    bad=call('edit',dict(id=code['id'],code='while True:\n    pass\n'))
    assert not bad['current']['verified']
    try: call('download',{});raise AssertionError('Failure escaped export gate')
    except urllib.error.HTTPError as exc: assert exc.code==400
    call('rollback',dict(id=revision))
    for item in good['bundle']['items']:call('review',dict(id=item['id'],accept=True))
    archive=call('download',{});assert 'lesson.md' in zipfile.ZipFile(io.BytesIO(archive)).namelist()
    preview=call('publish',{});assert 'directory' in preview
    published=call('publish',dict(confirm=True));assert published['written']>0
    assert Path('teacher_workspace/published/lesson.md').exists()
    result=dict(source=good['source'],verified=True,cases=sum(len(r['cases']) for r in good['reports']),failure_gate=True,host_files=True,zip_bytes=len(archive),revision=revision,restart_persistence=False)
    evidence.write_text(json.dumps(result,indent=2),'utf-8');print(json.dumps(result),flush=True)
