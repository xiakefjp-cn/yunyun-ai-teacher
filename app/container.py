"""Initialize an actual mounted teacher workspace without overwriting files."""
from pathlib import Path
import shutil
from .server import create_server

def main():
    root=Path('/workspace')
    root.mkdir(parents=True,exist_ok=True)
    for seed in Path('/srv/yunyun/seeds').iterdir():
        target=root/seed.name
        if seed.is_file() and not target.exists(): shutil.copyfile(seed,target)
    server=create_server(root,host='0.0.0.0',port=8765,mode='docker')
    print('Yunyun is ready on port 8765; persistent teacher workspace: /workspace',flush=True)
    server.serve_forever()

if __name__=='__main__': main()
