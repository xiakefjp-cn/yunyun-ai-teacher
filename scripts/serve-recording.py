import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.server import create_server
root=Path('demo_evidence/recording-workspace');root.mkdir(parents=True,exist_ok=True)
(root/'previous-lesson.md').write_text('# 上节课：条件语句\n本节课：循环结构。','utf-8')
port=int(sys.argv[1]) if len(sys.argv)>1 else 8770
server=create_server(root,port=port)
print(f'Recording workspace: http://127.0.0.1:{port}',flush=True)
server.serve_forever()
