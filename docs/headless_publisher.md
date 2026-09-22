# Ubuntu 无图形界面发布器

Python + Playwright Chromium，Docker Compose 常驻轮询 GitHub。服务器不需要桌面、X11、VNC，也不开放控制端口。

## 定时增量发布

服务器 `/home/meow/fanqie-novel/.env` 和仓库 `.env.example` 使用以下默认值：

```dotenv
PUBLISH_INTERVAL_SECONDS=7200
HEARTBEAT_INTERVAL_SECONDS=300
MAX_CHAPTERS_PER_RUN=0
```

每两小时从 GitHub 同步并扫描 `chapters/ready/*.md`，按章号处理合格的新文件。增量依据是文件的章号、内容摘要与持久化发布记录，**不使用 commit ID、提交时间或 commit diff 判定是否新增**。同一内容已发布则跳过；已发布章号的内容被改动则拦截，不当作新章重发。Git 的提交历史仅用于正常同步和回写。

`MAX_CHAPTERS_PER_RUN=0` 表示单轮处理全部新增章节，可改为正整数限制单轮数量。审核中仍先等待核验，不跳过该章继续发送后续章节。首次启动立即扫描一次，随后每两小时运行；`/data/schedule.json` 持久化计划，重启或单轮失败不会立即重跑。修改周期后，从上一次开始扫描的时间重新计算下次执行时间。手动 `run`/`check` 不改变定时计划。

登录心跳独立为每五分钟一次，不触发 GitHub 扫描或章节发布。修改 `.env` 后执行 `docker compose up -d` 使配置生效。

## 已部署的 Cookie 登录与心跳

`meow-server:/home/meow/fanqie-novel` 已成功使用用户提供的 Cookie 登录并核验目标作品。服务默认每 300 秒执行一次真实登录态检查，即使 ready 为空也执行，成功后保存服务器更新的 Cookie。验证失败时停止本轮发布，并在 `/data/heartbeat.json` 记录失败次数和最后成功时间。Docker healthcheck 检查心跳状态及新鲜度。

Cookie 保存在命名卷 `/data/storage-state.json`，权限 0600，不进入代码、镜像或日志。未来更新 Cookie：

```bash
cd /home/meow/fanqie-novel
docker compose stop publisher
docker compose run --rm publisher import-cookies
# 隐藏输入完整 Cookie 请求头；仅验证成功才覆盖已保存会话
docker compose up -d
docker compose ps
docker compose logs --tail=30 publisher
```

程序会修复粘贴内容中 Markdown 对下划线的转义，保留百分号编码，不伪造 Cookie 的有效期。心跳能检查会话并保存站点更新的 Cookie，不能阻止平台主动撤销或强制过期；失效后重新导入或登录即可。

## 当前完成与验证范围

- 已实现 GitHub clone/fetch、认证复用、严格 ready 门槛、正文提取、提交前持久化、分页查重、发布核验、归档和 GitHub 回写。
- 2026-09-12 已在真实后台确认作品 ID、章节管理入口、章节号/标题输入框以及唯一正文编辑器。当前作品为 `7684310849036504126` / `零点异常工单`（原名“咔咔猫的新书”）。
- 已在 `meow-server`（Ubuntu、Docker 29.1.3、Compose 2.40.3）成功构建并运行容器，29 项测试全部通过，包含真实无头 Chromium 的本地页面测试、短信登录模拟、Cookie 导入、心跳状态、重启后的定时计划及按章节防重检查。
- 第 1 章《夜班》已于 2026-09-12 01:17 提交并显示“已发布”，01:18 完成远端正文重新读取核验、归档及 GitHub 回写。番茄字数 3261，远端 ID 为 `7684324432383918654`。已验证错别字提示、基础检测、使用 AI 声明和确认发布的实际流程。使用 AI 选择“是”，与本仓库实际创作流程一致。
- 正文使用编辑器原生文字输入和逐段换行，避免直接 fill 多段文本被富文本编辑器截断。归档前重新打开远端章节，按去空白后的全文逐字比较。审核中只等待，保持原 ready 文件，绝不重复提交。
- 当前面向单作品、默认分卷、立即发布。多分卷、定时发布尚未适配；不要在多分卷作品开启自动发布，查重必须覆盖所有分卷后才能支持。
- 首次认证使用手机号加短信验证码，之后会话有效时自动登录。平台要求滑块/实名或会话过期时需要本人处理。服务器 IP 也可能触发平台额外验证。

