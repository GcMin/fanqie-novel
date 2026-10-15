> **2026-10-15 更新：当前只使用 Writer 与唯一 Audit 两个定时任务。下文多会话 Reader/Revision/QA 均归并为 Audit 内部不同轮次的阶段；具体执行优先遵守 `docs/combined_audit_protocol.md`。GitHub 写入受阻不可自动暂停任务。**

# 每小时小说写作：分会话协作协议

生效：2026-10-14；依据用户最新要求，`config/novel.yaml -> automation.mode: split_roles`。本协议只改变执行分工，不修改 Canon、主线硬节点、质量门槛或平台发布流程。

## 1. 谁写、谁审

| 会话 | 唯一职责 | 可修改 |
| --- | --- | --- |
| Writer（每小时） | 按协议读设定与近期正文，完成详细章纲、连续性预检，首次编写**一个新的**章节正文 | `plans/chapter_NNNN_plan.md`、`chapters/draft/NNNN.md`（新建时） |
| Reader（独立） | 对最新待审原稿或修订稿进行普通读者 Pass A / Canon Pass B，留可操作意见 | `reader_reviews/NNNN_<sha8>.md`、`memory/reader_state.yaml` |
| Revision（独立） | 仅修改 Review 指明需要修订的既有草稿；正文一变等待新 Review | 当前已存在 draft、`memory/revision_state.yaml` |
| QA + Memory + Publish Gate（独立） | Reader BLOCKER/MAJOR 为 0 后执行 Continuity / Style QA；同步长期记忆、计划、摘要；校验并移入 ready | QA、memory、plan、arc/volume、相应 ready/draft |
| Publisher（服务器） | 只使用 ready，平台发布核验成功才归档 published | 发布器日志与已发布快照 |

Writer 不读取历史 Reader Review；不生成 Review、QA 结果、Memory 更新或将章节置于 ready，也不回写既有草稿。Reader/Revision/QA 不擅自创建新章正文。不同任务不得并发覆盖同一文件。

## 2. Writer 每小时真实创建新章

1. 重新读取 `AGENTS.md`、`config/novel.yaml`、`docs/ai_reading_protocol.md`、Bible、人物卡、当前卷与 arc、长期 Memory、相关伏笔与时间线、最近十章摘要和最近五章正文。
2. 按 `published/`、`ready/`、`draft/` 的实际数字章名取最大现有章号 N，下一新章为 N+1；不得因 `reader_state`、`revision_state` 游标落后而重复创作 N。
3. 优先使用已审定的近期正文。若直接前章仅有 draft，则视作 **provisional**：新章详细计划写明 `depends_on_chapter: N`、`depends_on_source_sha: <40位 Git blob SHA>`、依赖的具体场景事实与不可先验确认的边界；新章草稿 Front Matter 同步保存这两字段。
4. 详细章纲必须包含目标、POV、开场、角色诉求、冲突、3–6个 beats、新信息与变化、伏笔和不可泄露秘密、结尾承接点、目标字数。再写完整首稿，标题不含第N章且至少5个非空白字符，字数按小说配置执行，每章有有效状态变化。
5. 完成后只保存计划与草稿，Front Matter 必须是 `status: draft`、`qa: pending`、`approved_at: null`、`publish_mode: draft`。不得宣称已经通过审查或被平台发布。GitHub 先检查当前分支 SHA，使用原子提交与非强制更新，不覆盖别人的同名文件。

## 3. 前章还在修订时如何衔接

允许 Writer 提前创作，但不允许其他会话把依赖未经核对的新章送进 ready。独立 Reader/QA 处理 N+1 时，须先确认 N 的最终标题/正文与新章 `depends_on_source_sha` 所指临时文本是否在关键事实、时间、地点、人物知识和结尾状态上兼容。若 N 后续修订没有改变新章依赖的关键事实，记录兼容性判断；若确有变化，由 Revision 对 N+1 进行相应修订，重新 Reader，而非让 Writer 返回重写旧章。

Writer 如发现前章仍在 retry_later 或严重冲突，不能自称前章已被审核通过。不得编造人身危险、物证、社会部门结论来替代前章尚未确立的事实。

## 4. 审核与交付

Reader 依 `docs/reader_agent_protocol.md`；Revision 依 `docs/revision_agent_protocol.md`。每次修订后按新 blob 审查。QA/Memory 独立阶段在前章衔接验证、Reader BLOCKER/MAJOR 清零后，执行 `qa/continuity_rules.md` 和 `qa/style_rules.md`，再同步本章真实长期状态和计划表，不继承旧章 pass。

实际结构校验使用 `python -m publisher.check_local --repo .` 与必要的 `--candidate`；没有实际通过不标记成功。最终只把 QA/Memory/结构通过的正文移入 ready；平台发布后方可进入 published。CI 绿色不能替代文本审核。原有全部 `ready` 章节计划行、标题、pass 必须保留，不能为了写新章删掉待发布历史。

## 5. 自动化编排与异常

写作、Reader、Revision、QA/Memory/Publish Gate 可是不同小时任务。并发提交拒绝后重新获取远端版本；任何 Agent 不得 force push 或重置他人审查游标。每个会话只汇报自己**实际完成**的工作，其他阶段必须明确“待独立会话”。单个小时若发现下一章已经存在，则不重建，不修改现有正文，不冒充新章已生成。
