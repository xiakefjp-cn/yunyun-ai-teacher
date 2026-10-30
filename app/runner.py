"""Restricted teaching Python: positive AST grammar + separate bounded process.

This is deliberately NOT a general-purpose Python sandbox.
"""
import ast
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ALLOWED = {"Module", "Expr", "Assign", "AugAssign", "Name", "Load", "Store", "Constant",
           "BinOp", "UnaryOp", "Add", "Sub", "Mult", "FloorDiv", "Mod", "USub", "UAdd",
           "Compare", "Eq", "NotEq", "Lt", "LtE", "Gt", "GtE", "If", "For", "While",
           "Call", "List", "Tuple", "Subscript", "BoolOp", "And", "Or", "Not", "Break",
           "Continue", "Pass", "IfExp"}
CALLS = {"print", "input", "int", "str", "range", "len", "abs", "min", "max", "sum"}

def check(code):
    if len(code) > 12000:
        raise ValueError("代码过长")
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if type(node).__name__ not in ALLOWED:
            raise ValueError("教学运行器不允许语法: " + type(node).__name__)
        if isinstance(node, ast.Name) and (node.id.startswith('_') or
                isinstance(node.ctx, ast.Store) and node.id in CALLS):
            raise ValueError("不允许覆盖内置函数或使用私有名称")
        if isinstance(node, ast.Call) and (not isinstance(node.func, ast.Name) or
                node.func.id not in CALLS or node.keywords):
            raise ValueError("只允许教学内置函数")
        if isinstance(node, ast.Constant) and (not isinstance(node.value, (int, str, bool, type(None)))
                or isinstance(node.value, str) and len(node.value) > 1000
                or isinstance(node.value, int) and abs(node.value) > 1000000):
            raise ValueError("常量超出教学范围")
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
            # Sequence multiplication can allocate before a trace hook fires.
            raise ValueError("受限运行器暂不支持乘法，请使用累加；可扩展容器运行器")
    return tree

WRAPPER = '''import sys,json,io,os
# Hard process memory limit: enforce before evaluating teaching code.
if os.name=='nt':
 import ctypes
 from ctypes import wintypes
 class BASIC(ctypes.Structure):
  _fields_=[('PerProcessUserTimeLimit',ctypes.c_longlong),('PerJobUserTimeLimit',ctypes.c_longlong),('LimitFlags',wintypes.DWORD),('MinimumWorkingSetSize',ctypes.c_size_t),('MaximumWorkingSetSize',ctypes.c_size_t),('ActiveProcessLimit',wintypes.DWORD),('Affinity',ctypes.c_size_t),('PriorityClass',wintypes.DWORD),('SchedulingClass',wintypes.DWORD)]
 class IO(ctypes.Structure):
  _fields_=[(n,ctypes.c_ulonglong) for n in ['ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount']]
 class EXT(ctypes.Structure):
  _fields_=[('BasicLimitInformation',BASIC),('IoInfo',IO),('ProcessMemoryLimit',ctypes.c_size_t),('JobMemoryLimit',ctypes.c_size_t),('PeakProcessMemoryUsed',ctypes.c_size_t),('PeakJobMemoryUsed',ctypes.c_size_t)]
 k=ctypes.WinDLL('kernel32',use_last_error=True)
 k.CreateJobObjectW.restype=wintypes.HANDLE
 k.SetInformationJobObject.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD]
 k.AssignProcessToJobObject.argtypes=[wintypes.HANDLE,wintypes.HANDLE]
 k.GetCurrentProcess.restype=wintypes.HANDLE
 job=k.CreateJobObjectW(None,None); limits=EXT(); limits.BasicLimitInformation.LimitFlags=0x100; limits.ProcessMemoryLimit=128*1024*1024
 if not k.SetInformationJobObject(job,9,ctypes.byref(limits),ctypes.sizeof(limits)) or not k.AssignProcessToJobObject(job,k.GetCurrentProcess()):
  raise RuntimeError('无法建立内存边界，拒绝运行')
else:
 import resource
 resource.setrlimit(resource.RLIMIT_AS,(128*1024*1024,128*1024*1024))
 resource.setrlimit(resource.RLIMIT_CPU,(2,2))
payload=json.loads(sys.stdin.read())
budget=0
def trace(frame,event,arg):
 global budget
 budget+=1
 if budget>30000: raise RuntimeError('执行步数超限：疑似死循环')
 return trace
class Output(io.StringIO):
 def write(self,s):
  if self.tell()+len(s)>12000: raise RuntimeError('输出超限')
  return super().write(s)
out=Output()
sys.stdin=io.StringIO(payload['stdin'])
sys.stdout=out
safe={k:__builtins__.__dict__[k] for k in ['print','input','int','str','range','len','abs','min','max','sum']}
sys.settrace(trace)
try:
 exec(compile(payload['code'],'<lesson>','exec'),{'__builtins__':safe})
 result={'stdout':out.getvalue(),'error':None}
except BaseException as e:
 result={'stdout':out.getvalue(),'error':type(e).__name__+': '+str(e)}
sys.settrace(None)
sys.stdout=sys.__stdout__
print(json.dumps(result,ensure_ascii=True))
'''

def run_case(code, case):
    try:
        check(code)
        with tempfile.TemporaryDirectory(prefix="yunyun-run-") as directory:
            result = subprocess.run([sys.executable, '-I', '-S', '-c', WRAPPER],
                input=json.dumps({'code': code, 'stdin': case['stdin']}),
                text=True, capture_output=True, timeout=2, cwd=directory,
                env={'SYSTEMROOT': __import__('os').environ.get('SYSTEMROOT', '')})
        actual = json.loads(result.stdout) if result.returncode == 0 else {'stdout':'', 'error':result.stderr[:1000]}
    except Exception as e:
        actual = {'stdout':'', 'error':str(e)}
    return {**case, **actual, 'passed': actual['error'] is None and actual['stdout'].strip() == case['expected'].strip()}

def verify(bundle):
    return [{'id': item['id'], 'title': item['title'],
             'cases':[run_case(item['code'], c) for c in item['tests']]}
            for item in bundle['items'] if item['kind'] in ('example','exercise')]

def passed(reports):
    return bool(reports) and all(r['cases'] and all(c['passed'] for c in r['cases']) for r in reports)
