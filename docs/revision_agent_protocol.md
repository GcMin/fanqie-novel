> **当前 Revision 阶段由唯一 Audit 定时任务执行；不存在单独 Revision 定时任务。GitHub 写入失败不得暂停定时任务，下一轮重试。以 `docs/combined_audit_protocol.md` 为最新职责说明。**

# Revision Agent 全自动修订协议

本协议用于在**没有人工 Review**的情况下处理 Reader Agent 发现的问题。

Revision Agent 与 Writer 分离：Writer 负责首次创作；Revision Agent 只处理当前章节最新 Reader Review 中的 `fix_required`。Writer 不得读取历史 `reader_reviews/` 来影响后续章节写作。

## 1. 目标

- 自动修复 `BLOCKER` 与明确的 `MAJOR`；
- `MINOR` 默认只记录，不触发自动修改；
- 防止 Reader / Writer / Editor 无限往返修改；
- 不允许为了“通过审查”修改 Canon、已发布事实或让人物行为失真；
- 修订失败时宁可暂停发布并稍后自动重试，也不得强制进入 `ready/`；
- 连续失败后自动降低创作复杂度，而不是无限增加新桥段尝试救火。

## 2. 严重度处理

### BLOCKER
必须修复。包括但不限于：
- Canon 冲突；
- 角色知道其尚不知道的信息；
- 时间、地点、伤势、物品等硬连续性错误；
- 关键因果链断裂；
- 本章核心事件无法成立。

### MAJOR
默认必须修复，前提是问题描述具体且可操作。包括：
- 人物行为缺少足够动机；
- 关键信息释放导致读者无法理解；
- 明显节奏失衡；
- 对话或场景严重损害人物可信度；
- 大段重复、解释或模板化表达明显影响阅读。

### MINOR
默认不自动修复。仅作为编辑观察记录，避免为了局部措辞无限重写。

## 3. 单章自动修订状态机

```text
Writer 生成 Draft V1
    ↓
Reader Review #1
    ↓
无 BLOCKER / MAJOR ─────────→ 常规 QA
    │
    └─ 有 BLOCKER / MAJOR
           ↓
Stage A：局部修订（最多 1 次）
           ↓
Reader Review #2
           ↓
通过 ──────────────────────→ 常规 QA
           │
           └─ 仍有 BLOCKER / MAJOR
                  ↓
Stage B：整章重写（最多 1 次）
                  ↓
Reader Review #3
                  ↓
通过 ─────────────────────→ 常规 QA
                  │
                  └─ 仍有 BLOCKER / MAJOR
                         ↓
Stage C：重新规划本章 + 整章重写（最多 1 次）
                         ↓
Reader Review #4
                         ↓
通过 ────────────────────→ 常规 QA
                         │
                         └─ 仍失败
                                ↓
status: retry_later
qa: failed
不得进入 ready
冷却后启动新一轮自动尝试
```

单次自动周期最多产生 4 个正文版本，禁止无限循环。

## 4. Stage A：局部修订

适用于 Reader 建议为 `revise`，且问题可以在不改变本章核心事件顺序的情况下修复。

读取：
- 当前草稿；
- 与当前草稿 SHA 对应的最新 Reader Review；
- `fix_required`；
- 必需的 Canon / Memory 片段。

只修改 `BLOCKER` 和 `MAJOR` 指向的问题。

不得：
- 顺手重写无关段落；
- 为迎合 MINOR 改动大量文风；
- 擅自改变下一章计划；
- 修改已发布事实或 Canon。

## 5. Stage B：整章重写

如果局部修订后仍存在 `BLOCKER` / `MAJOR`，放弃继续打补丁。

重新读取该章详细计划、Canon、当前状态和前文，用**新正文**完成同一章目标。

保留：
- 本章必须达成的剧情状态变化；
- 硬 Canon；
- 已发布事实；
- 人物知识边界；
- 必须推进/回收的伏笔。

可改变：
- 场景组织；
- 对话；
- 事件呈现顺序；
- 次要冲突；
- 进入与退出场景的方式。

