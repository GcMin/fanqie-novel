# 第481章独立 Continuity / Style / Meaningful Change QA｜2026-11-03

- **核验的源版本**：`chapters/draft/0481.md` Git Blob `46ee512c335ff1fd588b6ce9413a9744d6cbf4de`；独立Reader双遍 `reader_reviews/0481_46ee512c.md`，0 BLOCKER / 0 MAJOR / 2 MINOR，keep / none；无正文修订，无旧SHA复审需要。
- **依赖与章序 PASS**：第480章已在 `chapters/ready/0480.md`，正式Git Blob **d4771d4300bbbd81217a76e333be2d9fdafa5c5c**；481的草稿及详细章纲对它的引用皆精确匹配。没有临时草稿与最终前章的未比较版本差异。480止于Day343 10:17十一号实收、十二号外封见潮内件未核，481由Day343 20:26新馆借书台进入Day344授权开箱及后续公共告示；人物、时间及箱子状态自然连续。历史137/138、139/140、142/143、146/147、147/148旧事实差异并非本章证据来源，未据此自动免审或新增断言。
- **Front Matter / 章节编号 / 标题 / 字数 PASS（内容预检）**：文件名0481、`chapter:481`、`volume:6`、`arc:ARC-054`，标题《借书卡上的车轮还在，名字却不能随便念》与详细章纲、拟计划行一致，长度超过5个非空白字。正文3050有效字符（排除4处`***`分场符号），按照publisher代码的`normalized`连同12个分场星号计为3062；均在2600—3400偏好范围。尚须由精确候选Commit实际运行结构校验确认。
- **Continuity QA PASS**：第十二箱Day342夜有权整箱救出、Day343只在受控位置暂存，Day344由获准纸质资料人员检查外袋/受潮层及有限打开；上层可分卡编号，贴住的纸页不强拉；11:22看到似铅笔轮图但姓名栏遮挡且相邻页贴住，“相似图案”≠“借阅人身份核定”。旧屋短管只临时导排，未冒称永久修好。季唯补交有源操作事实/两类凭据；主管确认收件不等于最终审批；公众告示本身经有责环节限项更新也不等于档案里旧整车回执已改。
- **人物和知识边界 QA PASS**：许汀只安排保管权限内流程，不擅扩大对旧私人资料的展示；缪芸是退休见证人，只看允许呈现的画迹且明确拒绝凭几十年前印象认人；季唯承认误扫，记录可见事实不假签；纸质保护人员负责获准的操作，不把贴页分离和修复假定已经完成。志愿者不能公开旧借阅轨迹；父子不被旧卡与当代绘画强认。
- **Style QA PASS**：父子借修车书/新画轮子、缪芸摸旧桌布和留空行、贴页粘连和分项标签是有叙事功能的具体物象；季唯自责、许汀谨慎、缪芸惜物且尊重隐私有可辨对白。审稿记录两项MINOR：某些岗位限定语重复、书签隔日晚返场略被安排，均无强制修订依据。
- **Meaningful Change QA PASS**：第十二箱由“内部未核”真正进入受权限的分项检查，确认某些纸套受潮、部分贴页且见到**似**旧车轮画；外部公众告示由误导性全交付换成按真实时点列状态；缪芸从急于找旧卡主人转为尊重匿名和未核事实。纸张数量/损伤终局、个人身份、扫码更正审批及旧屋短管永久修理均待核。
- **Canon / F003 / F008 / M004/M005**：本章没有新增独立永安里史料；2022旧任务结束事件无实例子号、结果码和具体读取字节不能作完成证；F003旧关键事实仍未证，F008没有可靠新增记忆反证，M004/M005不借普通流程错映提前确证。Canon和published文件不修改。
- **放行结构门禁（候选阶段）**：Reader和以上独立内容QA已PASS，不等于结构校验PASS。仅当包含本章ready、从draft移除、Memory及完整章节计划行的**相同精确Git Commit**在GitHub Actions实际执行并SUCCESS完成`python -m unittest discover -s tests -p test_check_local.py -v`和`python -m publisher.check_local --repo .`后，才能以最新main的`expected_sha`、`force:false`原子放行。CI未执行、失败或main并发改变则保留draft，复核后重试；不force pass。

## 第481章正式ready结构门禁与main更新｜2026-11-03
- 精确候选并正式放行Commit `a199833406307918d2d4ec829bf228083d3e7acb`，Git Tree `f276fe806007bfa03b179724dc979fe8035d8424`。审计分支`audit/ready-0481-20261103` GitHub Actions `41535621570` **SUCCESS**，checkout精确候选SHA，结构单测与`python -m publisher.check_local --repo .`两步均为success。
- 实际main以`expected_sha=c33391b624ee4bcb1940bca7b46c82aa0fd6e38c`、`force:false`非强制更新成功，main同版本Actions `41535722474` **SUCCESS**。原`chapters/draft/0481.md`在同一Git Tree原子删除；正式`chapters/ready/0481.md` Git Blob `621991bba117c72193c8f8bb55eed31059dc1e42`。Reader0/0/2、独立内容QA三项PASS、正文0字改、前480ready精确依赖，Memory与计划已经同一候选树完成校验。
