# 第494章独立 Continuity / Style / Meaningful QA｜2026-11-03

**审核源稿：** `chapters/draft/0494.md` Git Blob `7baccf63314887c8420d381ca8773432a798e99f`；独立Reader Pass A后Pass B：0 BLOCKER / 0 MAJOR / 2 MINOR，`keep / none`；原小说正文0字修改。绑定 `reader_reviews/0494_7baccf63.md`，不沿用493章或其它正文版本的审查。

**结构内容检查 PASS：** 第494章，vol6，ARC-054；标题《旧歌被写成修好，原带还在桌上》与详细计划一致，非空白中文标题满足最低5字符。正文有效字符3415（剔除独立分场的5组三星分隔符；纯去空白包含分场符号3430），在硬范围2300—3800内。计划表唯一记录按章号追加，旧ready记录保留不覆盖；候选Front Matter设置status:ready、qa:pass、approved_at及publish_mode:ready。

**前章具体来源与版本差异 PASS：** 第493章正式ready Blob `dad59cdea686cd0eac3cf199cbd103440bd992fb` 与本章和详细计划依赖40位SHA精确一致，无旧/新SHA事实差异，未跳过未验证前章。第493章Day355 21时后董敬安现场真接中心电话、22:02实际回家、原录音机未修、原带尚未翻录；本章Day356前段手机违规试放并不反证其前夜已确认未修好。旧137→138、139→140、142→143、146→147及147→148旧历史交接继续以既有证据为准，本章未借其未知事实新增Canon。

**Continuity / 角色与时点 PASS：** Day356 17:25志愿者小阮仅私试放并用手机录19秒，20:42林叔收到误标群消息，21:16唐蕊管理员核原带及移放登记，21:48保留本群原帖源与限项撤回更正，22:12林叔本人真实签领取回；Day357上午修活动模板与限定说明，晚上20:09本人回拨确认原带在手、更正已看。原带未被鉴定完好/修复，外部副本仍未知；本群的撤回能力不可外推到私人聊天设备，已知两次外转仅证转达更正非销毁所有文件。林叔物品权利及个人电话隐私获尊重；小阮试播违背之前暂不翻录纸签，动机与道歉不能转化为技术免责。中心夜班20:00—08:00，Day357白天由社区和林叔独立操作，中心没有越班冒名执行。

**Style QA PASS：** 老胶痕、磁带窗、纸签、布袋及合唱六个人的名字有情感具体性；对话区分林叔、董敬安、小阮、夏宁梁策。规则解释略多是2项MINOR，只记录不触发重写。段落与句长有变化，结尾不虚假唱出未证的最后一句。

**Meaningful Change PASS：** 原带由社区保管真实转为林叔本人签领、官方误标群帖撤回并有源更正、已知两次外转获通知、志愿活动展示规则受限、维修只预约咨询，均为实际状态变化。安康接口正式修复、第三户退款到账、钟楼恢复、阿棋永久安排、F003/F008/M004/M005均未被本章擅改。

**Git结构门禁：** 本QA仅为内容PASS。必须对包含第494章ready、SHA绑定Review、本QA、Memory和唯一计划行的精确候选commit完成 `python -m publisher.check_local --repo .`（或可信相同代码的GitHub CI）实际SUCCESS，核实head SHA相同之后才允许以 `expected_sha`、`force:false` 将候选快进main；失败保留draft并记录阻塞。

## 精确候选结构校验与main实际放行证据
- 原始稿 Blob `7baccf63314887c8420d381ca8773432a798e99f`，双遍Reader `reader_reviews/0494_7baccf63.md` 0/0/2，独立内容QA PASS，正文0字修改；第493章前置正式ready `dad59cdea686cd0eac3cf199cbd103440bd992fb` 精确依赖。
- 含第494章正式ready、Reader Review、独立QA、长期Memory及完整计划的候选Git commit `6fb356be752a424b9189c94a0998352c656ee32f`，对应Git Tree `7d38c426bc77267b4fa21f99d977cf34e92eb4d8`；审计分支 `audit/ready-0494-20261103-1907` GitHub Actions run `41625992376` **SUCCESS**，运行head SHA与上述commit精确相同；`Test offline snapshot validation` SUCCESS，`Validate this checkout without Git sync or publishing` SUCCESS（实际运行 `python -m publisher.check_local --repo .`）。
- main原HEAD `f974a6addffdc52acd27dbf01b86e7563bc9fea1` 使用 `expected_sha`、`force:false` 非强制快进候选 `6fb356be752a424b9189c94a0998352c656ee32f` 成功并再次读取确认。正式ready Blob `24115755aac852cc43f90ff90f03e24157bc8ee6`；旧 `chapters/draft/0494.md` 在同一树中删除、无正文覆写，未经番茄发布。
- 上文“结构门禁待验证”仅为候选阶段描述；此处真实精确CI结果现已满足并覆盖该先前待核状态。