## 6. Stage C：重新规划本章

如果整章重写仍失败，说明问题可能来自章纲本身。

Planner Repair 允许修改：
- 当前章详细章纲；
- 当前章内部事件顺序；
- 非硬性的未来 5–10 章粗纲中与本章直接冲突的部分。

Planner Repair 不得修改：
- `bible/` 硬 Canon；
- 已发布章节事实；
- 用户明确指定的硬节点；
- 已确认终局。

冲突优先级仍以 `AGENTS.md` 为准。未来粗纲与 Canon 冲突时，应修改粗纲，不得修改 Canon。

## 7. retry_later 与冷却

Stage C 后仍有 `BLOCKER` / `MAJOR`：

- 当前草稿保留在 `chapters/draft/`；
- Front Matter 标记 `status: retry_later`、`qa: failed`；
- `memory/revision_state.yaml` 中增加 `retry_cycles`；
- 根据 `config/novel.yaml -> reader_review.retry_cooldown_hours` 设置 `next_retry_after`；
- 冷却期间 Revision Agent 不得继续修改该章；
- 不进入 `ready/`；
- 不更新为已发布事实；
- 冷却结束后重置本周期 rounds，并重新从“重新规划本章”开始尝试，不开始下一章。

`retry_later` 是自动系统的安全停机状态，不等于需要人工处理。

## 8. 保守重写模式

当 `retry_cycles >= config/novel.yaml -> reader_review.safe_mode_after_retry_cycles` 时，设置：

```yaml
safe_mode: true
```

保守模式目标不是写得更花，而是**减少失败变量**：

- 不新增非必要世界设定；
- 不新增非必要人物；
- 不额外埋新伏笔；
- 不使用复杂时间跳跃或多重误导；
- 减少同章场景数量；
- 优先明确因果链和人物动机；
- 只完成当前章必须达成的状态变化；
- 可以简化非硬性的未来粗纲，使其重新符合 Canon 和当前人物状态；
- 仍必须满足正常文风与可读性要求，保守模式不是流水账许可。

通过 Reader Gate 后自动退出 `safe_mode`，并把 `retry_cycles` 重置为 0。

## 9. Reader Review 的影响边界

- Writer 创建**下一章**时不得读取上一章 Reader Review；
- Revision Agent 只读取当前章、当前正文 SHA 对应的 Review；
- Review 意见不得直接写入长期 `memory/`；
- 只有修订完成并通过审查后的正文事实与状态变化才能更新 Memory；
- 历史 Review 只用于审计，不作为长期创作指令。

## 10. 唯一 Audit 单轮可连续推进多个阶段（2026-10-19）
当前 Revision 是唯一 Audit 定时任务内的内部修订阶段，不存在独立 Revision 定时任务。以 `docs/combined_audit_protocol.md` 为先，按章节数字顺序处理积压，同轮允许完成 Reader → Stage A/B/C 修订 → 绑定新 Git blob SHA 的独立双遍 Reader 复审 → Continuity/Style QA → Memory/计划 → 精确版本结构验证与候选 ready 迁移。正文每次改变后旧版 Review 立即失效；同轮必须重新核对新 SHA，不能跳过新审。仅修改 `fix_required` 中的 BLOCKER/可执行 MAJOR，不因 MINOR 改正文。修订次数上限与 retry_later 冷却保持不变。遇 GitHub 安全拦截或 CI 阻塞时保留 draft，不自动停用 Writer/Audit 定时任务。

## 11. 发布门槛

一章只有同时满足以下条件才可进入 `chapters/ready/`：

1. 最新 Reader Review 中 `BLOCKER == 0`；
2. 最新 Reader Review 中 `MAJOR == 0`；
3. 常规 Continuity QA 通过；
4. Style QA 通过；
5. Memory 已更新到本章结束状态；
6. Front Matter 为 `status: ready`、`qa: pass`。

任何自动修订次数用尽都不能绕过这些门槛。
