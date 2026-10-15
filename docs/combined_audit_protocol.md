# 双任务写作与审核修订规则

2026-10-15 起，GcMin/fanqie-novel 只使用两个 ChatGPT 定时任务。保留 automation.mode=split_roles。

1. Writer 每小时最多新建一个完整章节及详细章纲，不审核、不修订旧章、不更新 ready 或 published。
2. Audit 是唯一审核修订会话，每次尽可能逐章处理全部可安全推进的积压（Reader、Revision、新 SHA 复审、Continuity/Style QA、Memory、ready），每章需要独立可核对的完整证据，不能跳过前章或强制通过：Reader 双遍审查 → 必要修订 → 新 SHA 再审 → Continuity/Style QA → Memory 和计划更新 → ready。不得自己写新章，不发布番茄。
3. Reader 第一次只读当前章、前面正文、近期摘要及文风（Pass A），完成之后再读 Canon、人物知识、时间线、伏笔、卷/弧与依赖关系（Pass B）。报告绑定实际 Git blob SHA，存放 reader_reviews/NNNN_<sha8>.md。老版本评论不能用于新正文。
4. BLOCKER/明确可操作 MAJOR 才触发修订，MINOR 只记录。每章局部修订次数仍按配置控制；正文一变立即针对新 SHA 重新 Reader，旧结果失效。可在同次执行完成安全复审，不必人为等待下一轮。修订次数和 retry_later 遵循 config/novel.yaml；不能 force pass。
5. 以草稿章节数字升序处理尚未完成的最早章节，跳过已在 ready/published 的残留稿；不凭 reader_state 游标判断实际章节是否审核。第137章旧 orchestrator_self_review 不自动视为独立审查。前章的 provisional 依赖及 SHA 变化须核实关键事实，不可把未审草稿当 Canon。
6. 只有最新 SHA 的 Reader BLOCKER=0、MAJOR=0，且连贯性、文风、章间依赖、结构和长期 Memory 同步均真实通过时才可进入 ready。QA 绿灯不能由 CI 绿灯替代。
7. GitHub 写入必须基于最新 main HEAD，非强制，带 expected SHA；遇冲突重新读取。写入受阻、工具安全检查、网络或 CI 失败时，不得自动暂停、禁用、删除 Writer 或 Audit 任务，也不得另建任务。保留失败状态，等待下一次小时任务自动重试。不得虚报提交成功。
8. Linux 番茄发布器不是 ChatGPT 定时任务，只可读取 ready；审核任务不操作平台。

## 2026-10-15 补充：批量积压处理和放行
- 本审核任务是唯一审核+修订+QA+Memory+ready 的定时任务。用户要求立即处理所有已通过章节进入 ready，不能只交付 Reader 评论；允许同次执行多个章节和阶段，但必须按章号顺序执行真实 QA、同步 Memory 与计划、结构校验后才批准。
- 新写章节持续由唯一 Writer 任务负责；不另建其他任务。
- GitHub Actions 的 publisher-check.yml 对 ready 变化会进行实际结构检查；仅当其明确匹配目标 Git commit 并成功时，才报告结构通过。失败时不得虚报 ready 已验证，修复或回滚。
