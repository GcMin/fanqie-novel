# Chapters 章节文件协议

本目录同时服务 AI 写作流程与后续 Linux Python 番茄发布器。

## 目录状态

- `draft/`：正在创作、编辑或等待 QA，**绝不允许发布**。
- `ready/`：已通过 QA，**发布器唯一允许扫描的目录**。
- `published/`：番茄端已成功创建并核验后的正文快照。

状态迁移只能是：

```text
draft -> ready -> published
```

禁止从 `draft/` 直接发布，禁止把 `published/` 自动退回 `ready/`。

## 文件命名

统一使用：

```text
NNNN_章节标题.md
```

例如：

```text
0001_雨夜.md
0037_地下室.md
0128_旧车站.md
```

文件名前四位章节号必须与 Front Matter 中 `chapter` 一致。

## Markdown 文件格式

章节文件使用 UTF-8，LF 换行。Front Matter 保存机器状态，Front Matter 之后只保存读者可见正文。

```yaml
---
schema_version: 1
chapter: 1
title: 雨夜
volume: 1
arc: ARC-001
status: draft
qa: pending
char_count: 0
created_at: null
updated_at: null
approved_at: null
publish_mode: draft
scheduled_at: null
---
```

正文从第二个 `---` 后开始。

## 正文约束

为减少番茄发布器转换复杂度，章节正文建议使用“Markdown 文件 + 纯文本正文”的方式：

- 不在正文第一行重复章节标题；
- 不使用 Markdown 标题 `#` / `##`；
- 不使用表格、代码块、图片、链接；
- 不插入 AI 注释、TODO、QA 备注；
- 段落之间保留一个空行；
- 场景切换需要分隔时统一使用单独一行 `***`，发布器可转换为 `——` 或空行；
- 中文正文使用正常全角标点。

## 发布器最低校验

Linux Python 发布器在上传前必须至少验证：

1. 文件位于 `chapters/ready/`；
2. `schema_version == 1`；
3. `status == ready`；
4. `qa == pass`；
5. `chapter` 为正整数；
6. 文件名前缀与 `chapter` 一致；
7. `title` 非空；
8. 正文非空；
9. 重新计算正文字符数，不盲信 `char_count`；
10. 番茄后台不存在相同章节号，避免重复上传。

任意校验失败都应停止该章发布并记录错误，而不是尝试“猜测修复”。

## 发布内容

发布到番茄时只发送：

```text
chapter
title
body
```

不得发送 Front Matter、文件名、内部目录、AI 提示词、Memory、QA 报告或任何仓库元数据。

## Linux 部署注意

- 登录态、Cookie、浏览器 Profile、Token 均只保存在服务器本机或安全 Secret 中，禁止提交仓库；
- 发布器建议按章节号升序处理 `ready/`；
- 成功发布并在番茄后台核验后，再将文件迁移到 `published/`；
- 网络错误、验证码、登录失效、页面结构变化时应失败退出，不做绕过验证的逻辑；
- 推荐先实现“上传到番茄草稿箱”，稳定后再开启正式/定时发布。
