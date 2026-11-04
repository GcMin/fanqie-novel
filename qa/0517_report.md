# 第517章独立 Continuity / Style / Meaningful QA｜2026-11-04

- 检查原稿 `chapters/draft/0517.md` Git Blob `26db97c0d41edb1e1d0571e09b301ba344ea8ccf`，独立Reader先Pass A后Pass B：0 BLOCKER / 0 MAJOR / 2 MINOR，keep/none；正文和原稿Front Matter均无需修订，Review与真实SHA绑定。
- **序号/标题/字数 PASS**：517、标题“纸件出了单位门，孩子还在楼上等”与Front Matter及详细章纲一致；正文剔除空白及4个`***`场景分隔符的项目有效字符为3263（包含分隔符的纯去空白统计为3275），均在硬范围2300—3800。
- **前章依赖 PASS**：`chapters/ready/0516.md` 正式Blob `0d3c1ae4bb40787bea5bb6f0eb78894a8a2f9edd`与本章`depends_on_source_sha`和详纲完全匹配。第516章Day380 07:11交班、第517章Day380 09:14开始，两章人物时间及已证状态一致；没有待比较的旧临时前章SHA事实差异。历史137→148旧稿SHA非本章依赖，未凭旧SHA机械阻断，也没有援引未经核验的旧版本事实。
- **Continuity PASS**：2019同笔关联重拟稿前章仅可证原单位内部核发岗交出与内设收发转运岗接入；本章另新授权有责双岗核对同一原业务组合和新索引，确认原单位对外交出、外部承运独立接入。不能由承运接入推目的端实收、历史自然人收到答复、2016封内物或2022真实字节同一。F003仅限此新实证，F008/M004/M005不确证。
- **现代服务/知识边界 PASS**：Day380 20:27蒋宜只扫码进入楼、未到三楼，班级模板错写孩子已交；方老师仍实际守护黎苗，21:17由有权人员引导母亲抵达，21:23依原有效授权真正核身份交接、21:38母女真正离楼且回拨。错误自动记录保全撤回外部断言，运营根因/其他同类未核；夜班中心仅联动及分源记录，不擅改门禁或代机构确认系统全面修复。第516章南砂路28号院仅证明特定时段特定助行车可通过，Day381施工仍在、逐班核通道；陶佩云原机真领临机已还而长期适配未知。
- **Style PASS**：档案双端排除错号的对话与画湿蓝船、母女互相数画中人、方老师护人等具体行为支撑节奏；无元叙事或人物异常越权。旧档范围重复及相近章尾双线留白为MINOR，不因MINOR修稿。
- **Meaningful Change PASS**：2019原单位外部承运交接新增原始双端证据；孩子从后台误标已接领且实体仍在画室，变为实际有责身份核验、监护人接领并离楼；保留误映原记录供运营方核查。
- **Memory/Plan候选**：按正文同步本章摘要、人物、知识、世界、关系、时间线、F003和当前弧；仅新增517计划，全部已ready计划保持原状。
- **结构门禁**：本篇内容QA PASS不能替代结构CI。在与当前Git树精确匹配的候选Commit上，`python -m publisher.check_local --repo .`及结构单测必须真实SUCCESS，之后方可用`expected_sha`、`force:false`更新main并将draft原子迁ready。候选态不冒称结构校验已通过。

## 第517章精确结构CI SUCCESS后已正式ready｜2026-11-04
- 放行Commit `396de5fdf42ba1f8b5745f5c4003bca71f3c283a`，Git Tree `8ed4688436241940e47ccc384646267518e887cd`，父main `3cb4ce69d3e2777225c13880b789da461ea21781`。
- 候选分支 `audit/ready-0517-20261104-1810` Actions `41813217888` head_sha精确匹配放行Commit，状态completed/**SUCCESS**；结构单元测试和 `python -m publisher.check_local --repo .` 两步骤分别SUCCESS。
- 确认候选CI通过才使用expected_sha=`3cb4ce69d3e2777225c13880b789da461ea21781`、force:false将main非强制快进至该Commit；main同SHA Actions `41813326848` completed/**SUCCESS**，两步结构校验同样SUCCESS。
- 正式ready `chapters/ready/0517.md` Git Blob `85b841af1ce5bed58c7f758fc4abcc4cd6cc4cbb`，原draft与ready在同一Git Tree原子迁移。Reader0/0/2、独立内容QA PASS，全文无修订，长期Memory与计划同期更新；未改Canon/published，不发布番茄。
