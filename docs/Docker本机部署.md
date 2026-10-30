# Docker本机部署

## 一键运行

打开Docker Desktop（Linux containers），在项目目录执行：

```powershell
docker compose up -d --build --wait --wait-timeout 180
```

或双击 `start-docker.cmd`。打开 http://127.0.0.1:8765 ，点击“体验产品能力”进入工作台。容器使用Python 3.12，仅标准库，无需在Windows另装Python。

项目根目录 `.env` 配置 `YUNYUN_API_KEY`、`YUNYUN_API_BASE` 和 `YUNYUN_MODEL`。本机已有百炼配置已接入；仓库只包含空白 `.env.example`。Docker构建上下文按白名单复制源码与种子数据，排除密钥、Git历史、本地会话和导出文件。没有密钥仍可使用离线模板。

## 真正落在本机的文件

- `teacher_workspace/`：首次初始化10个教学种子文件，已有文件不覆盖。
- `teacher_workspace/published/`：审核确认后的教案、代码、题目和报告。
- `teacher_workspace/.yunyun/`：会话、修订、审计及覆写备份。

以上均为Windows绑定目录，不依赖容器可写层。停止、重启或重建容器仍保留。该目录已被Git忽略。

```powershell
docker compose ps
docker compose logs --tail 50
docker compose stop
docker compose up -d --wait
```

修改 `.env` 后：`docker compose up -d --force-recreate --wait`。端口冲突可在 `.env` 设置 `YUNYUN_PORT=8876`，再使用新端口。Linux主机须确保绑定目录对UID 10001可写。

## 本机验收（2026-10-30）

- 镜像真实构建、容器健康检查通过；监听127.0.0.1:8765。
- 浏览器从作品集首页成功进入Docker工作台，显示docker模式和真实API选项。
- 容器内真实qwen-plus生成，5段课堂代码的16条用例全部通过。
- 人工注入死循环的自动化验收：验证失败，下载被拒绝；回退后重新审核、下载ZIP并确认发布，本机文件已生成。
- 实际重启容器后，修订ID、6个接受状态和已发布教案均保留，恢复检查通过。
- 进程UID为10001，镜像中不存在 `.env` 或 `.api-config.json`。进程内存、CPU和子进程数量受Compose限制；这不构成通用代码运行服务。

原始验收结果保存在本机 `deliverables/docker-acceptance.json`。复现会真实调用API并产生少量费用：`python scripts/test-docker.py --live`；重启后恢复检查：`python scripts/test-docker.py --resume`。

原生Tk启动器是另一种宿主形态；本项完成的是Docker本机Web部署，不等同于原生窗口验收。
