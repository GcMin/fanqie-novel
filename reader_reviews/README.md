# Reader Reviews

本目录保存定时 Reader Agent 对最新草稿的独立阅读评论。

## 文件命名

`NNNN_<source_sha8>.md`

例如：`0037_a1b2c3d4.md`

同一章节正文发生修改后会产生新的 blob SHA，因此允许保留多个版本评论。

## 重要规则

- 评论不是小说正文，不推送番茄；
- Reader Agent 不直接修改被评论章节；
- `BLOCKER` / `MAJOR` / `MINOR` 必须分开；
- Pass A 不读取未来剧情答案；Pass B 才做内部逻辑核对；
- 不因为存在评论就自动阻止发布，当前阶段 Reader Review 为建议型 QA；
- Writer / Editor 后续修改草稿时应优先阅读该章最新一份 Review。

详细协议见 `docs/reader_agent_protocol.md`。
