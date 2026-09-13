# Latest QA Report

## Chapter

43《改名前照片》

## Baseline Check

PASS

- 本轮开始时重新核对第1–6章：`plans/chapter_plan.csv` 中第1–4章为 `completed / pass / published`，第5–6章为 `completed / pass / ready`。
- `chapters/published/` 当前包含第1–4章和README；`chapters/ready/` 当前包含第5、6章及后续已通过章节。第5–6章Front Matter与chapter plan保持ready/pass一致。
- 第6章最终Reader Review仍为0 BLOCKER / 0 MAJOR / 1 MINOR，既有Stage A修订、Memory与chapter_plan状态一致。
- 本轮开始时`chapters/draft/`只有模板与README，没有第1–6章遗留草稿。
- 因第1–6章Reader Review / QA / Memory / chapter_plan / 目录状态一致，本轮无需返修，允许严格只推进一个后续章节。

## Planner / Continuity Precheck

PASS

- 已重新读取`AGENTS.md`、`docs/ai_reading_protocol.md`、`config/novel.yaml`、Premise、主大纲、World、Style、周衡/梁策/夏宁人物卡、第二卷与当前ARC、`chapter_plan.csv`、当前Memory、伏笔、时间线、最近摘要及最近正文，并复核Reader/Revision、Continuity/Style QA协议。
- 新建`plans/chapter_0043_plan.md`；本轮只推进第43章《改名前照片》，没有继续写第44章正文。
- 第42章结束于Day 3约03:00，钱先生已由家属接走；本章明确第二夜班08:00正常交班、周衡白天休息、白天走档案审批、19:47进入第三夜班后再查看资料，避免人物连续超长工作。
- 本章目标限定为按正常项目档案权限调阅2016更名前改造影像，先核来源、页序、拍摄批次，再看具体图像；不得根据钱先生证词追历史人员，不得提前完成M003。
- 即使影像出现“永安里”，也只能作为历史公共导向设施证据，不得等同永安里6栋201正式地址证明。

## Reader Gate

PASS

- Draft source SHA：`77eac3c0663a423cd10ac507a76d486cc022620d`。
- Review：`reader_reviews/0043_77eac3c0.md`。
- 结果：0 BLOCKER / 0 MAJOR / 2 MINOR，`recommendation: keep`，`required_action: none`。
- MINOR 1：前半段卷封、移交、数字化副本、连续图号等档案元数据较密，但这些内容直接承担原图可信度和非临时拼入证明，不建议拆散。
- MINOR 2：中后段有短暂直接概括照片证明范围的句子，略接近证据总结口吻；篇幅短且随后立即转入DX-B-06行动，不触发Revision。
- 按Reader/Revision协议，只有MINOR且`required_action: none`时不做为了改而改的Stage A；本章直接进入QA。

## Continuity

PASS

- 第42章仍在第二夜班；第43章明确08:00交班、白天休息、19:47第三夜班开始，时间、疲劳与工作状态可衔接。
- 钱先生02:52已由家属陪同离站，本章没有恢复固定联络、P17/D-17实验或要求本人回站验证。
- 第42章只知道2016改造影像目录存在；第43章先取得白天正常审批后才实际查看内容，没有把未知档案内容提前写进角色知识。
- 2011旧导向图此前已出现B口附近“永安里”，本章新增的是独立2016改造前工程影像层，没有把旧证据包装成新发现。
- 影像登记表拍摄批次只到“2016年1月上旬、更名标识切换前”，正文明确单张无更精确日期，没有自行补日期。

## Knowledge Boundary

PASS

- 三人先核卷封、授权、登记表、纸卷号/数字化卷号及01—18连续页序，再按顺序看图；没有带着“永安里”答案先用OCR或关键词筛图。
- 第09张出现“永安里”后，角色才获得该信息；钱先生、青梧苑物业等未参与本章的人物没有被同步该知识。
- 郭铭明确纠正“DX-B-06是不是资产号”的推断：当前只能称改造项目拆改对象编号，是否对应长期固定资产及去向须等拆除清单/移交记录。
- 旧站务亭虽然进入影像，照片无可识别人员；正文没有利用钱先生“男性值班人员”证词追身份。
- F008仍只有王启明一个明确具体事件记忆冲突样本；本章纯档案/影像证据不新增F008。
- 永安里6栋201、M003、系统来源、周衡保留记忆原因和完整失址机制均未提前解释。

## Institution / Evidence Boundary

PASS

- 郭铭白天以正常项目档案用途申请目标卷，只读授权有明确范围和时段；正文没有获得整库搜索或无边界下载能力。
- 中心侧保留卷封、登记页、来源和只读引用，不把轨道原件随意复制为本地“万能证据库”。
- 页序/图号连续、归档/数字化来源都在正文中被核实，合理支撑照片不是本次协查临时拼入。
- 20:10后续申请只针对同一2016改造项目的拆除清单与移交记录，检索依据只有DX-B-06，没有泛搜“永安里”。

## Style

PASS

- 没有大段复述第35–42章异常证据；开场只交代交班、休息和授权成立本章前提。
- 档案调查主要通过打开页面、核页序、逐图查看、纠正编号性质等动作推进，没有把周衡写成长篇世界观解说者。
- “永安里”出现时人物反应克制；梁策“接方向。别接地址。”、夏宁守来源、周衡改记录措辞，角色声音和职责可区分。
- 章尾落在新的关联申请与普通工单提示，没有使用“真相更近一步”式万能悬念句。
- Reader的两项MINOR已记录，均不足以判Style失败或触发强制修改。

## Length

PASS

- Front Matter记录2967个有效字符，位于配置优选区间2600–3400内，低于3800硬上限。

## Meaningful State Changes

PASS

- ARC-004从“只有2016影像目录入口”推进为“目标原始影像卷已按正常权限调阅，并核清来源、页序与拍摄批次”。
- 独立2016改造前工程照片确认B口公共导向牌实际出现“永安里”，为F003新增一层不同于2011旧导向图和804旧照片的正常轨道资料证据。
- 登记表取得拆改对象编号`DX-B-06`，调查从地名/照片层推进到一个可按普通工程资料继续追踪的具体对象。
- 20:10只针对DX-B-06及同项目拆除清单/移交记录提交关联申请，形成第44章单一入口；当前仍无去向结果。

## Memory / Planning

PASS

- 已创建`memory/chapter_summaries/0043.yaml`。
- `memory/current_arc.md`、`memory/character_state.yaml`、`memory/knowledge_state.yaml`、`memory/world_state.yaml`、`memory/foreshadowing.csv`、`memory/timeline.csv`均推进到第43章结束状态。
- 本章没有新的稳定人物关系变化，因此`memory/relationship_state.yaml`按协议不做空更新。
- F003推进到第43章；F008保持第42章最后触及且继续只有王启明一个明确样本。
- `memory/reader_state.yaml`指向第43章Review；`memory/revision_state.yaml`记录本章0次局部修订、1轮Review并已回到idle。
- `memory/global_summary.md`在第40章完成最近一次十章节点压缩，第43章不重复重写。
- `plans/chapter_plan.csv`已将第43章标记为`completed / pass / ready`，第44章《拆牌清单》仍为`planned / pending / blocked`。

## Result

PASS

## Publish Gate Eligibility

PASS

第43章满足Reader Gate、Continuity、Knowledge Boundary、Institution/Evidence、Style、长度、Meaningful State Change与Memory同步要求，可进入`chapters/ready/0043.md`。进入ready时仅改变Front Matter发布门状态，不改正文内容；随后应删除对应draft。不得写入`chapters/published/`，不得自动发布到番茄。
