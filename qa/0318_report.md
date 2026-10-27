# 第318章独立 Continuity / Style / Meaningful QA（2026-10-27）

## 源版本、标题与门禁
审核的是 `chapters/draft/318.md` Git blob `39e263636078cfc133f13e6160838bde0fd74cf0`，正文非空白Unicode字符 3243，在硬2300—3800与首选2600—3400区间。Front Matter、章号、标题与详细章纲一致。
初审源 c2e128855b3364d2ca7870b2679b815a426fba98 的Reader为0/1/2，只因绑定317未审旧blob；Stage A一次仅改依赖元数据，不动正文。317原草稿 a5dbe2caf019e81b156b2b481f40364b5f7db2f5 与ready 1966c52470fab6a351b99ae11209c5952e78fc99 唯一差异为status/qa/approved_at/publish_mode，没有事件事实变化。新的完整318草稿blob 39e263636078cfc133f13e6160838bde0fd74cf0 重新独立双遍Reader后为0/0/2。
Reader Pass A普通读者视角完成后，另作Pass B Canon、人物知识/关系/世界/时间线/伏笔及前章SHA核查；最终 `reader_reviews/0318_39e26363.md` **BLOCKER=0，MAJOR=0，MINOR=2**，无待修 fix_required。

## Continuity QA：PASS
317正式ready仅交付Front Matter相对源草稿发生变动，正文Day179 10:36真实回收一原印、14印10控4未收且两张影印另控事实完全不变。318 Day179 20:26位于第177夜班，20:58道路核桥和卸货口禁行、21:09道路与企业门岗各核一段合法路、21:21本人工厂真正入门，22:37企业群自管撤旧置顶不等于所有缓存刷新或纸本回收。Day180 11:44道路只核昨20:58路况、13:16沈芷本人领有权事实摘录、15:02公司暂更正无证未到岗提示并留待程序核薪；20:00第178夜班。不能凭20:58核验倒填19:48路况或替企业裁定工资。
对历史137→138、139→140、142→143、146→147、147→148的旧/新事实差异保留原有效审核结论，不因当前章节SHA精确绑定擅自判定历史无差异。Day165以来62路新站合法运营不授予施工桥或卸货口任何公众通行权；历史1996本人回告、2018 A2两旧册同笔、F008可靠新记忆矛盾、M004/M005机制均不能从当代错误导向图推成已证。

## Style QA：PASS
企业考勤问题没有被中心工作记为市政责任；申请人未同意全面披露工作群/工资表；夜间路况的20:58核验没有被倒填为下车前已核。
对白、动作与证据逐层呈现，没有明显灌水复述或无场景服务的套话。两项MINOR只记录不触发重写。

## Meaningful Change QA：PASS
沈芷21:21门岗真记录、企业22:37撤错置顶，Day180 13:16本人真领道路事实摘录、15:02公司改无证未到岗为真实到岗和迟到原因待核，薪资未判。

## 精确结构检验
以上仅是草稿SHA独立内容QA。必须由包含两章原draft删除/ready迁入、Review/QA、Memory和plans的**精确候选Git commit**在GitHub Actions中实际执行单元测试与`python -m publisher.check_local --repo .`成功，才能使用expected_sha、force:false推进main；失败时main原draft保留并等待重试。
