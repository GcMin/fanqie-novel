# 第284章《新纸印出的是旧路》独立 Continuity / Style / Meaningful Change QA（2026-10-26）

- Reader原draft blob `05f737ae95489f0a355a2f2f6e14ae7cb530d1a2` Pass A/B发现0 BLOCKER/1 MAJOR/2 MINOR。唯一必须修订的是杜宜初始计划Day148送旧书箱、但正文22:27误写“早已把书箱留在阅读室”，违反故事自身前后因果并牵连下一章Day148实际送达。
- Stage A仅局部改成“那箱旧书还放在家里，准备明早送去阅读室；她没有为了验机把行程交给街道”，准确有效字数3077→**3086**。修后全新Git draft blob `2732f603a1dff37feaef16fadf76cafd8ede30ee`，独立重新Reader Pass A/B：**0 BLOCKER/0 MAJOR/2 MINOR**，不沿用原评审；无其它正文重写。修后ready配送字段另生成Git blob `6730cb42df121b60c2a9bfc9f9cedf0d176a00e9`，Reader对象仍为draft的精确SHA。
- **Continuity QA PASS**：前章283最终ready blob `400b233a1f5df66a0bf9dd48eb3006fa8b1482b8`与本章Front Matter精确匹配。Day147 20:00第145夜班已开始；Day147 21:14新有责夜间路况检查，仅证明当时南侧既有公众人行路可用、旧站施工东门封闭；不能用Day147 09:25白班核验替夜班或次日批准。Day144 16:07北侧临时绕行失效，Day147 20:30设备新印D144旧图有据，Day144原印64中20实撤+另交1+43未知，新增设备纸张是另批、不能抵扣43。21:48先停首页、22:03发现最近使用仍可触发、22:21三个已知入口现场复核才可标本机已阻断；另两台B07/C12只是待核。
- **人物/知识/职责 PASS**：杜宜自己决定Day148搬书、不以当晚个人行程提供道路验收；小唐只能现场核街道公示和本机已知入口；余松按运营权限停模板并保日志，不对其他终端或民众旧纸作全召回承诺。罗谨本章无新查阅，1996个人历史回告与2018原索引实填行未知。F003有界、F008无新样本、M004/M005未证，前期137→138等变更未被用于本章推断。
- **Style QA PASS**：普通人的纸和具体设备入口支撑动作与角色对白；时间节点较密、结尾稍作点题计2 MINOR，不足以启动重写。**Meaningful Change PASS**：首次证明旧模板能在Day147被重新印成带当日页眉的新纸并真正阻断一台设备的全部三个已知路线入口，明确另外两台尚待核。
- **Front Matter/字数/标题 PASS**：284、卷6、ARC-054、标题及详细章纲同名；有效正文**3086字**在2300–3800硬范围与优选区间，正文不含内部标记；计划行须唯一保留且对应标题。
- **Memory**：summary/character/knowledge/world/relationship/current_arc/timeline/foreshadowing及计划均按修订后正文分别同步，原ready行保留。
- **Structural Gate**：内容QA通过不等于结构通过。候选提交必须在GitHub Actions精确SHA上取得包含单测与`python -m publisher.check_local --repo .`的SUCCESS，方能以`expected_sha`、`force:false`更新main；否则本章main继续draft。
