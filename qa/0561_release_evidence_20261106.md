# 第561章结构校验与正式ready放行证据｜2026-11-06

## 审核对象
- 原稿 `chapters/draft/0561.md` Git Blob：`01912c6932191b3405570fa56b6280de591838ea`。
- 正式迁移 `chapters/ready/0561.md` Git Blob：`4412c883901c4c28d3639ea1f78edbe79ca4157b`，章号561，标题《墙根又测了一次，封套仍未拆开》，`status: ready`、`qa: pass`、3456有效字符。
- 前章 `chapters/ready/0560.md` Blob：`e1677401cdc447842965493e235273e2e242fb47`，与正文及章纲依赖精确匹配。
- Reader Review：`reader_reviews/0561_01912c69.md`，真实独立先Pass A后Pass B，BLOCKER=0、MAJOR=0、MINOR=2，keep/none。
- 正文修订：0字；不存在修订引起的新SHA重审义务。
- 内容QA：`qa/0561_report.md`，Continuity PASS、Style PASS、Meaningful Change PASS。
- Memory已按正文同步：新章摘要、人物/知识/世界/关系/时间线/F003/当前弧、Reader与Revision状态；计划表仅追加561行，不覆盖旧ready行。

## 精确候选结构校验
- 候选 Git commit：`1fd68460d99722ae457338ac58a57437bea4431a`。
- 候选 Git tree：`0b71a536b789b4eea81e3461f61db6ab48225eb7`。
- 候选独立分支：`audit/ready-0561-20261106-1406`。
- Actions Run：`42173580046`，匹配候选 SHA，结果 **SUCCESS**。
- Job `127746789737`：`Test offline snapshot validation` **SUCCESS**；`Validate this checkout without Git sync or publishing` **SUCCESS**（运行 `python -m publisher.check_local --repo .`）。
- 明确以精确候选版本实测结构通过后，才执行正式main分支推进。

## 正式原子迁移与复检
- main发布Commit（实际快进）：`1fd68460d99722ae457338ac58a57437bea4431a`。
- main更新参数：`expected_sha=461dc8f52968858733ed333fbd9783ed0d9782cb`、`force:false`；返回success。
- 正式main Actions Run：`42173640461`，同一精确 SHA，结果 **SUCCESS**。
- Job `127746988064`：离线结构单元测试 **SUCCESS**；`python -m publisher.check_local --repo .` **SUCCESS**。
- 实查 `chapters/draft/` 无数字稿，`chapters/ready/0561.md` 存在且Blob正确，原草稿已删除。
- 仅迁入ready，**没有发布番茄平台**；未修改Canon、published正文或定时任务。

此文件为对已成功的精确提交和运行结果的事后证据归档，不以本身代替Reader或QA。
