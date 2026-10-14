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

## 2. 单章生产流水线

每轮先读 `config/novel.yaml` 与 `docs/writing_orchestrator.md`。当前采用单一 Orchestrator 串行完成各角色阶段：

1. Planner：读取 `docs/ai_reading_protocol.md` 指定上下文，生成下一章详细章纲。
2. Continuity Precheck：确认章纲与 Canon、时间线、人物知识、伏笔不冲突。
3. Writer：写正文到 `chapters/draft/`。
4. Editor：只编辑已有正文，删除模板句、复述、解释性废话和凑字内容。
5. Reader Review：执行普通读者与连续性两遍审查；必要时按有限次数修订并重新审查。
6. QA：按 `qa/continuity_rules.md` 与 `qa/style_rules.md` 检查。
7. Memory Updater：只依据通过审查的正文更新 `memory/`、`plans/chapter_plan.csv` 和章节摘要。
8. Publish Gate：Reader、QA、Memory 及结构校验均通过后进入 `chapters/ready/`。
9. Publisher：只读取 `chapters/ready/`，成功发布并核验后移动到 `chapters/published/`。写作任务不执行平台发布。

每轮最多新写一个章节，不是每轮只能做一个阶段。已有章节的审核、修订、QA、Memory 与交付收尾不占新章名额；处理完后可在同一轮新写下一章。不存在质量阻塞时，不得为了等待另一个小时任务而主动结束。

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

## 8. 定时编排与旧协议兼容

2026-10-14 用户授权解除续写阻塞后，`docs/writing_orchestrator.md` 是调度行为的唯一细则。当前 `automation.mode: orchestrated` 下：

- Reader/Revision 的角色职责与质量标准继续有效；“必须独立定时任务”“一次仅一个修订动作后立刻结束”“完成 ready 后必须下轮才写”不再适用。
- 同一会话可以顺序承担不同角色，但必须标明 `reviewer_mode: orchestrator_self_review`，不得声称进行了独立模型、独立会话或人工审查。
- 旧独立 Reader/Revision 定时任务先读 automation.mode；集中模式下不修改仓库、不争抢当前章。
- 状态文件是索引，不是锁。以实际章节与对应版本的 Review/QA/摘要为准，可将已完成上一章的游标前移到当前未完成章，禁止回退或复用上一章的通过记录。
- 质量失败仍阻止依赖该章的新写作；纯执行环境/CI/平台发布等待与创作门分离，按新协议有限暂存，不强制停掉整个写作任务。
