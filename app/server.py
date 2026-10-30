import argparse
import json
import secrets
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
from .core import Engine

WEB=Path(__file__).resolve().parent.parent/'web'/'studio.html'
LANDING=WEB.with_name('index.html')

def create_server(root, host='127.0.0.1', port=8765, mode='web'):
    engine=Engine(root,mode); token=secrets.token_urlsafe(32)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def send(self,data,status=200,ctype='application/json; charset=utf-8'):
            body=data if isinstance(data,bytes) else json.dumps(data,ensure_ascii=False).encode()
            self.send_response(status); self.send_header('Content-Type',ctype); self.send_header('Content-Length',str(len(body)))
            self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(body)
        def do_GET(self):
            path=urlparse(self.path).path
            if path in ('/', '/index.html'): return self.send(LANDING.read_bytes(),ctype='text/html; charset=utf-8')
            if path=='/studio.html': return self.send(WEB.read_text('utf-8').replace('__TOKEN__',token).encode(),ctype='text/html; charset=utf-8')
            if self.headers.get('X-Yunyun-Token')!=token: return self.send({'error':'访问令牌无效'},403)
            if path=='/api/state': return self.send(dict(state=engine.state,files=engine.files(),mode=mode,workspace=str(engine.root)))
            return self.send({'error':'不存在'},404)
        def do_POST(self):
            if self.headers.get('X-Yunyun-Token')!=token: return self.send({'error':'访问令牌无效'},403)
            try:
                size=int(self.headers.get('Content-Length','0'))
                if size>200000: raise ValueError('请求过大')
                data=json.loads(self.rfile.read(size)); path=urlparse(self.path).path
                if path=='/api/generate': result=engine.generate(**data)
                elif path=='/api/edit': result=engine.edit(**data)
                elif path=='/api/review': result=engine.review(**data)
                elif path=='/api/rollback': result=engine.rollback(**data)
                elif path=='/api/publish': result=engine.publish(**data)
                elif path=='/api/download': return self.send(engine.archive(),ctype='application/zip')
                else: return self.send({'error':'不存在'},404)
                self.send(result)
            except Exception as e: self.send({'error':str(e)},400)
    return ThreadingHTTPServer((host,port),Handler)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--workspace',default='demo_workspace'); parser.add_argument('--host',default='127.0.0.1'); parser.add_argument('--port',type=int,default=8765)
    args=parser.parse_args(); server=create_server(args.workspace,args.host,args.port)
    print(f'耘耘AI助教 http://{args.host}:{server.server_port}',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: server.server_close()

if __name__=='__main__': main()
