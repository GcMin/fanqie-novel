# Latest QA Report

## Chapter

18《他们正在忘记》

## Baseline Check

PASS

- 第1–2章仍位于 `chapters/published/`，Front Matter 为 `published / pass`。
- 第3–6章仍位于 `chapters/ready/`，Front Matter 为 `ready / pass`，`plans/chapter_plan.csv` 对应状态为 completed / pass / ready。
- 本轮开始时 `chapters/draft/` 仅有模板与 README，没有第1–6章残留草稿。
- `memory/chapter_summaries/` 存在第1–6章摘要，既有 Reader Review 文件也覆盖第1–6章；当前长期 Memory 已推进到第17章，没有发现需要先修复的第1–6章冲突。

## Planner / Continuity Precheck

PASS

- 已创建 `plans/chapter_0018_plan.md`，本章只使用王启明一个已有明确历史行为记录的外部知情者作为认知核对样本。
- 王启明在第8章确实亲手发现并拍摄“13屋面”旧钥匙；钥匙一直按梁策要求留在正常青梧苑门岗旧钥匙柜，具备重新现场核对条件。
- 承接第17章 Day 2 约04:34：04:23第一版打印为13栋，04:30第二版为12栋，周衡/梁策/夏宁当前都仍记得这一对照。
- 预检明确禁止集体失忆、禁止提前解释失址机制、禁止把任何媒介写成绝对安全，也不提前触发第19章第二张工单。

## Reader Gate

PASS

- 第18章草稿 SHA：`9718e3287bfdaf82439706b5452d490e7bcad2ab`。
- Reader Review：0 BLOCKER / 0 MAJOR / 2 MINOR。
- `recommendation: keep`，`required_action: none`。
- 两项 MINOR 分别为“一张还没有”的过渡句略带写作技巧痕迹，以及章尾总结句略有作者式收束感；均不影响理解、逻辑或人物可信度，按协议不触发自动修订。
- 本章无需 Stage A / B / C Revision，正文保持 Writer 版本进入常规 QA。

## Continuity

PASS

- 时间从04:34自然推进到04:36–04:51，没有无解释跳时或换场。
- 04:23/04:30两版LJ-150907-0041打印状态保持一致，没有把第17章已经发生的电子源变化重置。
- “13屋面”钥匙仍在正常青梧苑门岗旧钥匙柜；01:49旧照片、04:41实体读数、04:44新照片形成可核对链条，物品位置连续。
- 王启明只出现一个具体事件记忆缺口：把此前钥匙记成12屋面并不记得01:49拍照；他没有被写成忘掉整晚、忘掉所有13栋事实或身份关系。
- 周衡、梁策、夏宁本章结束时仍分别记得三项核心事实，并在04:48独立写下即时记忆记录；没有违反“不要让全部角色同时失忆”的章节约束。
- 夜班疲劳、普通记错等正常解释仍保留；正文只确认“记忆与本人记录/当前实体不一致”，没有提前解释原因。
- 青梧苑地下2015纸质资料仍未开启，明确等待约07:30白班工程主管按正常手续处理。

## Style

PASS

- 开场直接由王启明误称“12屋面”进入新冲突，没有复述第17章全文。
- 证据链通过电话、现场读标签、聊天记录、新照片和独立书写等动作推进，避免用旁白讲世界规则。
- 夏宁继续负责压缩变量与保存来源，梁策继续限制风险/结论，周衡负责具体记录，人物语言指纹保持区分。
- “够我们害怕，不够我们立法”“先别自己补”等对白承担人物和方法功能，不是说明书式解释。
- 环境描写极少且服务于现场听感/设备状态，没有为了字数补景。
- Reader指出的两个MINOR没有达到自动修订阈值，不扩大改稿范围。

## Length

PASS

- 第18章：2620 个有效中文字符，位于优选区间 2600–3400。

## Meaningful State Changes

PASS

- 第一次出现既有知情者的具体事件记忆与其本人聊天记录、当前实体证据同时冲突。
- 王启明当前仍能读出13屋面，但缺失01:49亲手拍摄该照片的事件记忆，并一度稳定把标签记成12屋面。
- 风险由“档案内容会变化”升级为“人员认知也可能出现不稳定”，但范围严格限制在单一样本。
- 周衡、梁策、夏宁新增“给当下记忆留时间与个人来源”的处置办法，并将三份04:48即时记录分开保存。

## Memory / Planning

PASS

- `memory/chapter_summaries/0018.yaml` 已创建。
- `memory/current_arc.md`、`memory/character_state.yaml`、`memory/knowledge_state.yaml`、`memory/world_state.yaml`、`memory/timeline.csv` 与 `memory/foreshadowing.csv` 已更新到第18章结束状态。
- F002与F005完成第1–18章、15–18章阶段性回收；新增F008承接“人员具体事件记忆与保留记录冲突”的长期风险，不提前定义触发规律。
- `plans/chapter_plan.csv` 已将第18章标记为 completed / pass / ready，第19章《第二张工单》仍保持 planned / pending / blocked。
- `memory/reader_state.yaml` 已指向第18章当前草稿 SHA 与对应 Reader Review。

## Result

PASS

## Publish Gate

满足进入 `chapters/ready/` 的条件：Reader Gate 0 BLOCKER / 0 MAJOR、Continuity QA PASS、Style QA PASS、Memory 与计划已更新。

本轮只允许将第18章从 `chapters/draft/` 移入 `chapters/ready/`；不执行番茄发布，不修改或覆盖 `chapters/published/`。
