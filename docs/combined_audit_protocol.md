# 双任务写作与审核修订规则

2026-10-15 起，GcMin/fanqie-novel 只使用两个 ChatGPT 定时任务。保留 automation.mode=split_roles。

1. Writer 每小时最多新建一个完整章节及详细章纲，不审核、不修订旧章、不更新 ready 或 published。
2. Audit 是唯一审核修订会话，每小时最多推进一个章节的一个阶段：Reader 双遍审查 → 必要修订 → 新 SHA 再审 → Continuity/Style QA → Memory 和计划更新 → ready。不得自己写新章，不发布番茄。
3. Reader 第一次只读当前章、前面正文、近期摘要及文风（Pass A），完成之后再读 Canon、人物知识、时间线、伏笔、卷/弧与依赖关系（Pass B）。报告绑定实际 Git blob SHA，存放 reader_reviews/NNNN_<sha8>.md。老版本评论不能用于新正文。
4. BLOCKER/明确可操作 MAJOR 才触发修订，MINOR 只记录。每轮最多一次阶段性修改，正文一变就结束，下一轮重新 Reader。修订次数和 retry_later 遵循 config/novel.yaml；不能 force pass。
5. 以草稿章节数字升序处理尚未完成的最早章节，跳过已在 ready/published 的残留稿；不凭 reader_state 游标判断实际章节是否审核。第137章旧 orchestrator_self_review 不自动视为独立审查。前章的 provisional 依赖及 SHA 变化须核实关键事实，不可把未审草稿当 Canon。
6. 只有最新 SHA 的 Reader BLOCKER=0、MAJOR=0，且连贯性、文风、章间依赖、结构和长期 Memory 同步均真实通过时才可进入 ready。QA 绿灯不能由 CI 绿灯替代。
7. GitHub 写入必须基于最新 main HEAD，非强制，带 expected SHA；遇冲突重新读取。写入受阻、工具安全检查、网络或 CI 失败时，不得自动暂停、禁用、删除 Writer 或 Audit 任务，也不得另建任务。保留失败状态，等待下一次小时任务自动重试。不得虚报提交成功。
8. Linux 番茄发布器不是 ChatGPT 定时任务，只可读取 ready；审核任务不操作平台。
