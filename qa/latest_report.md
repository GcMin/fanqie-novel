# Latest QA Report

## Chapter

50《旧号新号》

## Result

**PASS**

## Baseline Check：第1–6章

**PASS**

- 本轮开始前重新核对第1–6章发布门：`plans/chapter_plan.csv`中第1–4章保持`completed / pass / published`，第5–6章保持`completed / pass / ready`。
- `chapters/ready/0005.md`、`chapters/ready/0006.md`均保持`status: ready / qa: pass`；第6章最终Reader Gate仍为0 BLOCKER / 0 MAJOR，既有Stage A修订、Reader、QA与Memory状态一致。
- `chapters/draft/`在开始本章前无第1–6章遗留草稿；未发现需要优先返修的状态冲突。
- 因基线一致，本轮没有修改任何已发布Canon，也没有回写第1–6章正文。

## Required Reading / Protocol

**PASS**

本轮在规划第50章前重新读取并以其为约束：

- `AGENTS.md`
- `docs/ai_reading_protocol.md`
- `config/novel.yaml`
- `bible/premise.md`
- `bible/main_outline.md`
- `bible/world.md`
- `bible/style.md`
- 周衡、夏宁、梁策角色Canon
- `outlines/volume_03.md`
- `outlines/arcs/arc_current.md`
- `plans/chapter_plan.csv`
- 当前`memory/current_arc.md`、人物/关系/知识/世界状态、伏笔、时间线、Reader/Revision State
- 最近十章摘要0040—0049
- 最近正文0045—0049
- Reader / Revision / Continuity / Style协议

## Planner

**PASS**

已建立`plans/chapter_0050_plan.md`。

本章目标不是再次解释第49章六项沿革字段，而是把正常正式地址变更从“知道字段”推进到“知道如何合法定位来源”：

1. 仅沿第49章已知来源文书“东桥片区门楼牌调整通知2018年第27批”进入历史门楼牌沿革索引。
2. 用花枝巷17号→槐北路112号附1回查目录结构。
3. 从同批次随机选择另一条普通记录“纸坊巷8号→槐北路108号”，再由现行地址卡独立反核，避免拿一个已知答案自证。
4. 明确同一批次可以包含不同门牌处置类型，不能以“同批次”替具体条目补变更原因。
5. 取得“未知来源文书时，以行政区片+历史图幅/旧道路范围+大致年代先申请候选索引”的正常入口。
6. 章尾只把旧B口行政区片与历史图幅号填进未提交草稿，不输入“永安里”或“6栋201”，不提前查看第51章结果。

## Continuity Precheck

**PASS**

- 时间从第49章Day 4约00:10自然续到00:12—00:35，仍是第三夜班。
- 花枝巷只作为正常控制样本；新增纸坊巷记录同样只是普通地址沿革交叉样本，不构成异常事实。
- `BK-JBS-160114-03 / S2-07`继续保持待正常实物盘点，没有半夜强行获得结果。
- Day 3 23:08商业街井盖工单最终现场结果仍未记录，本章没有倒写为已闭环。
- F008仍只有王启明一个明确具体事件记忆冲突样本。
- M003、永安里6栋201正式历史链、历史处置人员、完整失址机制、工单系统来源与周衡保留记忆原因均未提前揭示。
- 夜间账号只读取目录和现行基础沿革，不绕权限打开历史底册影像。

## Writer

**PASS**

- 最终有效字符：**2764**。
- 位于`config/novel.yaml`优选区间2600—3400内，也满足2300—3800硬范围。
- 本章围绕单一动作链推进：来源文书进入目录 → 花枝巷回查 → 第二普通样本交叉 → 阅读历史资料定位说明 → 建立旧B口未提交申请草稿。
- 没有通过重复上一章六项字段或反复总结同一结论凑字。
- 有明确Meaningful State Change：正式地址调查从一个正常控制样本推进为两条普通记录可重复验证的索引方法；未知来源资料获得合法的图幅/年代入口。

## Reader Review Round 1

Source SHA：`3d2b230430f69d3854cce49c0ca364024adbae4d`

- BLOCKER：0
- MAJOR：1
- MINOR：1
- recommendation：`revise`
- required_action：`local_revision`

### MAJOR

章尾申请页先写“行政区片和时间范围”为必填项，随后时间范围为空却写“提交”按钮已经亮起，界面规则自相矛盾。

### MINOR

中段对正式地址索引、实体旧牌与口头称呼的边界有少量再次解释，但第二普通样本承担实际交叉验证功能，不要求自动修订。

