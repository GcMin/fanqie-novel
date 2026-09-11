---
schema_version: 2
chapter: 0
title: ""
source_path: ""
source_sha: ""
reviewed_at: null
recommendation: revise
required_action: local_revision
blocker_count: 0
major_count: 0
minor_count: 0
scores:
  readability: 0
  engagement: 0
  logic: 0
  character: 0
  pacing: 0
  naturalness: 0
  next_chapter_pull: 0
---

# Reader Review

## 一句话读感

TODO

## Pass A：普通读者视角

### 好读的地方
- TODO

### 阅读卡顿 / 困惑
- TODO

### 节奏与信息释放
- TODO

### 人物与对白
- TODO

### 模板感 / AI 味
- TODO

### 章尾继续阅读动力
- TODO

## Pass B：逻辑与连续性

### BLOCKER
- 无 / TODO

### MAJOR
- 无 / TODO

### MINOR
- 无 / TODO

### 因果与人物动机
- TODO

### Canon / 时间线 / 状态检查
- TODO

### 伏笔与剧情弧
- TODO

## fix_required

仅列 `BLOCKER` 与明确的 `MAJOR`，供 Revision Agent 自动处理。每项必须具体、可执行，不写审美偏好。

1. severity: BLOCKER|MAJOR
   location: "具体段落/场景"
   problem: "问题是什么"
   required_result: "修订后必须达到的结果"

若没有必须修复项，写：`none`。

## observations

只记录不自动触发修改的观察，主要包括 MINOR、个人口味和可选优化。

- TODO

## 修改优先级

1. TODO
2. TODO
3. TODO

## 最终建议

- `keep`：没有 BLOCKER / MAJOR，可进入常规 QA；
- `revise`：局部修改可解决问题；
- `rewrite`：正文组织或核心场景需要整章重写。

`required_action` 只能是：
- `none`
- `local_revision`
- `chapter_rewrite`
- `replan_rewrite`

当前建议：`revise`
当前 required_action：`local_revision`
