# fanqie-novel

用于长期 AI 辅助长篇小说创作、连续性维护、质量审查与番茄小说发布的私有仓库。

## 核心原则

1. **正文与记忆分离**：模型不依赖重新阅读全书维持记忆，而使用结构化世界状态、人物状态、伏笔、时间线与章节摘要。
2. **越近越详细**：全书主线最稳定；当前卷/剧情弧更详细；未来 5–10 章为粗纲；下一章才写详细章纲。
3. **先规划、再写、再审**：Planner → Writer → Editor → Continuity QA → Memory Update → Publish Ready。
4. **番茄只接收最终章节正文**：`bible/`、`outlines/`、`memory/`、`plans/`、`qa/`、`docs/` 永远不发布到番茄。
5. **禁止为凑字数注水**：章节长度是区间，不是精确字数目标；剧情变化和阅读节奏优先。
6. **降低模板化 AI 文本特征的方式是提高写作质量**，不是规避检测器：删解释、删复述、区分人物语言、减少套话、保留自然的不完整表达和节奏变化。

## 目录

- `AGENTS.md`：AI/Agent 的最高优先级写作与维护规则
- `config/novel.yaml`：长度、读取窗口、发布门槛等机器可读配置
- `bible/`：不可轻易推翻的作品圣经、世界观、人物与文风
- `outlines/`：分卷、剧情弧、未来章节规划
- `plans/`：章节状态与生产计划
- `chapters/draft/`：生成后尚未通过 QA 的正文
- `chapters/ready/`：唯一允许番茄发布器读取的待发布正文
- `chapters/published/`：已确认发布成功的正文快照
- `memory/`：动态长期记忆、人物知识、关系、时间线、伏笔
- `qa/`：连续性与文风检查规则、最近一次检查报告
- `docs/`：AI 读取协议与番茄发布协议

## 单章生命周期

```text
读取规定上下文
  ↓
生成下一章详细章纲
  ↓
写入 chapters/draft/
  ↓
编辑去模板感 / 去复述 / 去注水
  ↓
连续性检查
  ↓
更新 memory/ 与 plans/
  ↓
QA 通过后移动到 chapters/ready/
  ↓
番茄发布器只读取 ready/
  ↓
发布成功并核验
  ↓
移动到 chapters/published/
```

详细规则见 `docs/ai_reading_protocol.md` 与 `docs/publishing_protocol.md`。

## Ubuntu 无头自动发布

已加入 Python + Playwright 发布器与 Docker Compose 配置。支持 Cookie 导入和手机号加短信验证码登录，复用会话，从 GitHub 同步 `chapters/ready/`，核验已发布后归档并回写仓库。服务器已使用 Cookie 登录，每 5 分钟检查登录态并保存更新后的 Cookie。

`.env` 默认 `PUBLISH_INTERVAL_SECONDS=7200`，每两小时按 ready 章节文件与发布记录增量推送，不按 commit 判断；`HEARTBEAT_INTERVAL_SECONDS=300` 独立控制登录心跳。

部署、输入格式和中断处理见 [无头发布器部署文档](docs/headless_publisher.md)。示例配置默认关闭公开发布；服务器首章《夜班》已实际发布、核验完整正文并归档回写 GitHub。后续使用已验证的正文输入和发布弹窗流程。
