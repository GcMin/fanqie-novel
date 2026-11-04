# 第513章独立 Continuity / Style / Meaningful QA｜2026-11-04

- 初稿源Blob `f5ef048eb88b609ab57c016b5f55dc256b398ab7`：Reader Pass A→B 0/2/2；MAJOR为依赖512仍为临时草稿SHA和长度申报3142但实际3154。
- 实际对照512原草稿Blob `fab485bedebb2280fa5574ca7fb5da21e11ee0a8`、修正长度版 `3b14cca386841b1f02ebc1012a7d21fbb815f633` 与正式ready Blob `42bab184c7780b3cbff0d3eb62637782f864ed03`：标题、小说正文逐字一致，差异仅字符数与status/qa/approved_at/publish_mode等交付字段；第513章原本依赖的“陶佩云本人续借、2019拟发待核发”故事事实无变化。Stage A只把513 Front Matter与详纲引用改绑正式ready SHA `42bab184c7780b3cbff0d3eb62637782f864ed03`、依赖状态写明facts reconciled、char_count改3154，小说正文0字改变。
- 修订后新draft Blob `c47c7b67c640c0b542ac33df8ee31f863bcaab48` 独立重新 Reader Pass A→B 0/0/2 keep/none，旧Review不能用于放行。
- Continuity PASS：512截止Day376 07:08且借机延至Day377 17:00，本章从Day376 09:12继续查拟发通知核发；14:42许可、15:26原双岗见同一拟发件当次审核“退回重拟”，不能推以后再稿永未外发/收到/历史本人答复。夜间20:47中心接赵爱莲求助、21:03梁策核西侧后巷被防护网占用、有责人员清障、安保试路、21:37带领、21:46本人与孙子实际入院并回拨。仅证两人真到院内，不证全院获通知或施工完成。
- Style PASS：老人担心孩子、湿面包与告示朝向等具体动作构成完整场景；MINOR为在夜案中回插下午档案线的短暂时间调整与后段提醒密集，但明确“曾”字，未造成MAJOR。
- Meaningful PASS：2019原拟稿审核退回重拟的新有源阶段和一宗居民真实获安全通路处置至少两项变化。F003边界如上，F008/M004/M005无新增独立证，青杉里702/榆荫路坡道/罗月本户状态不被改写。章号513、卷6 ARC-054、标题《通知退回原处，等门的人还没进去》与详纲一致，3154有效字符合规。
- **只有真实精确候选Commit结构单测及 `python -m publisher.check_local --repo .` 均SUCCESS，才能原子移动ready；本QA报告本身不构成结构放行。**

## 正式精确结构校验及main放行已完成
- Git Commit `5cb5ed1bc1e5f8c030e3d971032cc9aa5a23da47`，Tree `7c8a0f9bafd0b99c683f82195cc30f9ff03ae304`，candidate Actions `41784735180` completed/SUCCESS，main Actions `41784786060` completed/SUCCESS；两次运行的head_sha都等于本Commit，单元测试及 `publisher.check_local` 各自PASS。
- 已先经候选CI成功后才以旧main HEAD的expected_sha、force:false正式推进，原草稿删除，正式ready Blob `d0a9ee3ad802516db83905b5afae97c1fe720844`。本节的已验证事实覆盖本报告上方曾处于候选阶段的警告，不表示跳过结构门禁。
