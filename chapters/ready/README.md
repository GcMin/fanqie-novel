# Ready to Publish

这是**唯一允许番茄发布器扫描的目录**。

进入本目录必须同时满足：
- 章节正文完成；
- 长度在允许范围或已有明确例外理由；
- 连续性 QA 通过；
- 文风 QA 通过；
- `memory/` 已同步到该章结束状态；
- `plans/chapter_plan.csv` 已更新；
- Frontmatter `status: ready`、`qa: pass`。

发布器只发送章节标题和正文，必须剥离 Frontmatter 与内部注释。
