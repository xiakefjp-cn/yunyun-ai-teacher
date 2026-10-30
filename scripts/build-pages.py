"""Build public browser demo from shared core; no secrets copied."""
import json
import shutil
from pathlib import Path

root=Path(__file__).resolve().parents[1];out=root/'site_out';out.mkdir(exist_ok=True)
html=(root/'web/index.html').read_text('utf-8')
start=html.index('async function api(');end=html.index('async function refresh()',start)
bridge=(root/'web/browser-bridge.js').read_text('utf-8')
html=html[:start]+bridge+'\n'+html[end:]
html=html.replace('<option value="true">真实模型 API（服务端配置）</option>','')
html=html.replace('正在恢复会话…','首次加载浏览器Python运行环境，需下载约10MB，请稍候…')
html=html.replace('循环结构备课工作台 · 生成 → 真实验证 → 教师审核 → 交付','公网演示 · 浏览器Python真实验证 · 离线备课模板 · <a style="color:white" href="https://github.com/xiakefjp-cn/yunyun-ai-teacher">源码与本机真实API版本</a>')
html=html.replace('工作区为','工作区为').replace('预览写入差异','预览浏览器工作区差异')
(out/'index.html').write_text(html,'utf-8')
shutil.copyfile(root/'web/browser-worker.js',out/'browser-worker.js')
(out/'app').mkdir(exist_ok=True)
for name in ('__init__.py','core.py','runner.py'):shutil.copyfile(root/'app'/name,out/'app'/name)
seeds=[dict(path=p.name,content=p.read_text('utf-8')) for p in (root/'demo_workspace').iterdir() if p.is_file() and p.suffix in ('.md','.json','.py')]
(out/'seeds.json').write_text(json.dumps(seeds,ensure_ascii=False),'utf-8')
(out/'.nojekyll').touch()
print('Built public demo in site_out; copied only explicit shared core and seed files.')
