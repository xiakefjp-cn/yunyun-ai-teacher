"""Run locally; key input is hidden and never printed."""
import getpass
import json
from pathlib import Path

base=input('API Base URL（回车使用阿里云北京）: ').strip() or 'https://dashscope.aliyuncs.com/compatible-mode/v1'
model=input('模型名称（回车使用 qwen-plus）: ').strip() or 'qwen-plus'
key=getpass.getpass('百炼 API Key（输入不可见）: ').strip()
if not key or not base.startswith('https://'): raise SystemExit('密钥不能为空，接口必须HTTPS')
path=Path(__file__).resolve().parent/'.api-config.json'
path.write_text(json.dumps(dict(key=key,base=base,model=model)),'utf-8')
print('已保存到本机 .api-config.json（Git忽略）。该文件含明文密钥，请勿分享。可直接在工作台选择真实模型API。')
