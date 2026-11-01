# 在自己的电脑上启动

## 第一次用

1. 下载并解压项目源码，打开 Docker Desktop。这里需要使用Linux容器模式，通常是默认设置。
2. 如果要用真实模型，把项目里的 `.env.example` 复制成 `.env`，填写自己的密钥。只想试试流程，可以先不填。
3. 双击 `start-docker.cmd`，等它显示启动成功。第一次要下载镜像，可能较慢。
4. 打开 [本机页面](http://127.0.0.1:8765)，点击“体验产品能力”。用Docker启动后，不需要再装Python。

喜欢用命令行的话，在解压后的项目目录执行：

```powershell
docker compose up -d --build --wait --wait-timeout 180
```

## 密钥怎么填

用记事本打开 `.env`，在 `YUNYUN_API_KEY=` 后粘贴自己的阿里云百炼密钥。`YUNYUN_API_BASE` 填这个密钥对应的接口地址，注意地域和业务空间；`YUNYUN_MODEL` 是模型名称，示例为qwen-plus。

密钥只留在自己的电脑上，不要和源码一起分享。GitHub提供的文件不含任何人的密钥。

配置改完后执行下面的命令，让程序读到新值，再在页面选择“真实模型 API”：

```powershell
docker compose up -d --force-recreate --wait
```

真实模型会使用你账号的额度。不填密钥仍然可以选离线模板。

## 教案存在哪里

都在项目里的 `teacher_workspace` 文件夹：

|位置|里面是什么|
|---|---|
|published|老师审核确认后的教案、代码、练习和检查结果|
|.yunyun|聊天记录、历史版本、审核记录和旧文件备份|
|文件夹里的其他文件|首次启动时放入的教学示例资料，已有文件不会被替换|

这些文件保存在电脑上。停止、重启或重建Docker中的程序不会清空它们；如果手动删除这个文件夹，记录就会丢失。

## 下次用、停止和排查问题

- 下次启动：再双击 `start-docker.cmd`；不想重复构建，也可运行 `docker compose up -d --wait`。
- 停止：双击 `stop-docker.cmd`，或运行 `docker compose stop`。
- 查看是否启动：运行 `docker compose ps`。
- 启动失败：先看Docker Desktop是否已打开，再运行 `docker compose logs --tail 50` 查看提示。
- 如果8765端口被其他程序占用：在 `.env` 加一行 `YUNYUN_PORT=8876`，重新启动后打开 http://127.0.0.1:8876 。

以上步骤针对Windows Docker Desktop。Linux部署者还需保证工作文件夹允许编号10001的容器用户写入。

## 实际检查结果

已在本机完成：真实模型生成、16项代码测试、故意死循环后禁止下载、恢复旧版、审核、下载以及保存文件。实际重启Docker中的程序后，历史版本、6项审核和教案文件都还在。

检查记录在本机 `deliverables/docker-acceptance.json`。开发者可以运行 `python scripts/test-docker.py --live` 重做，会调用付费API；重启后可运行 `python scripts/test-docker.py --resume` 检查恢复。

桌面启动器的使用与检查另见 [桌面测试记录](桌面验收.md)。
