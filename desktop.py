"""Native desktop launcher; same engine and UI as Web, real chosen directory."""
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser
import json
from pathlib import Path
from app.server import create_server

def main():
    root=tk.Tk(); root.title('耘耘AI助教 · 本机工作区'); root.geometry('700x310')
    servers=[]
    tk.Label(root,text='选择老师的真实教案目录',font=('',16)).pack(pady=15)
    tk.Label(root,text='读取目录内文本作为备课上下文；发布前显示差异并确认。\n教案包写入所选目录的 published 文件夹。').pack()
    directory_var=tk.StringVar(value=str(Path('demo_workspace').resolve()))
    tk.Entry(root,textvariable=directory_var,width=85).pack(pady=10)
    status=tk.StringVar(value='选择或输入真实目录，再打开工作区。')
    def choose():
        directory=filedialog.askdirectory(title='打开教案与题库工作区',parent=root)
        if directory: directory_var.set(directory)
    def launch():
        try:
            directory=Path(directory_var.get()).expanduser().resolve()
            if not directory.is_dir(): raise ValueError('请选择已存在的教案目录')
            server=create_server(directory,port=0,mode='desktop'); servers.append(server)
            threading.Thread(target=server.serve_forever,daemon=True).start()
            url=f'http://127.0.0.1:{server.server_port}'
            (directory/'.yunyun'/'desktop.json').write_text(json.dumps(dict(url=url,workspace=str(directory))), 'utf-8')
            status.set('已打开 '+url+'；关闭此窗口将停止服务。')
            webbrowser.open(url)
        except Exception as exc:
            status.set('打开失败：'+str(exc))
            messagebox.showerror('工作区打开失败',str(exc),parent=root)
    tk.Button(root,text='选择目录',command=choose).pack()
    tk.Button(root,text='打开工作区并开始备课',command=launch).pack(pady=8)
    tk.Label(root,textvariable=status,wraplength=660).pack()
    root.mainloop()
    for server in servers: server.shutdown(); server.server_close()

if __name__=='__main__': main()
