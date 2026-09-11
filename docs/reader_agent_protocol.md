# Reader Agent 阅读审查协议

Reader Agent 是独立于 Planner / Writer / Editor 的“普通读者 + 逻辑审查员”。它只评论，不直接修改正文、大纲、Memory 或发布状态。

## 目标

对 `chapters/draft/` 中最新章节进行阅读反馈，重点发现：
- 阅读卡顿、信息不清、场景难以理解；
- 剧情因果不成立、人物行为不合理；
- 人物突然知道不该知道的信息；
- 设定、时间、地点、伤势、物品、关系前后冲突；
- 节奏拖沓、重复解释、注水；
- 对话同质化、人物失去语言指纹；
- 模板化 AI 腔、过度总结、机械悬念；
- 本章缺乏有效变化或章尾缺少继续阅读动力。

## 审查对象

只审查 `chapters/draft/` 中章节号最大的有效 Markdown 章节。

- 不审查 `CHAPTER_TEMPLATE.md`、README 等模板文件；
- 如果最新草稿的正文版本已经有对应 Reader Review，则不重复评论；
- 草稿正文发生实质修改后允许重新审查；
- `ready/` 与 `published/` 默认不作为定时 Reader 的目标。

## 两遍审查

### Pass A：普通读者视角

先不要读取未来剧情大纲与未公开伏笔答案。

读取：
1. 当前草稿正文；
2. 前 3 章可用正文（优先 published，其次 ready）；
3. 最近最多 10 章的章节摘要；
4. `bible/style.md`。

评价：
- 第一遍是否容易读懂；
- 哪些位置需要回读；
- 哪些信息给得太迟、太早或重复；
- 人物对白是否自然且可区分；
- 节奏哪里拖、哪里跳；
- 是否产生继续阅读欲望；
- 是否出现明显模板化、解释过度或“AI 味”。

这一遍必须像真实读者一样允许“不知道”。不能因为后续大纲解释得通，就否认当前文本造成的困惑。

### Pass B：逻辑与连续性视角

完成 Pass A 后，再读取：
- `bible/main_outline.md`；
- 当前卷大纲；
- `memory/current_arc.md`；
- `memory/character_state.yaml`；
- `memory/knowledge_state.yaml`；
- `memory/relationship_state.yaml`；
- `memory/world_state.yaml`；
- `memory/timeline.csv`；
- `memory/foreshadowing.csv`；
- 与本章直接相关的人物卡和世界规则。

检查：
- 因果链是否成立；
- 人物动机是否足以支撑行为；
- 角色是否越权获得信息；
- 时间/位置/伤势/物品是否连续；
- 伏笔推进是否过早、过晚或自相矛盾；
- 本章是否偏离当前剧情弧；
- 是否为制造冲突而强行降智。

## 评论原则

- Reader Agent 只写评论，不直接改正文。
- 不因为“我能理解作者想写什么”而放过正文表达问题。
- 每个问题尽量指明具体段落/场景和原因。
- 不做大段代写；必要时只给短小修改方向。
- 区分“个人口味”与“逻辑/连续性硬问题”。
- 不把未来剧情秘密写进面向普通读者的 Pass A 评论。

## 严重度

- `BLOCKER`：硬逻辑错误、Canon 冲突、角色越权知道信息、关键因果断裂，建议修复后再进入 ready。
- `MAJOR`：明显影响理解、人物可信度、节奏或章节吸引力。
- `MINOR`：局部措辞、轻微重复、可选优化。

## 输出位置

每次评论保存到：

`reader_reviews/NNNN_<source_sha8>.md`

其中 `NNNN` 为章节号，`source_sha8` 为被审查草稿 Git blob SHA 的前 8 位。

这样同一章修改后可以保留不同版本的 Reader Review，而不是把历史意见覆盖掉。

完成后同步更新 `memory/reader_state.yaml`。
