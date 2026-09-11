# 番茄发布协议

本协议回答：**仓库里的哪些内容应该推送到番茄。**

## 1. 唯一发布源

番茄发布器只能读取：

`chapters/ready/*.md`

其他目录一律视为内部资料。

## 2. 推送到番茄的内容

每个 ready 章节只发送：

1. **章节标题**
2. **章节正文**

发布器必须剥离：
- YAML Frontmatter；
- Markdown 内部注释；
- Agent/QA 备注；
- GitHub 路径、commit 信息；
- 字数统计；
- 大纲和摘要。

## 3. 绝对不能推送到番茄

以下全部只保留在 GitHub：

- `AGENTS.md`
- `config/`
- `bible/`
- `outlines/`
- `plans/`
- `memory/`
- `qa/`
- `docs/`
- `chapters/draft/`

这些是作者后台与 AI 的“脑内资料”，不是读者内容。

## 4. Ready 门槛

章节进入 `ready/` 前必须：
- Continuity QA = pass
- Style QA = pass
- 没有未处理的硬冲突
- Memory 已更新到该章结束状态
- `chapter_plan.csv` 已标记完成
- 正文中不存在 TODO、内部说明、模型自述、提示词残留
- Frontmatter 标记：`status: ready`、`qa: pass`

## 5. 发布后

发布器应核对番茄后台：
- 作品 ID 正确；
- 章节号与标题正确；
- 正文长度与本地基本一致；
- 没有重复章节；
- 发布/定时发布状态正确。

核验成功后：
1. 将本地章节状态改为 `published`；
2. 移入 `chapters/published/`；
3. 更新 `plans/chapter_plan.csv` 的 `publish_status`。

失败时不得假装成功，也不得删除 `ready/` 原文件。

## 6. 推荐安全策略

初期先使用“自动写作 + 自动 QA + 自动进入 ready，但番茄保存草稿/人工确认”的模式。稳定运行足够多章节后再考虑完全自动公开发布。
