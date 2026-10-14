# 每小时写作编排协议

> **模式提示（2026-10-14）：**当前 `config/novel.yaml` 使用 `split_roles`，各会话实际分工以 `docs/writing_roles.md` 为准。本文保留供历史 `orchestrated` 模式参考，不要求 Writer 自行审稿或修改 Memory。

生效：2026-10-14。用户授权检查并修改阻塞规则。模式由 `config/novel.yaml -> automation.mode` 决定。

## 1. 单一负责人，角色串行，不按小时拆阶段

`orchestrated` 模式由主续写任务完成 Planner、Precheck、Writer、Editor、Reader、Revision、QA、Memory 和 Publish Gate。保留各角色的检查标准，不把角色分离误作必须等待另一条定时任务。

一轮最多创建一个以前不存在的新章。恢复旧章、审核旧章、修订旧章、补 Memory 或转 ready 都不占新章名额。旧章真正完成后，本轮仍可新写下一章并尽量完成全流程。不得无原因停在“已写草稿，等待下小时审查”或“已 ready，等下轮才写”。

旧独立 Reader/Revision 任务在此模式下不进行仓库写入；它们仅检查模式后退出。需要切回独立任务时由用户明确切换配置与任务提示词，不能自动双主运行。

## 2. 每次先定位真实进度

1. 获取 main 最新提交及目录，只认数字章名，不认模板。
2. published 为已发布快照；ready 为待发布成稿。两者都不是平台等待期间阻止续写的理由。
3. 检查所有未交付章节，优先处理章号最小的尚未创作通过章，不再只挑最大 draft 而漏掉旧阻塞。
4. 已有同号 ready/published 时，只有核对标题、正文与审查证据一致才清理残留 draft；不同正文不得直接删。
5. `reader_state`、`revision_state` 和 `writing_state` 只是缓存。若游标仍在已完成上一章，初始化下一章自己的轮数、源版本与待审状态；这属于正常前移，不是违规回退。不得继承上一章的 pass。
6. 不能仅因 cache.current_chapter 不等于草稿章号就结束任务。真正冲突应记录所涉及文件和版本，并按事实修复缓存。

每轮读取 AGENTS、配置、本协议与原读取协议。最近正文按章节顺序读取，最近五章优先取其有效成稿；若有第5节允许的“创作通过但待交付”草稿，须核对完整证据后将其纳入最近窗口，不能跳过它从更旧正文续写。

## 3. Reader 与有限修订

继续执行 `docs/reader_agent_protocol.md` 的 Pass A、Pass B 和严重度标准。同会话执行须记录 `reviewer_mode: orchestrator_self_review`。这不是独立盲审；Pass A 不得用未来答案为正文的含混辩护。

优先复用与当前标题/正文完全匹配的已有 Review；没有时立即执行，不等待独立时钟。Review 仍存入 `reader_reviews/NNNN_<source_sha8>.md`，保留原草稿 blob SHA。

BLOCKER/MAJOR 按局部修订一次、整章重写一次、重规划重写一次的上限处理，总审查最多四次。正文一变，旧审查失效，必须重新读修改后的全文并产生新版本 Review。在同一主任务内可立即完成下一次复审，不再强制跨小时等待。到达真实质量失败上限才进入 retry_later 与配置中的冷却。

没有 Review、旧游标、网络故障、CI 排队或暂时缺执行环境不是质量失败，不能消耗修订轮数，也不能触发六小时冷却。

### 版本绑定

不得只比较整个 Markdown blob SHA：Frontmatter 中 status、时间、计数等交付元数据变化会改变 blob，但不一定改变被审查正文。

新 Review/QA 建议同时记录 `source_sha` 与 `content_sha256`。后者按 UTF-8 的 `title.strip() + '\n\0\n' + body` 计算；body 去掉 Frontmatter 与一致的可选一级标题，统一 CRLF 为 LF，仅去首尾空白，不压缩正文内部空白。正文或标题变化必须复审；仅交付元数据变化，可读取原审查 blob、比较标题与正文后记录对应关系，不凭口头声称复用。

## 4. QA 与 Memory

Reader 的 BLOCKER/MAJOR 为零后仍需做独立阶段的 Continuity/Style QA，核查时间、空间、知识、伤势、物品、状态变化、长度与标题。

发布结构检查不是内容审查。机器不能凭一份 pass 字段替代逐项阅读。QA 报告写清源版本、实际检查、问题及结果。

更新本章摘要与必须的 Memory、时间线、伏笔、当前弧、计划表。没有事实变化的关系/世界条目可注明核对后无需改动。只有经过审查和 QA 的正文事实进入长期 Memory，审稿意见留在 Review。

## 5. 创作门与交付门分离

创作门通过必须同时有：本章匹配正文的 Reader 通过、Continuity/Style QA 通过、Memory 完整同步、标题与字数符合规则。缺一项仍阻止依赖它的新正文，不允许跳过内容问题。

交付门另外要求结构校验通过并将文件从 draft 移到 ready。仅因无法执行命令、CI 暂未回执或仓库临时写入失败，不把创作通过章改成质量失败。

无法完成交付时，保留 draft 不发布，并在本章摘要写明真实 `creative_gate: pass`、`publish_gate: blocked`、具体原因与 Reader/QA/源版本证据。每轮先重试交付；在全部前置创作通过、Memory 一致的前提下，最多允许累计 `max_approved_unready` 章等待交付。达到上限后优先修复，不无限囤积。

实际字段/计划错配导致校验失败应立即修复，不能笼统归为基础设施故障。已通过的最近正文可以支撑下一章连续性，但不能被标为平台 published。

## 6. 校验当前输入，不校验另一个 main

本地或容器已拿到完整快照时运行：

```sh
python -m publisher.check_local --repo .
```

草稿 Reader/QA/Memory 已完成、计划已有真实 completed/pass 记录后，可在移动前预检：

```sh
python -m publisher.check_local --repo . --candidate chapters/draft/NNNN.md
```

候选预检仅在临时目录改变 status 以模拟 ready；它不改源文件、不写 QA、不移动章节，且拒绝 qa 非 pass 的候选。输出保留输入 SHA-256 清单。通过后核对原文件未变再进行原子交付。

GitHub Actions 对触发提交的 checkout 执行同一离线检查及回归测试。原 `python -m publisher check` 会同步服务器仓库，不作为待提交工作树的证据。只看到旧提交的绿色 CI 不能批准新正文。

仅 GitHub connector 可用而没有容器时，可在检查分支构建不改变真实 main 状态的候选快照，核验该提交的 CI，再用带 expected SHA 的提交合并；不得先把未审查草稿放到 main/ready 来触发检查。

## 7. 并发、失败与重试

只由主任务修改正文、QA、长期 Memory 与发布门状态。GitHub 多文件修改优先一个 tree/commit，并使用 expected main SHA 的非强制 ref 更新。主分支变化时重新读涉及文件，重新计算差异，不强推、不覆盖他人结果。

同一主任务可能重入时以远端版本为准，最多新建一章，提交被拒绝不盲目重放。未来粗纲不得占用实际章号或替代真实正文。

写入失败保留实际完成阶段；下轮从证据恢复，不能报告“已写入”。不自动停用定时任务，不把正文问题交给用户人工审稿，确需修改硬 Canon 才请求确认。

## 8. 每轮报告

报告本轮修复或完成的旧章、唯一新章、Reader/QA/Memory/交付状态、真实阻塞原因和对应提交。没有完成的新章节不得宣称已完成。用户可从提交验证，不重复输出整章正文。
