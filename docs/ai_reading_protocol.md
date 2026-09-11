# AI 写作读取协议

本协议回答：**写下一章时 AI 应该读什么，什么不用读。**

## A. 每次写下一章前必读

按顺序读取：

1. `AGENTS.md`
2. `config/novel.yaml`
3. `bible/premise.md`
4. `bible/main_outline.md`
5. `bible/world.md`
6. `bible/style.md`
7. 与本章相关的 `bible/characters/*.md`
8. 当前 `outlines/volume_XX.md`
9. 当前 `outlines/arcs/arc_XXX.md`
10. `plans/chapter_plan.csv` 中当前章与未来约 5–10 章
11. `memory/current_arc.md`
12. `memory/character_state.yaml`
13. `memory/relationship_state.yaml`
14. `memory/knowledge_state.yaml`
15. `memory/world_state.yaml`
16. `memory/foreshadowing.csv` 中 active/计划近期触及的项目
17. `memory/timeline.csv` 中近期与本章相关事件
18. 最近约 10 章 `memory/chapter_summaries/*.yaml`
19. 最近 3–5 章完整正文，优先从 `chapters/published/`，其次 `chapters/ready/`

最后再生成**下一章详细章纲**，通过 Precheck 后才写正文。

## B. 旧历史按需检索，不常驻上下文

出现以下情况时再查更早章节/摘要：
- 回收旧伏笔；
- 老角色重新登场；
- 引用很久以前的承诺、伤势、物品或地点；
- 当前记录之间存在冲突；
- 需要复现旧场景细节或原话语义。

优先查 `chapter_summaries`、timeline、foreshadowing，再定位具体历史正文。

## C. 默认不要读取

- 全部历史章节全文；
- 与当前章无关的所有角色卡；
- 已关闭且与当前剧情无关的 QA 历史；
- 所有已回收且不再影响剧情的伏笔全文。

长上下文不是垃圾桶。信息越多不代表模型越记得重点。

## D. 写完一章后必须更新

至少更新：
- 本章 `memory/chapter_summaries/NNNN.yaml`
- `memory/current_arc.md`
- `memory/character_state.yaml`
- `memory/relationship_state.yaml`（有变化时）
- `memory/knowledge_state.yaml`
- `memory/world_state.yaml`（有变化时）
- `memory/timeline.csv`
- `memory/foreshadowing.csv`（有新增/触及/回收时）
- `plans/chapter_plan.csv`

每约 10 章重新压缩 `memory/global_summary.md`。

## E. Planner 生成的下一章详细章纲至少包含

- 本章目标；
- POV；
- 开场状态；
- 角色想得到什么；
- 阻碍/冲突；
- 3–6 个关键 beat；
- 本章新增信息；
- 人物/关系/危险/目标中的状态变化；
- 要推进或回收的伏笔；
- 不能提前泄露的信息；
- 结尾状态与承接点；
- 目标字数区间。