## 1. 准备 Ubuntu

安装官方 Docker Engine 与 Compose v2，参照 [Docker Ubuntu 安装文档](https://docs.docker.com/engine/install/ubuntu/)。本项目仅提供应用 Compose，不自动改变服务器 Docker 权限。

```bash
git clone https://github.com/GcMin/fanqie-novel.git
cd fanqie-novel
cp .env.example .env
mkdir -p secrets
chmod 700 secrets
```

私有仓库 clone 使用你已有的 GitHub 认证。服务器部署目录需要包含本次新增代码；若尚未提交到 GitHub，可先通过 SSH/SCP 上传工作区文件。

编辑 `.env`，检查作品 ID、作品名和 GitHub 分支。创建仅能访问此仓库的 GitHub fine-grained PAT，`Contents: Read and write` 用于读取章节及回写归档。不要把 token 写入 URL、`.env`、Git 或命令历史。交互输入：

```bash
read -rsp 'GitHub token: ' GH_TOKEN_INPUT
printf '%s' "$GH_TOKEN_INPUT" > secrets/github_token
unset GH_TOKEN_INPUT
printf '\n'
sudo chown 10001:10001 secrets/github_token
sudo chmod 600 secrets/github_token
docker compose build
```

Compose 将 token 作为只读 secret 挂载，容器使用 UID 10001。默认分支若禁止直接写入，需要给发布机器人预先配置合适的写入权限，或使用允许写入的专用分支。程序不会强推或绕过分支保护。

## 2. 手机短信验证码登录（服务器仍然是 headless）

在服务器终端运行，或者先 `ssh -t meow-server`：

```bash
cd /home/meow/fanqie-novel
docker compose stop publisher
docker compose run --rm publisher login-sms
```

程序依次提示输入大陆手机号、确认本次接受番茄的《用户协议》和《隐私政策》、输入收到的短信验证码。手机号和验证码使用隐藏输入，不写入日志、配置或 Git，截图会遮盖这两个字段。必须本人明确同意后才能勾选协议。

发送前如果出现滑块，会提示“等待人工滑块验证”，保留会话并保存 `/data/sms-login.png`。在登录终端输入 `/refresh` 更新截图；人工操作可输入 `/drag x1 y1 x2 y2`，坐标以 1440×1000 截图为准。程序只执行明确输入的拖动，不自动识别或绕过 CAPTCHA。Agent 代操作前需要用户对当前验证码明确确认。直接回车退出；不要在未确认发送时连续重发短信。

成功后会显示“登录态已保存”，再执行 `docker compose up -d`。手机号不会被当成长期登录密码，后续使用持久化 Cookie；会话失效再执行上述命令。

## 2a. 可选扫码登录

终端 A，在服务器运行：

```bash
docker compose stop publisher
docker compose run --rm --name fanqie-login publisher login
```

登录命令会持续更新截图，最长等待 5 分钟。终端 B，在服务器复制截图：

```bash
docker cp fanqie-login:/data/login.png ./login.png
```

然后从自己电脑拉取并打开图片，例如：

```bash
scp your-server:/path/to/fanqie-novel/login.png ./login.png
```

用本人手机扫码并完成确认；二维码过期就重新复制最新截图。若截图仍显示页面加载中，几秒后再复制。登录成功会输出“登录态已保存”。如果站点没有显示扫码入口，调整 `config/publisher.yaml` 的 `login_labels`；此模式不能远程操作滑块。

会话保存到 Docker 命名卷的 `/data/storage-state.json`，权限 0600。`docker compose down` 保留会话、仓库和防重复台账；不要执行 `down -v`，也不要在多个服务器/不同 Compose 项目中同时发布同一作品。截图和状态文件都包含账户信息，勿提交 Git。

## 3. 校验与启动

```bash
docker compose run --rm publisher check
```

`check` 会同步 GitHub 并验证所有 ready 文件，不打开番茄编辑器。当前仓库只会报告 0 章。

第一次有真实合格章节时，核对发布配置，把 `.env` 中 `PUBLISH_ENABLED` 改为 `true`，先单次运行：

```bash
docker compose run --rm publisher run
```

若遇到额外弹窗，获取截图：

```bash
docker compose run --rm --entrypoint cat publisher /data/last-error.png > last-error.png
```

根据真实界面调整 `config/publisher.yaml` 的按钮步骤；不要随意添加“忽略风险”“同意协议”等点击，也不要清空事务后反复重发。首次成功联调后常驻：

```bash
docker compose up -d
docker compose logs -f --tail=100 publisher
```

默认每 7200 秒同步并处理新增 ready 文件。审核中保留 ready、阻止后续章节越过，并在下一轮只核验；仅“已发布”且作品 ID、远端章节 ID、章号、标题、正文去空白后完全一致，才进入归档。

## 4. 章节输入格式

文件必须直接放在 `chapters/ready/`，不递归扫描；`README.md` 自动忽略。格式示例仅作说明，不是可供发布的测试章节：

```markdown
---
chapter: 1
title: 门后的脚步
status: ready
qa: pass
---
# 第1章 门后的脚步

这里放通过 QA 的完整小说正文。

<!-- 内部注释会被剥离，不发送 -->
```

`title` 不含“第1章”，序号填入独立输入框。正文可带一个与元数据一致的一级标题，标题和 HTML 注释会剥离；其余正文必须为纯文本，不允许 Markdown 链接、代码块、内部小标题、TODO 或未结构化 QA/大纲备注。有疑义会整章拦截，避免误删小说内容或泄露资料。

`plans/chapter_plan.csv` 中必须有且仅有一行对应章号，标题一致、`status` 为 `completed` 或 `ready`，`qa_status` 为 `pass`。作品生产流水线负责在进入 ready 前完成 Memory 和两项 QA；发布器不生成正文，也不伪造 QA 结果。

## 5. 中断与恢复

查看台账须先停止常驻服务（整个周期持有锁，防止登录/发布并发）：

```bash
docker compose stop publisher
docker compose run --rm publisher status
```

- `preparing`：新建前已记录，但可能还没取得远端 ID。核对后台草稿箱，禁止直接重发。
- `editing`：已取得远端 URL，但填写/提交未完成。本人在后台核对处理。
- `submitted`：已进入提交步骤，结果可能未知。重启只核验，绝不再次点击提交。
- `quota_deferred`：平台明确返回每日字数上限，且原章节已保存。按北京时间跨日后，在下一次定时任务中先检查发布列表与原远端章节的完整正文，再恢复原 URL 提交；不会新建重复章节。同日不会重复尝试。普通超时不会进入此状态。
- `archiving`：番茄已核验，但本地/GitHub 归档可能中断。保留所有文件，人工核对本地 published、CSV 和 GitHub 提交后处理；服务会停在这一章，不掩盖部分成功。
- `published`：核验、快照、CSV 及 GitHub push 均完成。

如果本人已在后台完成中断章节的发布，绑定正确远端编辑 URL 后只核验：

```bash
docker compose run --rm publisher reconcile --chapter 1 --url 'https://fanqienovel.com/main/writer/作品ID/publish/章节ID'
```

`reconcile` 不新建、不提交，仅核验已有事务与匹配的 ready 文件；同号/同名但不同远端 ID 或正文变化都会拦截。仍在审核可稍后重复此命令。

本地 GitHub 回写失败会保留文件和 commit；下一次同步只做正常 push/fast-forward。远端与本地分叉、未提交修改均需人工处理。不要使用 `reset --hard`、清空台账或删除数据卷解决发布故障，这会丢失防重依据。

没有邮件/消息通知集成；检查 `docker compose logs` 和 `/data/last-status.json` 可接入你现有的监控。更新源码后 `docker compose build && docker compose up -d`；`.env` 改动也需要重新创建服务。

## 开发验证

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
```

测试覆盖正文隔离、QA/计划门槛、路径限制、重复章号、归档以及“提交后断网再运行不会重发”。测试正文只存在临时目录，不提交到番茄。
