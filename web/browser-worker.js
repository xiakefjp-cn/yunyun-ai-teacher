/* Browser host for the same Python Engine. No API keys or backend required. */
importScripts('https://cdn.jsdelivr.net/pyodide/v0.28.3/full/pyodide.js');
const boot=(async()=>{
 const py=await loadPyodide({indexURL:'https://cdn.jsdelivr.net/pyodide/v0.28.3/full/'});
 py.FS.mkdirTree('/app');py.FS.mkdirTree('/workspace');
 for(const name of ['__init__.py','runner.py','core.py']){
  const r=await fetch('app/'+name);if(!r.ok)throw Error('无法加载共享核心');
  py.FS.writeFile('/app/'+name,await r.text());
 }
 const seeds=await(await fetch('seeds.json')).json();
 for(const f of seeds)py.FS.writeFile('/workspace/'+f.path,f.content);
 await py.runPythonAsync(`
import sys, json, io, base64
sys.path.insert(0, '/')
from app import runner

def browser_case(code, case):
    output=io.StringIO()
    try:
        runner.check(code)
        lines=iter(case['stdin'].splitlines())
        def read_input():
            try: return next(lines)
            except StopIteration: raise EOFError('没有更多输入')
        def write_output(*args, sep=' ', end='\\n'):
            text=sep.join(str(x) for x in args)+end
            if output.tell()+len(text)>12000: raise RuntimeError('输出超限')
            output.write(text)
        budget=[0]
        def trace(frame,event,arg):
            budget[0]+=1
            if budget[0]>30000: raise RuntimeError('执行步数超限：疑似死循环')
            return trace
        safe={k:__builtins__.__dict__[k] for k in ['int','str','range','len','abs','min','max','sum']}
        safe.update(print=write_output,input=read_input)
        sys.settrace(trace)
        try: exec(compile(code,'<lesson>','exec'),{'__builtins__':safe})
        finally: sys.settrace(None)
        error=None
    except BaseException as exc:
        sys.settrace(None)
        error=type(exc).__name__+': '+str(exc)
    actual=output.getvalue()
    return dict(**case,stdout=actual,error=error,passed=error is None and actual.strip()==case['expected'].strip())

runner.run_case=browser_case
from app.core import Engine
engine=Engine('/workspace')
def dispatch(raw):
    payload=json.loads(raw)
    if payload.get('saved'): engine.state=payload['saved']
    route=payload['route']; data=payload.get('data') or {}
    if route=='state': result=dict(state=engine.state,files=engine.files(),mode='browser',workspace='浏览器独立工作区（只在此设备保存）')
    elif route=='generate':
        if data.get('live'): raise ValueError('公网演示不接收密钥；真实模型请使用本机版本')
        result=engine.generate(**data)
    elif route=='edit': result=engine.edit(**data)
    elif route=='review': result=engine.review(**data)
    elif route=='rollback': result=engine.rollback(**data)
    elif route=='publish': result=engine.publish(**data)
    elif route=='download': result=dict(zip=base64.b64encode(engine.archive()).decode())
    else: raise ValueError('未知操作')
    return json.dumps(dict(result=result,saved=engine.state),ensure_ascii=False)
`);
 return py;
})();
self.onmessage=async({data})=>{
 try{const py=await boot;py.globals.set('request_json',JSON.stringify(data.payload));const value=await py.runPythonAsync('dispatch(request_json)');self.postMessage({id:data.id,...JSON.parse(value)});}
 catch(e){self.postMessage({id:data.id,error:String(e.message||e)});}
};
