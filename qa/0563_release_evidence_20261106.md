# 第563章独立Reader、结构校验与正式ready放行证据｜2026-11-06

## 原稿到新SHA Reader
- 最初 `chapters/draft/0563.md` Git Blob `2e3c21cfcf8a88e7b32b7e15510ab6c8d282d0e4`，Reader `reader_reviews/0563_2e3c21cf.md` 先Pass A后Pass B：BLOCKER=0、MAJOR=1、MINOR=2，唯一MAJOR为第562章临时来源SHA过期。
- 第562章原临时草稿 Blob `564ab6dcc5293d57d3f5c7b5bde0e9c3cb12e66e` 和正式ready Blob `e08d3be9c94c546df361084aed6b10a91bddd69a` 的**标题和小说正文逐字一致**；差异仅在status、qa、approved_at、publish_mode等交付元数据。经具体比较确定第563章依赖的Day425新短住、合法移柜见旧水印与2019非身份散页另封记载均未被改变。
- Stage A实际修订Commit `eed679fb901ea8adca08793cce413888b4979af6`：只更新563草稿和详细章纲对正式ready SHA的依赖，小说正文0字更改；修订后真实Git Blob `54b2ed1cb3f90136d9c3ecc3f182b520923ad53b`。
- 对新SHA重新独立Pass A、Pass B，Review `reader_reviews/0563_54b2ed1c.md`：BLOCKER=0、MAJOR=0、MINOR=2，keep/none；旧Review不用于放行。
- 独立内容QA `qa/0563_report.md`：Continuity、Style、Meaningful Change均PASS，有效字数2965，标题和依赖一致，历史137→148旧SHA未被作为新事实直接依赖。Reader/QA与CI分别真实执行。

## 先精确结构门禁后迁ready
- 候选commit `d58fc441c20281cbce4ddb499b2382eb597e68de`，Git Tree `1988c399dfd08eaf100e2ca4ce1b629e66807b5d`；分支 `audit/ready-0563-20261106-1629`。
- 精确候选Actions Run `42188053937`：`completed/success`；Job `127793020809` 内离线结构单元测试 **SUCCESS**、`python -m publisher.check_local --repo .` **SUCCESS**。
- 经上述结构成功后，main以 `expected_sha=eed679fb901ea8adca08793cce413888b4979af6` 与 `force:false` 实际快进至同一Commit，main Actions Run `42188118795` 亦匹配相同SHA并 `completed/success`。
- 正式文件 `chapters/ready/0563.md` Git Blob `0315019d5a398f4078a7d62f667e998e214886ab`，`status: ready`、`qa: pass`，原draft 0563已删；依赖562正式ready Blob精确绑定。
- Reader状态、Revision状态、章节摘要、人物、知识、关系、世界、时间线、F003、当前剧情弧、章节计划均按最新563正文同步更新，原有ready计划行未覆盖。最末复核draft只有README和模板。
- 没有操作平台发布，不修改Canon、published正文或两个既有定时任务。

本文件归档**已发生**的commit、QA、CI和主分支更新事实，不冒充新一轮独立审查或替代其源文件。