## Editor / Revision

**PASS**

按Stage A只修Reader指定的MAJOR，没有扩大改稿范围：

- 保留“年代尚未确定、申请未提交”的剧情不变。
- 将章尾按钮状态改为：时间范围未填写时“提交”按钮仍为灰色且不可用。
- 未因唯一MINOR重写其他段落。

修订后Source SHA：`2d8008c0dcc5b391d6a0ac610feb816405e84a34`。

## Reader Review Round 2

**PASS**

- BLOCKER：0
- MAJOR：0
- MINOR：1
- recommendation：`keep`
- required_action：`none`

唯一MINOR仍是中段证据分层有轻微重复强调，不影响阅读、因果或角色可信度，按协议不继续修订。`memory/revision_state.yaml`已恢复`idle`，记录本章1次local revision、2次Review。

## Continuity / Knowledge / Institution QA

**PASS**

### 时间

- Day 4 00:12—00:35连续成立。
- 没有把目录阅读、跨年档案核验压缩到不合理的几分钟内完成；本章只处理目录级信息和现行地址卡。

### 人物知识边界

- 周衡只根据第49章已知来源文书和本章实际看到的目录说明形成方法总结。
- 夏宁负责来源、目录、权限和申请条件，不凭空给出历史答案。
- 梁策继续只守推论尺度，阻止“同批次=同原因”“图幅=地址证明”。
- 纸坊巷案例没有被任何角色写成永安里机制类比证据。

### 制度 / 权限

- 历史底册影像按钮保持不可访问；夜间账号仅看目录/现行基础沿革并可准备目录范围申请。
- 未知来源资料按行政区片、历史图幅/旧道路范围和大致年代缩小候选范围，符合本章建立的普通档案流程。
- 时间范围作为必填条件未填写，因此旧B口申请只保存草稿，未提交。

### 证据边界

- “纸坊巷8号→槐北路108号”只证明索引路径可以重复，不证明与花枝巷具有同一具体变更原因。
- 正式地址沿革索引不负责证明居民口头称呼或旧实体门牌是否仍存在。
- 旧B口历史图幅只是定位条件，不是正式地址证明。
- 未输入或查询“永安里6栋201”，F003只推进调查方法；正式地址层仍为“未取得独立来源”。

## Style QA

**PASS**

- 无章节编号、作者说明、Reader/QA等元叙事泄漏进正文。
- 对话具有角色区分度，资料场景由实际点选、核对、反问承载，没有整章写成档案说明书。
- 没有把普通行政流程神秘化，也没有用抽象悬疑句替代具体动作。
- 未发现需要Reader Gate之外继续自动修订的模板化重复。

## Memory Updater

**PASS**

已更新：

- `memory/chapter_summaries/0050.yaml`
- `memory/current_arc.md`
- `memory/character_state.yaml`
- `memory/knowledge_state.yaml`
- `memory/world_state.yaml`
- `memory/foreshadowing.csv`（F003推进至50；F008明确仍仅王启明）
- `memory/timeline.csv`（新增T053）
- `memory/reader_state.yaml`
- `memory/revision_state.yaml`
- `plans/chapter_plan.csv`
- `memory/global_summary.md`已在第50章节点重新压缩为“第50章后”版本。

`memory/relationship_state.yaml`本章没有出现关系状态变化，因此按协议不做空更新。

## Publish Gate

**PASS**

- 最终Reader Gate：0 BLOCKER / 0 MAJOR。
- QA：pass。
- Memory：已推进至第50章。
- `plans/chapter_plan.csv`：第50章已为`completed / pass / ready`。
- 最终正文已进入`chapters/ready/0050.md`，Front Matter为`status: ready / qa: pass / publish_mode: ready`。
- `chapters/draft/0050.md`已在Ready副本创建后删除，不保留双份草稿。
- 第51章《图幅索引》仍保持`planned / pending / blocked`，本轮没有编写下一章。
- 未自动发布到番茄。
- 未修改或覆盖`chapters/published/`中的任何正文。

## Next Allowed Entry

第51章只能沿第50章已经形成的“行政区片 + 历史图幅 + 年代”入口，先确定合理时间范围并提交目标区片的历史门楼牌目录范围申请。不得用“永安里6栋201”做无来源全文搜索；若目录返回空白、不完整或只覆盖部分年代，只能记录对应范围的阴性/缺口，不能直接写成历史不存在，也不能提前进入M003人员确认。
