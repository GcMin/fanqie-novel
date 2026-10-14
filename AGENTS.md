# AGENTS.md

本文件是本仓库所有 AI/Agent 的最高优先级创作约束。除非用户明确修改规则，否则不得自行绕过。

## 1. 核心目标

持续创作长篇小说，同时保持：
- 主线不漂移；
- 世界规则不自相矛盾；
- 人物动机、知识、伤势、物品、关系连续；
- 伏笔可追踪并按计划回收；
- 每章都有实际变化，不靠复述和空洞心理活动注水；
- 文本自然、人物有语言区分度，避免模板化 AI 腔。

## 2. 单章生产流水线与角色分工

每轮先读 `config/novel.yaml`；当前 `automation.mode: split_roles`，细则见 `docs/writing_roles.md`。用户明确指定 Writer 会话只负责“新章详细章纲 + 新章正文首稿”，不得替其他会话执行修订或审核。

章节仍遵循顺序：
1. Writer 会话：读取 `docs/ai_reading_protocol.md` 规定上下文，完成 Planner 和 Continuity Precheck，创建 `plans/chapter_NNNN_plan.md` 与 `chapters/draft/NNNN.md`。
2. 独立 Reader 会话：两遍阅读，产出与正文版本绑定的 Reader Review；不修改正文。
3. 独立 Revision 会话：依据 Review 的 BLOCKER/MAJOR 修订或重写已有草稿，正文变更后重新送 Reader，不擅自写新章。
4. 独立 QA/Memory/Publish Gate 会话：在 Review 通过后执行 Continuity QA、Style QA、必要 Memory 更新和结构校验，合格才将对应草稿移入 ready。
5. Publisher：只读取 ready，并在番茄平台实际发布核验成功后归档 published；Writer 不执行平台发布。

Writer 每轮最多创建一个以前不存在的章节。上一章还在待审时可先以其**特定版本**作临时连续性参考写下一章，但必须保存依赖章号与 Git blob SHA；后续 Reader/QA 必须核对前章最终版是否改变关键事实。未经确认的前章不能被写成既成 Canon。若前章修订导致冲突，应由独立修订/QA 会话处理后章衔接，Writer 不回头自行修改旧稿。

## 3. 硬规则

- 不得一次性靠重新阅读全书来维持记忆。
- 不得修改已经确认的 Canon 来迁就新章节；若确需 Retcon，必须显式记录并等待用户确认。
- 不得让角色知道 `memory/knowledge_state.yaml` 中其尚未知晓的信息。
- 不得忘记伤势、物品、位置、时间、关系与承诺。
- 不得为了达到目标字数重复描写、重复总结上一章或追加空洞内心戏。
- 不得把内部大纲、Memory、QA 报告、提示词、YAML/CSV 元数据发布到番茄。
- 不得把 `chapters/draft/` 内容直接发布。
- 不以“逃过 AI 检测器”为目标。目标是自然、具体、连贯、可读、有作者风格的文本。
- 不得把 CI 成功当作 Reader/内容 QA 通过，也不得为解除流程阻塞伪造审查结果。

## 4. 单章最低剧情变化

一章结束时，至少有一项发生有意义变化：新信息、人物关系、人物目标、危险程度、资源/物品、身份暴露、地点/处境、行动计划、读者认知。

若以上均无变化，应判定该章存在注水风险并重写章纲。

## 5. 冲突优先级

发生冲突时按以下优先级判断：
1. 用户最新明确要求；
2. `bible/` 中的硬 Canon；
3. 已发布章节事实；
4. `memory/` 当前状态；
5. 当前卷/剧情弧大纲；
6. 未来粗纲；
7. Writer 自由发挥。

本次流程调整不改变故事 Canon、主线硬节点或已发布事实。

## 6. 文件状态与校验

- `chapters/draft/`：尚未交付的正文，可能处于待审、修订、QA 或交付阻塞阶段，均不可发布。
- `chapters/ready/`：Reader、QA、Memory 与结构校验通过，唯一允许番茄发布器读取的目录。
- `chapters/published/`：番茄已发布并核验成功的正文快照。

任何 Agent 看到 `status: draft` 都不得发布。

- 修改 `plans/chapter_plan.csv` 时，必须保留所有 ready 章节对应的唯一计划行、原有标题和真实 QA 结果，直到发布核验完成。
- 更新计划或 ready 后必须执行结构校验。写作端首选 `python -m publisher.check_local --repo .`，它直接检查当前快照，不联网、不克隆、不登录、不写发布数据库。
- 已真实通过 QA 的草稿可用 `python -m publisher.check_local --repo . --candidate chapters/draft/NNNN.md` 预检拟交付内容。此命令不会自动批准或移动正文。
- 原 `python -m publisher check` 保留作发布服务器的同步后复检，不再是写作唯一可用的校验入口。CI 检查触发提交的 checkout，不重新拉取浮动 main。
- 所有结构成功都必须关联真实输入版本。未执行、失败或检查旧版本均不得标为成功。

## 7. 章节标题发布规则

- 新进入 ready 的章节标题至少包含 5 个非空白字符，不含“第 N 章”。
- Frontmatter、正文标题（若存在）与计划表标题必须一致。
- 标题被平台拒绝时，修改须经用户确认，保留原远端章节 ID 和正文，核对后恢复，不重复建章。

## 8. 每小时任务分工（2026-10-14 最新用户要求）

目前选择 `split_roles`：本会话只负责新章 Writer。完整详细要求见 `docs/writing_roles.md`；旧 `docs/writing_orchestrator.md` 只适用于先前 `orchestrated` 模式，不作为当前角色的执行约束。

- Writer：只创建新章详细章纲与首稿，不读取历史 Reader Review、不审核、不修订现有稿、不改长期 Memory、不设置 QA/ready/published、不发布番茄。
- Reader：独立审查草稿；Revision：独立负责当前章修订；QA/Memory/Publish Gate：由独立收尾会话操作，各阶段必须保留可验证来源。
- 原有 Reader/Revision 定时任务应在 `split_roles` 模式真实工作，不得沿用集中模式“只检查配置然后退出”的指令。
- Writer 允许在上一章尚未审定时启动下一新章，但新稿必须标注所依赖上章的具体 blob SHA，供其他会话在前章发生修订时核对；这只是预先创作许可，**不是**提前通过 QA 或进入 ready 的许可。
- 禁止复用其他章的 Reader/QA 结果，禁止为了按时新写而修改前章 Canon。所有 GitHub 写入须保护最新 main，遇并发冲突重新读取后再提交，不强推。
