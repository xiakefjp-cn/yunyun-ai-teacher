# 耘耘AI助教

[公网演示](https://xiakefjp-cn.github.io/yunyun-ai-teacher/) · [视频与源码包](https://github.com/xiakefjp-cn/yunyun-ai-teacher/releases/tag/v0.2.0) · [最终交付说明](docs/最终交付.md)

公网演示使用离线模板与浏览器Python真实验证；真实qwen-plus调用请运行本机版本。首次访问需下载Python运行环境。

为初中信息科技教师实现的可验证备课助手。Python 3.11+，仅用标准库，无需安装依赖；Windows 桌面与 Web 共享 `app/core.py`。

## 作品集与体验入口

首页展示项目能力和流程，点击“体验产品能力”进入 `studio.html` 备课工作台。公网版和本机版使用同样的两页入口。新版演示视频已按“首页 → 工作台 → 验证 → 回退 → 导出”重录，见Release v0.2.0。

## 一键启动

**推荐本机 Docker 部署**：先打开 Docker Desktop（Linux containers），双击 `start-docker.cmd`，或执行：

```powershell
docker compose up -d --build --wait --wait-timeout 180
```

打开 http://127.0.0.1:8765 ，从作品集首页点击“体验产品能力”进入本机工作台。本机无需安装Python。第一次需联网下载镜像，后续可用 `docker compose up -d --wait` 快速启动。

- 班情与种子文件首次自动复制到 `teacher_workspace/`，已有文件不覆盖。
- 教案写到 `teacher_workspace/published/`，会话、修订与备份在 `teacher_workspace/.yunyun/`，均真实保存在本机。
- 根目录 `.env` 配置百炼密钥与模型；没有key仍可选择离线模式。修改配置后运行 `docker compose up -d --force-recreate --wait`。
- 停止：双击 `stop-docker.cmd` 或 `docker compose stop`；再次启动会恢复会话。`docker compose down` 也不会删除本机工作区。
- 状态：`docker compose ps`；日志：`docker compose logs --tail 50`。端口冲突时在 `.env` 增加 `YUNYUN_PORT=8876`，然后打开相应端口。
- Linux手动部署时，绑定目录须允许容器UID 10001写入；Windows Docker Desktop直接使用项目下的目录。

以下保留无需Docker的Python启动方式：

在本目录双击 `start-web.cmd`，或运行：

```powershell
python -m app.server --workspace demo_workspace
```

打开 http://127.0.0.1:8765 。这是本机可访问 URL，**不是公网部署地址**。

桌面：双击 `start-desktop.cmd`，或 `python desktop.py`，在原生窗口选择真实教案目录，自动打开本机工作台。保持启动器开启。允许自动读取目录中的小型 Markdown/JSON/Python/TXT 文件；正式导出写到该目录 `published/`。会话与备份保存在 `.yunyun/`。

## 现场演示（约4分钟）

1. 使用默认初中班情（40人、5缺交、3死循环、6边界错误），生成《循环结构》。离线模式明确标为固定模板。
2. 查看40分钟环节、2示例、3道分层练习及其参考解、评分点。展开真实输入、期望、输出结果，共16条用例。
3. 输入“故意失败”再生成，观察 while 死循环的执行超限、定位到演示2及具体用例，尝试接受或下载会被阻止。
4. 点历史中的通过版本恢复；也可直接编辑代码、保存后重验。任意修订都会清空审核状态。
5. 检查全部条目并接受；下载 ZIP。点击预览写入差异，确认后在本机 `published/` 查看真实文件。
6. 改为大学、把缺交/死循环人数改为0，重新生成，对比时间分配、讲解与挑战题深度。
7. 关闭重开，恢复同一工作区的对话、修订和审核记录。

## 真实模型 API

也可直接编辑项目根目录 `.env`，填写 `YUNYUN_API_KEY=` 后的值。默认配置为阿里云北京接口和 `qwen-plus`。每次生成时重新读取；更新本功能后首次需重启旧服务。优先级：进程环境变量 → `.env` → `.api-config.json`。`.env` 已被Git忽略。

阿里云百炼可直接运行 `python configure-api.py`，按提示输入地域接口、模型与隐藏密钥；北京默认兼容接口与 `qwen-plus`。配置保存在Git忽略的本地 `.api-config.json`，含明文密钥，不要分享；每次调用重新读取，无需重启。环境变量优先于此文件。

在启动终端配置（不要将密钥写进源码或浏览器）：

```powershell
$env:YUNYUN_API_KEY='你的密钥'
$env:YUNYUN_API_BASE='https://api.deepseek.com/v1'
$env:YUNYUN_MODEL='deepseek-chat'
python -m app.server
```

选择“真实模型 API”。支持兼容 Chat Completions 的 HTTPS 服务。无 key 或服务失败时会报错，不会偷偷降级并声称调用成功。已使用用户提供的百炼凭证完成真实调用：首轮6个条目、16条用例通过，详见 docs/真实API验收.md；不保证任何特定模型的当前名称、资费和兼容性。每轮最多3次模型调用，每次输出最多7000 tokens；界面不自动重试，不保证总成本小于50元，应在供应商端设置额度。

模型获取工作区资料、最近8条对话与当前完整修订，返回严格JSON；引擎校验结构、真实执行全部代码，把失败报告追加回模型上下文，最多修复2轮。持久化不丢完整对话，发送模型的上下文采用有界最近历史+当前产物；这是确定性裁剪，不是模型语义压缩。固定系统前缀减少无谓变动，未实现缓存命中统计。

## 交付协议与权限

每包固定6项：1教案、2示例、基础/进阶/挑战各1题。每段代码3~8条用例。只有全部通过且全部接受，才可下载或发布；导出前再次真实复验。ZIP含结构化 JSON、教案 Markdown、代码、题干评分点、验证报告、审计与SHA256清单。拒绝撤销单项接受；恢复旧修订会清空接受状态。

读工作区、写会话与临时目录、受限教学代码验证可自动执行；正式教案包新增/覆写需先展示 diff、再点击确认，覆写自动保留备份。没有删除工具和任意 shell 工具。执行受限教学程序在打开工作区后属于已授权低风险操作，不弹每条命令审批；系统命令不开放。UI token 用于防跨站写请求，不构成账号或公网身份认证。

## 验证

```powershell
python -m unittest discover -s tests -v
python scripts/demo.py
```

`scripts/demo.py` 在独立 `demo_evidence/` 目录重现成功、失败、恢复和发布，留下可复核 JSON、ZIP 与教案。它是自动化演示证据，不是录屏视频。

## 部署与已知边界

推荐使用上文Docker Compose启动方式，已包含真实目录绑定、健康检查与资源限制；容器镜像使用Python 3.12。部署到远程主机时另行配置HTTPS、认证和访问范围。详见 [Docker本机部署](docs/Docker本机部署.md)。

本版本为**单教师单工作区演示**，所有浏览器访问共享同一会话。不能把带教师资料的实例直接暴露到公开网络。上线前应加租户隔离、容器级运行沙箱、鉴权、配额和审计保护。当前运行器禁用 import、属性、定义函数、乘法等，故不会支持通用 Python；内存边界建立失败会拒绝执行。配套用例大多与答案同源，无法证明教学内容正确；教师仍须复核，下一迭代加入教师维护的独立题库测试与课程知识点白名单。

公网演示、公开Git仓库和新版实际录屏已交付。Docker Compose提供本机持久化部署；完整原生Tk窗口验收仍按用户选择暂缓。真实API证据位于本机 demo_evidence/live/。详见 `docs/最终交付.md`。
