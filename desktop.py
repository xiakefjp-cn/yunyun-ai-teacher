"""Native desktop launcher; same engine and UI as Web, real chosen directory."""
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser
from app.server import create_server

def main():
    root=tk.Tk(); root.title('耘耘AI助教 · 本机工作区'); root.geometry('540x220')
    servers=[]
    tk.Label(root,text='选择老师的真实教案目录',font=('',16)).pack(pady=15)
    tk.Label(root,text='读取目录内文本作为备课上下文；发布前显示差异并确认。\n教案包写入所选目录的 published 文件夹。').pack()
    def launch():
        directory=filedialog.askdirectory(title='打开教案与题库工作区')
        if not directory: return
        server=create_server(directory,port=0,mode='desktop'); servers.append(server)
        threading.Thread(target=server.serve_forever,daemon=True).start()
        webbrowser.open(f'http://127.0.0.1:{server.server_port}')
        messagebox.showinfo('工作区已打开','保持启动器运行。关闭窗口会停止本机服务。')
    tk.Button(root,text='打开本地目录并开始备课',command=launch).pack(pady=20)
    root.mainloop()
    for server in servers: server.shutdown(); server.server_close()

if __name__=='__main__': main()
