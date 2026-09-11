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

严格按以下顺序：

1. Planner：读取 `docs/ai_reading_protocol.md` 指定上下文，生成下一章详细章纲。
2. Continuity Precheck：确认章纲与 Canon、时间线、人物知识、伏笔不冲突。
3. Writer：写正文到 `chapters/draft/`。
4. Reader Agent：按 `docs/reader_agent_protocol.md` 对最新草稿做独立读者审查，评论写入 `reader_reviews/`，不得直接修改正文。
5. Editor：结合 Reader Review 编辑已有正文，不擅自推进下一章剧情；删除模板句、复述、解释性废话和凑字内容。
6. QA：按 `qa/continuity_rules.md` 与 `qa/style_rules.md` 检查。
7. Memory Updater：更新 `memory/`、`plans/chapter_plan.csv` 和章节摘要。
8. Publish Gate：只有 QA 通过的章节才允许进入 `chapters/ready/`。
9. Publisher：只读取 `chapters/ready/`，成功发布并核验后移动到 `chapters/published/`。

Reader Agent 可以按定时任务异步执行；如果某次 Reader Review 尚未完成，当前阶段它是建议型 QA，不自动改变 `status` 或 `qa` 字段。

## 3. 硬规则

- 不得一次性靠重新阅读全书来维持记忆。
- 不得修改已经确认的 Canon 来迁就新章节；若确需 Retcon，必须显式记录并等待用户确认。
- 不得让角色知道 `memory/knowledge_state.yaml` 中其尚未知晓的信息。
- 不得忘记伤势、物品、位置、时间、关系与承诺。
- 不得为了达到目标字数重复描写、重复总结上一章或追加空洞内心戏。
- 不得把内部大纲、Memory、QA 报告、Reader Review、提示词、YAML/CSV 元数据发布到番茄。
- 不得把 `chapters/draft/` 内容直接发布。
- Reader Agent 不得直接修改小说正文、大纲、Memory 或发布状态。
- 不以“逃过 AI 检测器”为目标。目标是自然、具体、连贯、可读、有作者风格的文本。

## 4. 单章最低剧情变化

一章结束时，至少有一项发生有意义变化：
- 新信息；
- 人物关系；
- 人物目标；
- 危险程度；
- 资源/物品；
- 身份暴露；
- 地点/处境；
- 行动计划；
- 读者认知。

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

## 6. 文件状态

- `chapters/draft/`：未通过 QA，不可发布。
- `chapters/ready/`：已通过 QA，唯一允许番茄发布器读取的目录。
- `chapters/published/`：番茄已发布并核验成功的正文快照。
- `reader_reviews/`：Reader Agent 的独立评论，仅供 Writer / Editor / QA 参考，绝不发布番茄。

任何 Agent 看到 `status: draft` 都不得发布。

## 7. Reader Agent 特殊规则

- 定时 Reader 只审查 `chapters/draft/` 中章节号最大的有效草稿。
- 第一遍审查不得先读未来大纲或未公开答案，以模拟真实读者体验。
- 第二遍才读取 Canon、当前剧情弧、人物状态、知识状态、时间线和伏笔，检查逻辑连续性。
- 评论必须区分 `BLOCKER`、`MAJOR`、`MINOR`。
- 评论保存为 `reader_reviews/NNNN_<source_sha8>.md`，同一正文版本不得重复评论。
- 草稿实质修改后可以重新评论，并保留历史 Review。
- 完成后更新 `memory/reader_state.yaml`。
