# AGENTS.md

本文件是本仓库所有 AI/Agent 的最高优先级创作约束。除非用户明确修改规则，否则不得自行绕过。

## 1. 核心目标

持续创作长篇小说，同时保持：
- 主线不漂移；
- 世界规则不自相矛盾；
- 人物动机、知识、伤势、物品、关系连续；
- 伏笔可追踪并按计划回收；
- 每章都有实际变化，不靠复述和空洞心理活动注水；
- 文本自然、人物有语言区分度，避免模板化 AI 腔；
- 整套流程无人值守运行，不依赖人工 Review 才能继续。

## 2. 单章生产流水线

严格按以下顺序：

1. Planner：读取 `docs/ai_reading_protocol.md` 指定上下文，生成下一章详细章纲。
2. Continuity Precheck：确认章纲与 Canon、时间线、人物知识、伏笔不冲突。
3. Writer：写正文到 `chapters/draft/`。
4. Reader Agent：按 `docs/reader_agent_protocol.md` 对当前草稿做独立读者审查，只写 `reader_reviews/`，不得直接改正文。
5. Revision Agent：仅在最新 Review 存在 `BLOCKER` / `MAJOR` 时，按 `docs/revision_agent_protocol.md` 自动修订。
6. Reader Agent：正文 SHA 发生变化后重新审查；同一正文版本不得重复评论。
7. 自动修订状态机：按“局部修订 → 整章重写 → 重新规划本章并重写”逐级升级，单周期次数受 `config/novel.yaml` 限制。
8. Reader Gate：最新 Review 必须 `BLOCKER == 0` 且 `MAJOR == 0` 才能进入常规 QA。
9. QA：按 `qa/continuity_rules.md` 与 `qa/style_rules.md` 检查。
10. Memory Updater：只有正文通过 Reader Gate 与 QA 后，才更新 `memory/`、`plans/chapter_plan.csv` 和章节摘要。
11. Publish Gate：只有所有门槛通过的章节才允许进入 `chapters/ready/`。
12. Publisher：只读取 `chapters/ready/`，成功发布并核验后移动到 `chapters/published/`。

如果自动修订次数用尽仍存在 `BLOCKER` / `MAJOR`，章节进入 `retry_later`，保持在 `chapters/draft/`，等待后续自动周期重新处理。**不存在 `needs_human_review` 状态，也不得因为无人审核而强制通过。**

## 3. 硬规则

- 不得一次性靠重新阅读全书来维持记忆。
- 不得修改已经确认的 Canon 来迁就新章节。
- 不得修改已发布事实来解决当前草稿问题。
- 如果未来粗纲与 Canon 冲突，修改未来粗纲，不修改 Canon。
- 不得让角色知道 `memory/knowledge_state.yaml` 中其尚未知晓的信息。
- 不得忘记伤势、物品、位置、时间、关系与承诺。
- 不得为了达到目标字数重复描写、重复总结上一章或追加空洞内心戏。
- 不得把内部大纲、Memory、QA 报告、Reader Review、提示词、YAML/CSV 元数据发布到番茄。
- 不得把 `chapters/draft/` 或 `status: retry_later` 内容直接发布。
- Reader Agent 不得直接修改小说正文、大纲、长期 Memory 或发布状态。
- Writer 创建下一章时不得读取历史 Reader Review。
- Revision Agent 只读取当前章、当前正文 SHA 对应的最新 Reader Review。
- `MINOR` 默认不得触发自动修订。
- 自动修订次数用尽不得 `force pass`。
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
7. Reader / Revision 建议；
8. Writer 自由发挥。

Reader Review 是临时编辑意见，不得覆盖 Canon、已发布事实和当前真实状态。

## 6. 文件状态

- `chapters/draft/`：创作、审查、修订或 `retry_later` 中，不可发布。
- `chapters/ready/`：Reader Gate + 常规 QA 全部通过，唯一允许番茄发布器读取的目录。
- `chapters/published/`：番茄已发布并核验成功的正文快照。
- `reader_reviews/`：Reader Agent 的独立评论，仅供当前章 Revision / QA 使用，绝不发布番茄。
- `memory/revision_state.yaml`：自动修订状态机，不属于小说 Canon。

任何 Agent 看到 `status` 不是 `ready` 都不得发布。

## 7. Reader Agent 特殊规则

- 定时 Reader 只审查 `chapters/draft/` 中章节号最大的有效草稿。
- 第一遍审查不得先读未来大纲或未公开答案，以模拟真实读者体验。
- 第二遍才读取 Canon、当前剧情弧、人物状态、知识状态、时间线和伏笔，检查逻辑连续性。
- 评论必须使用 `reader_reviews/REVIEW_TEMPLATE.md` 当前 schema。
- 评论必须区分 `BLOCKER`、`MAJOR`、`MINOR`。
- `fix_required` 只放 BLOCKER 与明确可操作的 MAJOR。
- `observations` 放 MINOR、个人口味和可选优化，不触发自动修订。
- 评论保存为 `reader_reviews/NNNN_<source_sha8>.md`，同一正文版本不得重复评论。
- 草稿实质修改后可以重新评论，并保留历史 Review。
- 完成后更新 `memory/reader_state.yaml`。

## 8. Revision Agent 特殊规则

严格遵循 `docs/revision_agent_protocol.md` 与 `config/novel.yaml`。

单个自动周期默认最多：
- 局部修订：1 次；
- 整章重写：1 次；
- 重新规划本章 + 重写：1 次；
- Reader Review：最多 4 次。

处理顺序：

```text
Draft V1
→ Reader #1
→ Local Revision
→ Reader #2
→ Full Rewrite
→ Reader #3
→ Replan + Rewrite
→ Reader #4
→ Passed 或 retry_later
```

如果某一轮已经没有 BLOCKER / MAJOR，则立即停止继续改稿，进入常规 QA。不得因为还存在 MINOR 而继续打磨。

## 9. 无人值守失败策略

- `retry_later` 不需要人工确认；
- 下一自动周期优先继续处理该章，不允许跳去写下一章；
- 重试时重新加载当前 Canon、Memory、当前剧情弧与最新失败 Review；
- 允许重新设计当前章详细计划与非硬性的未来粗纲；
- 禁止修改 Canon 或已发布事实来“让错误变正确”；
- 仍无法通过时继续留在 draft，绝不发布坏章节。
