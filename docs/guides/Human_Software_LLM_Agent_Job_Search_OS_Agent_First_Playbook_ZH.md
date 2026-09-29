---
title: Human + Software + LLM + Agent Job Search OS — Agent-First 工程实施手册
document_type: Engineering Playbook
language: zh-CN
status: Proposed
version: 1.0
last_updated: 2026-09-24
owner: Human Product Owner
review_cycle: monthly
---

# Human + Software + LLM + Agent Job Search OS

## Agent-First 工程实施手册（中文）

> 目标：让你可以像管理一支小型工程团队一样指挥 Codex，从产品想法一路推进到可验证、可回滚、可继续迭代的软件，而不是靠一个很长的对话和一组一次性提示词。

当前仓库的权威设计入口是 [Architecture](../../ARCHITECTURE.md)；文档职责与路径以
[documentation catalog](../README.md) 为准。

---

## 0. 先读这一页：你明天就可以怎么开始

如果你现在只有一个仓库、一个人和 Codex，不要先造一个 Symphony。先做下面六件事：

1. 在仓库根目录维护一个不超过约 150 行的 `AGENTS.md`，只放长期有效的操作契约、禁止事项、验证入口和文档地图。
2. 把当前架构、目标架构、数据不变量、运行方式分别放进独立文档，不把它们全部塞进 `AGENTS.md`。
3. 每个较大的功能先写一份 `docs/plans/active/JOS-xxx-*.md`；定义目标、范围、验收、风险、回滚和人工审批点，再让 Codex 实施。
4. 一项任务对应一个 Git 分支、一个 worktree、一个主要写入 Agent。需要并行时，并行不同任务，不让多个 Agent 同时修改同一组文件。
5. 每次交给 Codex 的指令都包含：目标、事实来源、范围、禁止事项、验收证据、文档更新责任和停止条件。
6. 合并前必须看到真实证据：测试结果、关键输出、数据库迁移演练、界面截图或运行日志。Agent 的“已完成”不是证据。

第一阶段建议只运行：

- 1 个实现任务；
- 必要时再开 1 个独立审查任务；
- 所有外部写入、数据删除、数据库切换、真实申请提交都由你批准。

这已经是 agent-first。Agent-first 的核心不是 Agent 数量，而是把意图、边界、事实、验证和恢复路径做成 Agent 能读取并执行的系统。

---

## 1. 本手册如何使用 OpenAI 两篇文章

### 1.1 主要来源

- **S1 — OpenAI, “Harness engineering: leveraging Codex in an agent-first world”**  
  https://openai.com/index/harness-engineering/
- **S2 — OpenAI, “An open-source spec for Codex orchestration: Symphony”**  
  https://openai.com/index/open-source-codex-orchestration-symphony/

补充的 Codex 官方入口：

- Codex 学习与产品资料：https://developers.openai.com/learn/codex
- 长任务与持久目标示例：https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex

### 1.2 来源原则与本项目改造的区别

| 类型 | 内容 | 在本手册中的处理 |
|---|---|---|
| **S1 来源原则** | 仓库内、版本化的知识是 Agent 可读取的事实来源；给地图而不是千页手册 | 采用：短 `AGENTS.md` + 分层文档 + 可执行验证 |
| **S1 来源原则** | 通过测试、lint、结构规则和反馈回路约束 Agent，不只靠提示词 | 采用：把安全与数据不变量变成测试和 CI |
| **S1 来源原则** | 人负责优先级、意图和结果验收；Agent 执行实现、测试、文档和修复 | 采用，但求职事实和外部申请必须保留更强人工控制 |
| **S1 来源经验** | OpenAI 实验中所有仓库代码都由 Codex 生成 | **不作为本项目要求**；你可以手改，但应把重要修正反馈成规则或测试 |
| **S1 来源经验** | 高吞吐下使用短生命周期 PR 和较少阻塞门禁 | **不直接照搬**；个人求职数据、迁移和外部动作需要保守门禁 |
| **S2 来源原则** | 任务/Issue 是控制平面；每个任务有独立工作区，状态驱动执行 | 分阶段采用：先用仓库任务文件和 GitHub Issue，再考虑编排器 |
| **S2 来源原则** | 目标比僵硬步骤更重要；Agent 可以处理 PR、CI 和反馈循环 | 采用：Agent Brief 写“完成状态”和证据，不规定每一行实现 |
| **S2 来源经验** | 人通常只能舒适管理约 3–5 个交互式会话 | 用作上限信号；本项目初期建议只并行 1–2 个，成熟后最多 3 个 |
| **S2 来源边界** | 含糊、需要强判断的任务仍适合交互式 Codex，而非无人值守编排 | 采用：产品取舍、签证判断、职业叙事和架构分歧留给人机共创 |
| **本手册建议** | SQLite 作为单机阶段的权威状态库 | 是针对个人、本地优先系统的改造，不是两篇文章的结论 |
| **本手册建议** | Notion 作为行动视图，Obsidian 作为经人工确认的职业知识库 | 是 Job Search OS 的领域适配，不是 OpenAI 原文实践 |

### 1.3 应复制什么，不应复制什么

应该复制：

- 仓库知识可发现、可版本化、可验证；
- 人定义目标与边界，Agent 负责执行；
- 失败后补能力、补规则、补测试，而不是只换一种措辞重试；
- 任务、工作区、分支、证据包之间有清楚映射；
- 把 Agent 看成能使用工具的工程协作者，而不是代码补全器。

不应复制：

- “零人工代码”作为身份或 KPI；
- 在测试和回滚尚不成熟时追求 PR 数量；
- 为个人项目提前建设常驻多 Agent 编排平台；
- 把求职领域的高风险判断交给无人值守 Agent；
- 假设 OpenAI 内部规模、工具、权限和容错成本与你相同。

本项目的口号应改写为：

> **Human steers and approves. Software preserves truth. LLM interprets. Agents execute bounded work.**  
> 人负责方向与批准；软件维护事实；LLM 做受约束理解；Agent 执行有边界的工作。

---

## 2. 操作模型：四个执行者和一个控制平面

### 2.1 四类执行者

| 执行者 | 负责 | 不能擅自负责 |
|---|---|---|
| Human | 产品目标、个人事实、风险偏好、职业判断、验收、外部提交 | 重复搬运状态、手工跑可自动化检查 |
| Software | 抓取、解析、确定性过滤、状态机、存储、同步、预算、审计 | 主观匹配、未经编码的模糊判断 |
| LLM | JD 结构化、语义分类、证据映射、解释和草稿 | 事实主库、硬性资格终审、外部写入 |
| Agent | 调用工具完成有限多步任务、实现代码、运行测试、生成证据包 | 无界研究、修改个人事实、自动投递、绕过权限 |

### 2.2 唯一控制平面

在开始阶段，**当前交接和活动 ExecPlan 是仓库内控制平面**：

```text
docs/current-state.md  当前活动任务、阻塞和下一步交接
docs/plans/active/     已授权并正在执行的计划
docs/plans/completed/  已完成、取消或被替代的计划；首个计划结束时才创建
```

`BACKLOG / READY / REVIEW / BLOCKED` 可以保存在任务平台或 active plan 的状态与
进度中，不要为每个状态创建空目录。如果以后采用 GitHub Issues、Linear 或自建
编排器，仓库仍保存可执行规范、ADR、schema、eval 和关键决策。不要同时让聊天、
Notion、GitHub Issue 和 Markdown 各自保存一套不一致的“真实进度”。

### 2.3 一个任务的状态机

```text
BACKLOG
  ↓ 人确认价值与范围
READY
  ↓ 分配 branch + worktree + agent
ACTIVE
  ├── 需要人作决定 → BLOCKED
  ├── 验证失败但仍可修 → ACTIVE
  └── 证据齐全 → REVIEW
REVIEW
  ├── 需修改 → ACTIVE
  ├── 放弃 → CANCELLED
  └── 人验收 → MERGED → DONE
```

状态改变必须伴随证据，不允许仅因为 Agent 说“完成了”就进入 `DONE`。

---

## 3. 推荐仓库目录

下面是与当前 documentation catalog 一致的目标目录。不要第一天创建所有空目录；
在出现第一份真实内容时再创建对应文档族。

```text
job-search-os/
├── AGENTS.md                         # 短小的 Agent 操作契约与导航地图
├── README.md                         # 人类入口：产品、快速开始、当前能力
├── ARCHITECTURE.md                   # CURRENT / TARGET 高层架构
├── PLANS.md                          # ExecPlan 规则与生命周期
├── pyproject.toml                    # 或项目实际依赖配置
├── .env.example                      # 仅变量名与安全示例，绝无真实 secret
├── .gitignore
├── .github/
│   ├── pull_request_template.md
│   └── workflows/
│       ├── test.yml
│       ├── docs-check.yml
│       ├── eval.yml
│       └── daily-digest.yml
├── docs/
│   ├── README.md                     # 文档目录、权威归属、状态说明
│   ├── roadmap.md                    # 产品/工程结果与阶段顺序
│   ├── current-state.md              # 当前工作、阻塞、下一步；短期交接
│   ├── designs/                      # 已存在：持久技术设计
│   ├── plans/
│   │   ├── active/                   # 已存在：活动 ExecPlan
│   │   └── completed/                # 首个计划真正结束时才创建
│   ├── guides/                       # 已存在：人类指南
│   ├── references/                   # 已存在：历史和点时证据
│   ├── product-specs/                # 有首份详细产品规格时才创建
│   ├── decisions/                    # 有首份独立 ADR 时才创建
│   ├── runbooks/                     # 有首份已验证操作手册时才创建
│   ├── evaluations/                  # 有首份质量规范时才创建
│   └── generated/                    # 有生成器和首份产物时才创建
├── schemas/
│   ├── source-observation.schema.json
│   ├── canonical-job.schema.json
│   ├── job-analysis.schema.json
│   ├── agent-research.schema.json
│   └── daily-digest.schema.json
├── migrations/
│   ├── 0001_initial.sql
│   └── README.md
├── prompts/
│   ├── README.md
│   ├── extract-job-v1.md
│   ├── score-fit-v1.md
│   └── research-job-v1.md
├── evals/
│   ├── fixtures/
│   ├── expected/
│   └── runners/
├── src/
│   ├── collectors/
│   ├── normalisation/
│   ├── canonicalisation/
│   ├── rules/
│   ├── llm/
│   ├── agents/
│   ├── storage/
│   ├── ranking/
│   ├── integrations/
│   └── digest/
├── tests/
│   ├── unit/
│   ├── contract/
│   ├── integration/
│   └── end_to_end/
├── scripts/
│   ├── check-doc-links.sh
│   ├── check-generated.sh
│   ├── backup-sqlite.sh
│   └── verify-migration.sh
└── var/                               # gitignored 本地状态
    ├── job-search-os.sqlite3
    ├── backups/
    └── artifacts/
```

### 3.1 与现有 Job_Scraper 的关系

现有仓库已经有：

- `AGENTS.md`：操作契约、证据优先级和渐进式阅读入口；
- `ARCHITECTURE.md`：CURRENT 与 TARGET；
- `PLANS.md`：ExecPlan 契约；
- `docs/current-state.md`：当前交接；
- `docs/designs/canonical-job-model.md`：已接受的 Canonical Job 语义；
- `docs/plans/active/`：活动计划。

因此，如果继续在现有仓库演进，不要平行创建另一套同义目录。优先映射：

| 本手册概念 | 现有 Job_Scraper 位置 |
|---|---|
| Agent 操作契约 | `AGENTS.md` |
| 当前/目标架构 | `ARCHITECTURE.md` |
| 任务执行计划规则 | `PLANS.md` |
| 当前交接 | `docs/current-state.md` |
| 活动任务计划 | `docs/plans/active/` |
| 领域模型设计 | `docs/designs/canonical-job-model.md` |
| 参考审计 | `docs/references/` |

**重要冲突：**现有仓库已记录长期向 Postgres/Supabase 迁移的方向；本手册的 SQLite 是适合个人本地优先 v0/v1 的推荐示例。若在现有仓库采用 SQLite 作为目标权威存储，必须新建 ADR，说明它是临时阶段、永久方向还是替换原决策，并经你批准。Agent 不得把本手册当成默许的架构改写授权。

---

## 4. Agent 指导文档：内容 pattern 与边界

### 4.1 `AGENTS.md`：地图与操作契约，不是百科全书

根 `AGENTS.md` 应只包含长期、跨任务、需要每次都知道的内容：

```markdown
# Agent operating contract

## Mission
把现有 Job_Scraper 增量演进为个人 Job Search OS；保持可验证、可回滚。

## Evidence precedence
运行代码/加载配置/工作流 > schema 与聚焦测试 > 已接受设计 > 当前交接 > 历史参考。

## Read progressively
- 所有任务先读本文件。
- 大任务再读 docs/current-state.md 和相关架构。
- 迁移读 migration runbook；LLM 改动读对应 eval spec。

## Core invariants
- 先确定性规则，后 LLM。
- UNKNOWN 不得自动变成 false 或淘汰。
- Job 事实、个人分析、申请状态分离。
- 禁止修改真实 secrets；禁止自动提交申请。

## Working method
- 编辑前检查 Git 状态和相关测试。
- 大改先有 active task spec。
- 编辑后运行验证、检查 diff、更新 owning docs。

## Commands
- Unit: <真实命令>
- Contract: <真实命令>
- Full: <真实命令>
- Docs: <真实命令>

## Documentation map
- Architecture: ARCHITECTURE.md
- Active work: docs/current-state.md
- Decisions: docs/decisions/
- Runbooks: docs/runbooks/
```

不要放进 `AGENTS.md`：

- 一次性任务需求；
- 某次测试输出；
- 大段架构细节；
- 会频繁变化的进度；
- 可由 schema、类型、测试或脚本强制的规则全文；
- 重复出现在其他权威文档中的内容。

子目录可以有局部 `AGENTS.md`，但只用于局部特殊规则，例如 `migrations/AGENTS.md` 规定迁移不可破坏性，`evals/AGENTS.md` 规定金标准样本不能由被测模型自动改写。局部规则不能悄悄推翻根规则。

### 4.2 架构文档：始终区分 CURRENT、TARGET、PROPOSED

每条架构声明标注一种状态：

- `CURRENT`：已用代码、运行结果或配置验证；
- `TARGET`：经人接受的目标方向；
- `PROPOSED`：尚待决定或实验；
- `DEPRECATED`：仍存在但准备淘汰；
- `REFERENCE`：历史证据，不自动保持最新。

推荐内容：

```markdown
# Architecture

## CURRENT
- 当前数据流
- 每个模块的真实责任
- 当前权威存储
- 已知漂移与限制

## TARGET
- 目标数据流
- 权威边界
- 不变量
- 迁移阶段

## Gaps
| Gap | Evidence | Planned owner | Task |

## Verification
- 最后验证日期
- 使用的命令/代码位置
- 未验证范围
```

### 4.3 Task Spec / ExecPlan：让无上下文 Agent 也能续接

当任务满足任一条件时，先写任务计划：跨多个模块、数据迁移、外部集成、LLM 行为变化、架构边界变化、超过半天、失败代价较高。

Task Spec 必须自包含：

- 为什么做、可观察结果；
- 当前行为与证据；
- 范围与非目标；
- 兼容性约束；
- 可执行步骤；
- 验收与真实验证结果；
- 幂等性、失败、恢复和回滚；
- 进度、发现和决定；
- 人工审批点。

聊天可以帮助形成 Task Spec，但聊天不是最终事实来源。

### 4.4 ADR：记录难以逆转的“为什么”

以下情况必须 ADR：

- SQLite、Postgres 或其他权威存储选择；
- Canonical Job ID 策略；
- Notion 双向还是单向同步；
- Obsidian 可写边界；
- 模型供应商或数据出境边界；
- 是否允许自动合并、自动发送或自动提交；
- 不兼容 schema 变化。

ADR 只记录重要决策，不记录每天的实现细节。状态采用 `Proposed → Accepted → Superseded / Rejected`。后来的 ADR 通过链接取代旧 ADR，不重写历史。

### 4.5 Runbook：在压力下也能照着恢复

每个 runbook 必须包含：

- 触发症状；
- 风险和停止条件；
- 前置检查；
- 逐步操作；
- 每一步预期结果；
- 失败分支；
- 恢复/回滚；
- 验证完成；
- 升级给人的条件。

例如 `restore-sqlite.md` 不能只写“恢复备份”，而要写备份位置、校验方法、复制到临时位置验证、何时替换、怎样保留坏库和怎样确认记录数/迁移版本。

### 4.6 Evaluation Spec：在改模型之前定义“好”

每项 LLM/Agent 能力至少定义：

| 字段 | 说明 |
|---|---|
| Objective | 评估什么能力 |
| Dataset | 固定样本、来源、隐私等级、版本 |
| Ground truth | 谁确认、如何更新 |
| Metrics | 精确率、召回率、字段正确率、成本、延迟等 |
| Must-pass slices | 签证、远程、缺失字段、prompt injection 等高风险切片 |
| Thresholds | 上线/回滚阈值 |
| Procedure | 可重复命令与环境 |
| Result | 日期、模型、prompt、代码版本和结果 |

不得让同一个被测 Agent 自己修改金标准并宣布通过。候选输出可以由 Agent 生成，但金标准变更由人审阅。

### 4.7 Schema：事实契约，不是愿望清单

Schema 应：

- 有唯一版本；
- 对缺失、空值和 `UNKNOWN` 有明确语义；
- 区分输入 observation、canonical fact、LLM analysis 和 workflow state；
- 在生产写入边界执行验证；
- 有兼容性测试与迁移；
- 不把未来想要的字段标成“当前必需”而生产又不验证。

### 4.8 Invariants：少而硬，可机械执行

不变量分三层：

1. 数据库约束：外键、唯一性、非空、枚举、版本；
2. 结构检查：模块依赖方向、禁止导入、禁止 secrets 路径；
3. 行为测试：UNKNOWN 处理、同步所有权、外部审批门。

文档说明为什么；代码和 CI 决定是否真的阻止错误。

### 4.9 Checklists：给人和 Agent 一个相同的完成标准

Checklist 要短、二元、可验证。不要写“代码质量良好”，而写：

- [ ] 修改路径有对应自动测试；
- [ ] 所有新增 schema 字段有缺失/未知用例；
- [ ] 未在日志、fixture、截图中暴露 secret/PII；
- [ ] 外部写操作仍停在人工批准前；
- [ ] 迁移已在备份副本演练并验证回滚。

### 4.10 Work Log：记录过程证据，不伪装成架构真相

Work Log 属于任务文件或 `var/artifacts/<task-id>/`：

```markdown
## Work log

### 2026-09-24 10:30 Europe/London
- Action: 在备份数据库运行 0003_add_observation_hash.sql
- Result: 迁移成功，1,842/1,842 行得到 hash
- Evidence: artifacts/migration-dry-run.txt
- Interpretation: 可继续运行 contract tests
- Next: 测试旧版 JSON export
```

Work Log 是审计轨迹；长期规则要提升到 runbook、ADR、schema 或测试。

---

## 5. 文档归属：人写什么，Agent 写什么，双方怎样协作

### 5.1 所有权矩阵

| 文档/内容 | Human-owned | Agent-maintained | Joint | 更新触发 |
|---|---:|---:|---:|---|
| 产品愿景、成功定义 | ✅ |  | 可提案 | 产品方向变化 |
| 个人事实、签证、毕业日期、经历与数字 | ✅ |  | 仅整理/指出冲突 | 用户明确确认 |
| 职业偏好、风险容忍、申请策略 | ✅ |  | 可分析 | 人作新决定 |
| `AGENTS.md` 原则与审批边界 | ✅ 最终批准 | 可起草 | ✅ | 工作方式或风险边界变化 |
| CURRENT 架构 |  | ✅ 基于证据更新 | ✅ 审核 | 实现边界改变 |
| TARGET 架构 | ✅ 批准 | 可分析/起草 | ✅ | 架构决定变化 |
| Task Spec / ExecPlan | 定义目标、范围、验收 | 更新进度、发现、验证 | ✅ | 任务全生命周期 |
| ADR | 批准决策 | 收集选项/证据、起草 | ✅ | 不可逆或跨模块决策 |
| Runbook | 批准高风险动作 | 起草、按真实演练修正 | ✅ | 流程或工具变化 |
| Schema/API 文档 | 审核语义 | ✅ 随代码生成/更新 | ✅ | 契约变化 |
| Eval spec | 定义业务标准/高风险切片 | 实现 runner、报告结果 | ✅ | 模型/prompt/规则变化 |
| 生成文档 |  | ✅ 仅由生成器 |  | 源契约变化 |
| Work log |  | ✅ | 人可补充决定 | 每个重要执行步骤 |
| Review checklist | ✅ 批准高风险项 | 执行并提供证据 | ✅ | 合并前 |

### 5.2 开发中何时更新文档

不要规定“每改一行代码都更新文档”。采用触发式更新：

| 发生的变化 | 必须更新 |
|---|---|
| 任务开始 | Task Spec 状态、起始 revision、branch/worktree |
| 发现当前行为与文档不符 | Task discovery + owning CURRENT doc，或开独立修复任务 |
| 作出持久架构决定 | ADR + 架构链接 |
| 数据契约变化 | schema + contract test + migration + owning design |
| CLI/运行步骤变化 | runbook/README + smoke test |
| LLM prompt/model变化 | prompt version + eval result + cost/latency记录 |
| 外部集成字段变化 | field ownership matrix + integration contract |
| 遇到可重复失败 | 回归测试；必要时更新 AGENTS/runbook |
| 任务完成 | 实际验证、偏差、剩余工作、current-state、移入 done |

### 5.3 防止文档漂移

使用五道防线：

1. **唯一权威归属。** 每个主题只有一个 owning doc，其他地方只链接。
2. **状态标签。** CURRENT/TARGET/REFERENCE/GENERATED 不混写。
3. **CI 机械检查。** 链接、frontmatter、任务状态、schema 示例、生成文件差异。
4. **PR 模板强制询问。** “哪些文档受影响？为什么无需更新？”
5. **定期 gardening。** 每月让 Agent 扫描可疑漂移并开小 PR，人决定是否接受。

建议的文档检查不是比较自然语言是否“正确”，而是寻找可机械验证的信号：

- 文档引用的文件/命令是否存在；
- schema 示例是否通过验证；
- `active` 任务是否长时间无更新；
- `CURRENT` 文档引用的函数名是否消失；
- 生成文件是否与源 schema 一致；
- 任务标记 done 时是否有验证结果。

### 5.4 Review 工作流

```text
Agent 更新代码 + 测试 + owning docs
          ↓
Agent 自查 diff 与验收标准
          ↓
独立 Review Agent 只读审查（可选）
          ↓
CI：unit / contract / integration / docs / eval
          ↓
Human：产品语义、个人事实、风险门、可见结果
          ↓
Agent 根据反馈修复并重跑验证
          ↓
Human 批准 merge
```

审查反馈分四类：

- **Bug:** 直接修复并加回归测试；
- **Missing contract:** 补 schema/invariant/test；
- **Missing context:** 补 owning doc 或任务说明；
- **Taste/preference:** 若会重复出现，转成小而明确的规则；否则只在当前 PR 修正。

---

## 6. 实际如何指挥 Codex：使用哪一种界面

### 6.1 选择矩阵

| 入口 | 最适合 | 不适合 | 输出应落在哪里 |
|---|---|---|---|
| ChatGPT 讨论 | 澄清愿景、比较方案、发现未知、组织用户事实、写产品草案 | 直接声称已修改/测试本地仓库 | 经确认后转入 product doc / ADR / Task Spec |
| Codex Desktop/Chat | 需要读仓库、改文件、跑测试、看 diff、长时间迭代的工作 | 未定义边界的高风险外部操作 | branch/worktree + task log + artifacts |
| Codex CLI 交互 | 你已在终端，需快速调查、修改、运行命令 | 多项目状态管理、非技术讨论 | 当前 worktree 与 Git diff |
| `codex exec` 类非交互任务 | 可重复、范围清楚、可由 CI/脚本调用的单任务 | 含糊产品设计、需要频繁选择 | 机器可读输出、日志、PR |
| Issue / Task 文件 | 需要异步执行、交接、排依赖、定义完成状态 | 临时的一句话解释 | 唯一任务记录 |
| Pull Request | 审查可合并变更、聚合证据、讨论 diff | 早期头脑风暴 | 可审查 diff + 证据包 |
| 命令/脚本 | 完全确定、频繁重复、无需模型判断的流程 | 模糊语义判断 | 可重复日志或生成物 |
| 自动化/编排器 | 成熟、低风险、高频、已有防护和恢复的任务 | 第一次运行、敏感字段、投递申请 | 状态机 + 审计日志 + approval gate |

### 6.2 正确的层级转换

```text
ChatGPT：我真正想解决什么？有哪些选择？
      ↓ 人确认方向
Product/ADR：被接受的意图与决定是什么？
      ↓
Task Spec：本次具体交付什么？怎样证明完成？
      ↓
Codex Desktop/CLI：在真实仓库实施、验证、记录
      ↓
PR：审查差异和证据
      ↓
Merge：更新 current state，进入下一任务
```

不要把 ChatGPT 聊天中的一句“我觉得可以用 SQLite”直接当成已接受架构。让 Codex 先生成 ADR 草案，列出现有 Postgres 方向、迁移成本、个人本地使用需求和选择后果，再由你批准。

### 6.3 给 Codex 的最小高质量指令

```markdown
请在当前仓库完成任务 JOS-014。

目标：将每日摘要改为从 SQLite 的 daily_queue 读取，并保持现有 JSON 摘要兼容。

先读：
- AGENTS.md
- docs/plans/active/JOS-014-sqlite-daily-digest.md
- docs/designs/<owning-design>.md
- docs/runbooks/migration-rollback.md

范围：src/digest、src/storage、相关 tests 和 owning docs。
非目标：不修改抓取逻辑，不启用 Notion 写入，不删除 JSON 路径。

完成条件：
1. 旧 JSON fixture 与 SQLite fixture 产生相同的岗位集合；
2. UNKNOWN eligibility 不被排除；
3. unit、contract、digest eval 通过；
4. 任务文件记录真实命令、结果和限制；
5. 提交可审查 diff，但不要 merge。

安全边界：
- 不读取或修改真实 .env；
- 不连接生产 Notion；
- 不运行不可逆 migration；
- 如需改变 schema 或架构方向，停止并写出 ADR 需求。
```

### 6.4 什么时候用普通 prompt，什么时候用持久 Goal

普通 prompt：一次性解释、小 bug、局部重命名、只读审查。  
持久 Goal：路径会根据实验结果变化，但完成线可测，例如降低重复率、修复 flaky test、完成迁移演练。

持久 Goal 的内容应包括：

- 期望最终状态；
- 证明方式；
- 不得破坏的约束；
- 允许的文件、数据和工具；
- 每轮如何选择下一步；
- 何时诚实停止并报告阻塞。

示例：

```text
目标：把 canonical matching eval 的 precision 提升到 ≥0.98，且 recall 不低于当前基线，
以 evals/canonical-matching-v1 中冻结样本为证据。只修改 canonicalisation、相关测试和文档；
不得改变金标准、不得用标题模糊相似直接合并。每轮记录改动、指标和失败切片。
若三种有证据的方案都无法达标，停止并报告尝试、结果、风险和需要的人类决定。
```

### 6.5 命令行使用原则

Codex CLI 的具体参数会随版本变化，先以当前官方帮助和文档为准：

```bash
codex --help
codex exec --help
codex review --help
```

推荐把**稳定命令**写进仓库脚本或任务 runner，把自然语言目标交给 Codex。不要在文档里长期复制一串可能过期的复杂 flags。

可重复的本地工程入口可以是：

```bash
make test
make test-contract
make eval
make docs-check
make verify
```

这些只是接口建议；实际仓库应绑定真实命令，禁止创建“看起来存在但什么都没验证”的占位命令。

---

## 7. 端到端 SOP：从想法到下一轮迭代

### 阶段 1：产品想法

Human 写清楚：

- 哪个具体痛点；
- 谁会使用；
- 当前替代方案；
- 什么变化才算有价值；
- 哪些事实只有本人能确认。

示例：

> 我每天面对 30 个岗位，实际只能认真处理 3 个。我需要系统先排除明显不符合地点/工作权的岗位，再从剩余岗位中给出 3 个有解释的优先项。系统不得替我判断未写明的签证条件，也不得自动投递。

产物：已有 roadmap 的更新，或在确有首份详细规格时创建
`docs/product-specs/daily-queue.md`。

### 阶段 2：问题调查与 CURRENT 基线

让 Codex只读检查：

- 当前代码路径；
- 数据生产者和消费者；
- 当前 schema 与真实数据差异；
- 已有测试真正覆盖什么；
- 配置、工作流、localStorage、JSON 等兼容面；
- 本地证据和远程状态的区别。

产物：任务中的 `Context and Evidence`，必要时更新 CURRENT architecture。不要在这一步顺手重构。

### 阶段 3：架构选择

只对需要决定的部分写 ADR：

- 选项；
- 约束；
- 权衡；
- 决定；
- 后果；
- 退出/替换条件。

Job Search OS 示例：SQLite 适合单用户、本地事务和简单备份；Postgres 更适合多设备、服务端同步和并发。若第一阶段目标只是可靠替换浏览器 localStorage，SQLite 可能是较小步骤；如果现有接受方向是 Postgres，必须说明 SQLite 是过渡还是方向变更。

### 阶段 4：拆任务与依赖图

按“可独立验证的结果”拆，不按目录拆：

```text
JOS-001 定义 canonical schema + contract fixtures
    ↓
JOS-002 SQLite repository + migration 0001
    ↓
JOS-003 JSON → SQLite shadow import + parity report
    ├── JOS-004 deterministic eligibility rules
    └── JOS-005 dashboard read adapter
             ↓
JOS-006 explicit cutover decision
```

坏拆法：Agent A 改 model、Agent B 改同一 model 的测试、Agent C 改 migration。它们会争抢同一契约。  
好拆法：先由一个任务完成 schema 和契约；后续独立消费者并行。

### 阶段 5：Definition of Ready

任务进入 `ready` 前检查：

- [ ] 用户价值和可观察结果清楚；
- [ ] CURRENT 基线有证据；
- [ ] 范围和非目标清楚；
- [ ] 输入/输出/兼容面已列出；
- [ ] 验收可执行；
- [ ] 风险、人工审批点和回滚已定义；
- [ ] 无需未授权的凭据或外部动作；
- [ ] 依赖任务已完成或明确阻塞。

### 阶段 6：创建 Agent Brief

Agent Brief 是任务文件的执行摘要，不重复完整设计。至少包含：

- objective；
- must read；
- scope / non-goals；
- constraints；
- acceptance evidence；
- allowed tools/data；
- human gates；
- blocked stop condition。

模板见第 13.1 节。

### 阶段 7：分支与 worktree

```bash
git fetch origin
git switch main
git pull --ff-only
git worktree add ../job-search-os-wt/JOS-014 -b feat/JOS-014-sqlite-digest main
```

在任务文件记录：

```yaml
task_id: JOS-014
branch: feat/JOS-014-sqlite-digest
worktree: ../job-search-os-wt/JOS-014
base_revision: <commit-sha>
primary_agent: implementation
```

不要让多个 Agent 共用同一个工作目录写文件。

### 阶段 8：实现循环

Agent 的循环：

```text
读取相关上下文
  → 验证当前基线
  → 做最小可验证变更
  → 跑聚焦测试
  → 检查 diff
  → 跑更广验证
  → 更新任务日志和 owning docs
  → 对照验收条件
  → 继续、完成或明确阻塞
```

Human 不需要逐行指挥，但要在这些点介入：

- 目标或语义发生变化；
- 需要新的权限、凭据或外部服务；
- 要改变个人事实或高风险默认值；
- 要执行不可逆迁移/删除；
- 验收标准本身被证明不合理；
- 两个合理架构选项需要价值判断。

### 阶段 9：测试与 Eval

验证顺序：

1. unit：纯函数、规则、解析；
2. contract：schema、repository、同步字段所有权；
3. integration：SQLite、Notion mock、真实文件边界；
4. eval：LLM/Agent 质量、切片、成本、延迟；
5. end-to-end：从 fixture 抓取到 daily digest；
6. manual proof：需要时检查 UI、导出或恢复演练。

LLM 变更不能只看“示例感觉更好”。至少比较：旧版本、候选版本、固定数据集、关键切片、成本和失败样本。

### 阶段 10：生成 Review Packet

每个 PR 附带：

```markdown
## What changed
## Why
## Scope / non-goals
## Evidence
- tests:
- evals:
- screenshots/artifacts:
- migration dry-run:
## Data and safety impact
## Docs updated
## Known limits
## Rollback
## Human decisions required
```

### 阶段 11：审查

先让实现 Agent 自查，再让独立上下文的 Review Agent 只读找问题。Review Agent 不应直接“顺便修”；先输出按严重度排序、带文件/行号和复现证据的问题。实现 Agent 再修复。

Human 重点看：

- 产品语义是否正确；
- 个人事实是否被错误推断；
- UI/摘要是否真的减少判断负担；
- 外部动作是否仍有审批门；
- 迁移/回滚是否可信；
- 证据是否足以合并。

### 阶段 12：合并与清理

合并前：

- 所有 required checks 通过；
- 任务文件记录实际结果；
- owning docs 已更新；
- 未解决问题有新 task ID；
- Human 明确批准。

合并后：

- plan 移入 `docs/plans/completed/`；
- 更新 `docs/current-state.md`；
- 若 worktree 干净且分支已合并，再安全移除；
- 若是数据/行为变化，观察一个定义好的窗口；
- 不因合并成功就立刻删除旧数据或回滚路径。

### 阶段 13：下一轮

从真实结果选择下一任务：

- 用户手工覆盖最多的判断；
- eval 最弱的高风险切片；
- 运行失败最频繁的环节；
- 人每天重复花时间的步骤；
- 文档/实现漂移暴露的系统缺口。

不要把 Agent 自动发现的所有改进立刻排入 active。Agent 可以创建 backlog 建议，人决定优先级。

---

## 8. Job Search OS 的具体实现示例

### 8.1 总体数据流

```text
Collectors
  ↓
SourceObservation（来源事实，不可被 LLM 改写）
  ↓
Canonicalisation（确定性身份 + 冲突保留）
  ↓
CanonicalJob（SQLite 权威状态，示例方案）
  ↓
Deterministic filters（过期、明确地点、已处理、重复）
  ↓
LLM extraction/scoring（版本化分析，不覆盖事实）
  ↓
Priority rules（每日容量、时效、成本、置信度）
  ↓
Daily digest（1–3 Act now；≤5 Review）
  ↓
Human decision
  ├── 高价值不确定 → bounded agent research
  ├── 行动视图 → Notion projection
  └── 经确认的证据/复盘 → Obsidian
```

### 8.2 确定性 scraper/filtering

Software 负责：

- 来源请求、解析、重试、速率限制；
- URL/来源 ID/ATS ID 的规范化；
- 明确日期和地点规则；
- 同源重复；
- 已处理状态；
- 规则版本和理由。

示例输出：

```json
{
  "rule_id": "eligibility.country.v1",
  "result": "UNKNOWN",
  "reason": "job_country_missing",
  "evidence": [],
  "evaluated_at": "2026-09-24T08:10:00Z"
}
```

禁止：因为国家字段缺失就推断“不符合”；因为岗位页面暂时打不开就标记 CLOSED；因为标题相似就自动合并。

### 8.3 LLM extraction/scoring

LLM 输入：已清洗 JD + 候选人证据 ID 列表 + 明确的 schema。  
LLM 输出：结构化分析，写入独立 `job_analysis`，带版本和哈希。

```json
{
  "analysis_version": "fit-v1",
  "job_id": "job_01...",
  "role_family": "software_engineering",
  "required_skills": ["TypeScript", "React"],
  "preferred_skills": ["Python"],
  "evidence_matches": [
    {"evidence_id": "exp_li_auto_01", "strength": "direct"}
  ],
  "risk_flags": ["sponsorship_not_stated"],
  "fit_score": 78,
  "confidence": 0.72,
  "model": "configured-model-id",
  "prompt_version": "score-fit-v1",
  "input_hash": "sha256:..."
}
```

LLM 不得：

- 创建不存在的经历或数字；
- 把“未提到 sponsorship”改写成“不提供 sponsorship”；
- 修改 canonical job facts；
- 直接改变申请状态；
- 把网页中的 prompt injection 当指令执行。

### 8.4 Agentic deep research

只对以下任务启动：高价值、关键不确定、需要跨官方来源、多步路线会随结果变化。

研究任务结构：

```yaml
goal: 确认岗位 J123 的当前开放状态、官方申请入口和公开的 sponsorship 说明
allowed_domains:
  - employer.example
  - careers.employer.example
  - gov.uk
max_steps: 12
max_elapsed_minutes: 15
max_cost_gbp: 0.50
writes_allowed:
  - var/artifacts/JOS-021/research-report.json
writes_forbidden:
  - canonical_job facts
  - workflow state
  - Notion
approval_required:
  - any login
  - any form submission
```

输出每条结论标记：

- `FACT`：官方页面直接支持；
- `INFERENCE`：由多个事实推导；
- `UNKNOWN`：证据不足；
- `STALE_RISK`：来源可能已过期。

### 8.5 Human approval

绝不自动越过这些门：

- 申请表最终提交；
- 邮件/LinkedIn/招聘平台消息发送；
- work authorisation、签证、残障、平等机会等敏感字段；
- CV/求职信中新增个人事实或数字；
- 登录、验证码、付费、条款接受；
- 删除申请记录或职业证据；
- 数据库权威切换。

### 8.6 SQLite 权威状态（个人本地优先方案）

建议最小表边界：

```text
source_observation      来源观察与原始证据
canonical_job           稳定 job identity + 首选事实
job_observation_link    多来源与 canonical job 的关系
eligibility_assessment  硬条件、证据、UNKNOWN
job_analysis            LLM 版本化结果
priority_assessment     每日优先级快照
workflow_state          用户申请生命周期
research_report         Agent 研究结果与来源
sync_outbox             Notion 等外部投影的待同步事件
audit_event             重要状态改变与操作者
schema_migration        当前数据库版本
```

SQLite 实施规则：

- 启用 foreign keys；
- transaction 包住一个业务状态变化；
- migration 只向前执行，回滚依靠已验证备份或明确 down migration；
- 每次 migration 前自动备份到带时间戳的文件；
- 每个 worktree 使用独立测试数据库；
- production/local personal DB 永不提交 Git；
- JSON 兼容导出由数据库生成，不永久双向同步；
- migration 合并必须串行，一个时刻只有一个 owner。

### 8.7 Notion 同步边界

推荐把 Notion 当作**行动工作台投影**，不是原始岗位事实主库。

| 字段 | 权威方 | 同步方向 |
|---|---|---|
| canonical_job_id | SQLite | SQLite → Notion，只读 |
| title/company/location/apply_url | SQLite | SQLite → Notion |
| fit/priority/reasons | SQLite analysis | SQLite → Notion |
| review status | 明确选一个 owner | 初期建议 Notion → SQLite 仅通过受控命令 |
| personal notes | Notion 或 SQLite 二选一 | 不允许无规则双主 |
| submitted_at | Human-confirmed workflow | 受控写回 SQLite |
| raw JD/source payload | SQLite/artifact store | 不同步到 Notion |

同步使用 outbox + idempotency key；失败可重试，不把 Notion 暂时失败解释为主状态丢失。冲突不静默覆盖，进入人工 review queue。

### 8.8 Obsidian 知识边界

Obsidian 保存经人确认的长期职业知识：

- 事实与证据；
- STAR-L 故事；
- 项目贡献；
- 面试复盘；
- 长期能力缺口；
- 最终材料索引。

AI 可以：发现相关证据、起草引用、整理结构、生成待确认草稿。  
AI 不可以：覆盖用户原始故事、创造数字、把推断写成事实、在无人确认时把草稿提升为正式证据。

推荐边界：

```text
Obsidian/Inbox/Agent Drafts     Agent 可写草稿
Obsidian/Verified Evidence     只在 Human 批准后写入
Obsidian/Stories               Human-owned，Agent 可提议 patch
Obsidian/Application History   从 SQLite 生成只读摘要或人工确认后同步
```

### 8.9 Daily digest

Daily digest 应由确定性查询形成骨架：

```text
Act now: 最多 3
Review: 最多 5
Park/Reject: 只显示统计与可展开原因
System health: 抓取失败、数据陈旧、预算、同步失败
Human gates: 今天必须本人确认的事项
```

LLM 可把结构化理由压缩成自然语言，但不能改变候选集合、优先级、eligibility 或状态。摘要必须链接回原始岗位、结构化理由和证据。

---

## 9. Git、Worktree、PR 与并行 Agent

### 9.1 基本规则

- `main` 始终可运行；
- 一任务一 branch；
- 一 branch 一 worktree；
- 一 worktree 一个主要写入 Agent；
- Review Agent 默认只读；
- 不在多个 worktree 共用同一个 SQLite 写文件、端口或生成目录；
- 不把未提交的用户修改复制、覆盖或清理掉。

命名：

```text
feat/JOS-014-sqlite-digest
fix/JOS-027-notion-retry
refactor/JOS-031-collector-boundary
docs/JOS-004-agent-contract
experiment/JOS-040-fit-prompt-v2
```

### 9.2 并行数量

| 成熟度 | 建议并行 | 配置 |
|---|---:|---|
| 初始 0–4 周 | 1–2 | 1 实现；必要时 1 只读审查 |
| 有稳定 CI/任务模板 | 2 | 2 个互不依赖实现，或 1 实现 + 1 eval |
| 有 worktree 隔离与契约测试 | 2–3 | 每任务独立工作区，明确依赖图 |
| 自动编排成熟 | 最多 3 个活跃写任务 | 超过前先证明人能及时审查 |

OpenAI 在 Symphony 文章中报告交互式管理约 3–5 个会话后上下文切换明显痛苦。本项目只有一个 Human Product Owner，且包含个人数据和高风险外部动作，因此把 **3 个写任务视为成熟阶段上限，不是起点**。

### 9.3 什么可以并行

适合：

- 一个 Agent 实现 SQLite repository，另一个只读设计 eval fixture；
- 一个 Agent 改 dashboard，另一个研究 Notion API 契约，但两者不同时改 schema；
- 一个 Agent 实现，另一个在冻结 diff 上审查。

不适合：

- 两个 Agent 改同一 migration 链；
- 两个 Agent 同时重构 canonical model；
- 一个改 schema、另一个基于未合并 schema 写消费者；
- 多个 Agent 写同一个测试数据库或真实 Notion workspace；
- 一个任务尚未确定语义就拆成很多“并行编码”。

### 9.4 PR 大小与合并策略

PR 应围绕一个可验证结果，而非固定行数。优先：

- schema + contract tests；
- repository implementation；
- shadow import + parity report；
- cutover；

不要把 schema、存储迁移、UI 重写、Notion 同步和 LLM prompt 一次合并。

高风险 PR 必须阻塞：migration test、contract test、关键 eval、安全检查、人工批准。低风险文档或小修可以简化，但不能因为 Agent 吞吐高就取消必要门禁。

### 9.5 冲突与集成

- 依赖任务合并后，下游 worktree rebase/merge 最新 main，再重跑验证；
- Agent 可以解决机械冲突，但语义冲突必须报告；
- 不允许为“让测试绿”而删除断言、放宽 schema 或改金标准，除非任务明确授权并有审查；
- migration 编号冲突必须重新编号并重新演练；
- lockfile 冲突由实际依赖变化重新生成，不手拼。

---

## 10. 安全、Guardrails、成本与回滚

### 10.1 Secrets

- 永不编辑真实 `.env`、钥匙串、浏览器 cookie、云端 secret；
- `.env.example` 只含变量名和安全占位符；
- 日志、fixture、截图、PR 不出现 token、邮箱、地址、申请答案等敏感数据；
- Agent 只知道“secret 名称”，不需要值；
- 新集成先用 mock/sandbox；真实连接由人批准；
- secret 轮换使用 runbook，不通过聊天传值。

### 10.2 Migration 规则

采用 expand → migrate → verify → cutover → contract：

1. **Expand:** 新增兼容结构，不删除旧字段；
2. **Migrate:** 在副本/影子路径回填；
3. **Verify:** 数量、哈希、语义、消费者 parity；
4. **Cutover:** 人批准改变权威读写路径；
5. **Contract:** 观察期后另一个任务删除旧路径。

每次 migration 必须：

- 有备份与校验；
- 在临时副本演练；
- 可重复运行或明确检测已运行；
- 记录版本；
- 失败不留下“半成功却继续运行”的状态；
- 有回滚/恢复 runbook；
- 不由两个 Agent 并行修改。

### 10.3 数据不变量

必须最终编码为约束或测试：

1. `canonical_job_id` 不随标题、URL 或 LLM 分类变化；
2. `SourceObservation` 保留来源和观察时间，不能被 LLM 覆盖；
3. source URL 与 direct apply URL 是不同概念；
4. `UNKNOWN` 不等于 `false`、不符合或零分；
5. Job live state 与用户 application state 分离；
6. Eligibility、Fit、Daily Priority 分离；
7. LLM/Agent 输出带版本、模型、prompt、输入哈希、时间和证据；
8. Notion 不是 raw job system of record；
9. Obsidian 中个人事实由用户确认；
10. 未经 Human approval 不发生外部提交或消息发送。

### 10.4 成本限制

成本限制同时在配置、执行和报告层实现：

```yaml
budgets:
  daily_llm_gbp: 2.00
  per_job_analysis_gbp: 0.05
  per_research_task_gbp: 0.50
  max_jobs_llm_per_day: 20
  max_agent_steps: 12
  max_retries: 2
  on_limit: stop_and_queue_for_human
```

以上金额是**个人项目的起始建议，不是 OpenAI 价格承诺**。运行两周后根据真实 token、模型、命中率和价值调整。

成本守则：

- 先 deterministic filter，再 LLM；
- 内容哈希相同就复用分析；
- prompt/model 变化才批量重算，并先跑抽样 eval；
- deep research 只处理人选中的少量岗位；
- 达到预算立即停止，不能静默换更昂贵模型；
- digest 显示当日使用量和被预算推迟的任务数。

### 10.5 Human approval gates

| Gate | Agent 可准备 | Human 必须批准 |
|---|---|---|
| Architecture | ADR 草案、选项、证据 | Accepted 决策 |
| Schema breaking change | migration、parity、回滚 | cutover/删除旧路径 |
| External integration | mock、dry-run、payload preview | 首次真实写入 |
| Application | 草稿、字段检查、材料包 | Submit |
| Sensitive facts | 标出冲突和 `needs-input` | 事实内容 |
| Spend | 预算内执行 | 提升预算 |
| Data deletion | 影响清单、备份、dry-run | 真实删除 |
| Merge | PR、CI、review packet | 高风险 PR 合并 |

### 10.6 Rollback

代码回滚、数据恢复和外部副作用不是同一件事：

- 代码：revert PR 或切回旧 feature flag；
- schema：从已验证备份恢复或执行已验证 down migration；
- 数据：保留错误写入审计，按 idempotency key 修复；
- Notion：从 sync outbox 重放或生成补偿事件；
- LLM：切回旧 prompt/model version，重新生成派生分析；
- 外部申请/消息：通常不可回滚，因此必须在发生前审批。

---

## 11. 评估与质量门

### 11.1 分层指标

| 层 | 主要指标 | 不能只看 |
|---|---|---|
| Scraper | 成功率、字段完整性、新鲜度、来源失败隔离 | 抓到的总数量 |
| Canonicalisation | precision、recall、冲突保留、稳定 ID | 去重后数量 |
| Eligibility | 高风险 false-negative、UNKNOWN 率、证据覆盖 | 总准确率 |
| LLM extraction | 字段级 F1/accuracy、schema pass、关键切片 | 主观“回答不错” |
| Fit scoring | 与人工排序一致性、校准、解释证据 | 平均分 |
| Agent research | 事实可追溯、任务成功率、成本、停止合规 | 最终报告长度 |
| Daily digest | 用户实际处理率、人工判断数、漏掉高价值岗位 | 每日条目数 |
| Integration | 同步延迟、重试、冲突、幂等性 | API 200 次数 |

### 11.2 上线门示例

```yaml
canonical_matching:
  precision_min: 0.98
  recall_not_below_baseline: true
  zero_auto_merge_on_material_conflict: true

eligibility:
  unknown_must_remain_unknown: true
  zero_rejection_from_missing_sponsorship_text: true

llm_extraction:
  schema_pass_rate: 1.0
  prompt_injection_slice_pass_rate: 1.0
  hallucinated_personal_evidence: 0

daily_digest:
  act_now_max: 3
  review_max: 5
  deterministic_membership: true
```

阈值是项目拟定标准；必须用真实样本验证并由你确认，而不是因为模板里写了就自动成为事实。

### 11.3 失败如何反馈到 harness

| 失败 | 首选系统修复 |
|---|---|
| Agent 不知道当前数据权威 | 更新导航/architecture，并加 ownership check |
| 重复把 UNKNOWN 当 false | 加 schema enum + 回归测试 + invariant |
| 误改个人故事 | 限制写路径 + approval gate + ownership metadata |
| 迁移后消费者坏 | 加 contract/parity test 和 cutover checklist |
| 相同手工步骤反复出现 | 写脚本/runbook；成熟后才自动化 |
| Prompt 对一个例子有效、整体退化 | 扩 eval fixture，不继续盲调 |
| Agent 经常卡在缺少工具 | 提供受限工具或明确停止条件，不给无界权限 |

---

## 12. 分阶段采用路线

### Phase 0 — 一次只做一个可验证任务（1–2 周）

目标：建立基本纪律，不改系统架构。

- 精简 `AGENTS.md`；
- 建 `docs/current-state.md` 和一个 `docs/plans/active/` 下的 active plan；
- 记录真实测试命令；
- 使用 branch + PR；
- 每个任务有验收与验证结果；
- 不并行写任务。

退出条件：你可以关闭聊天后，仅凭仓库文档让另一个 Codex 续接任务。

### Phase 1 — 仓库可读、契约可执行（2–6 周）

目标：把关键知识从脑中/聊天中移入仓库。

- CURRENT/TARGET 架构；
- Canonical Job 设计与 schema；
- 数据和安全 invariants；
- unit/contract tests；
- runbook 与 PR 模板；
- 文档链接/状态检查。

退出条件：Agent 能从小 `AGENTS.md` 找到正确文档，关键错误会被 CI 拦截。

### Phase 2 — 受控的 Agent 开发（1–3 个月）

目标：让 Codex 完成实现—验证—文档—PR 的完整闭环。

- task/agent brief 模板；
- worktree 隔离；
- 独立 review Agent；
- SQLite/目标存储的影子迁移与 parity；
- LLM eval；
- 明确人工审批门；
- 同时最多 2 个任务。

退出条件：大多数常规任务无需逐步指挥，但仍产生完整证据包。

### Phase 3 — 任务平台成为控制平面（3–6 个月）

目标：减少你管理多个会话的认知负担。

- GitHub Issues/项目看板或 Linear 映射任务状态；
- 每个 ready task 自动创建隔离工作区；
- 自动回报进度、CI、PR 和阻塞；
- Agent 可创建 backlog 建议，但不能自行提优先级；
- 同时最多 2–3 个低耦合任务。

退出条件：你管理 deliverables，而不是盯会话；失败会安全停止并留下可续接状态。

### Phase 4 — 最小 Symphony-like 编排（按需，而非必做）

只有当这些条件持续成立才做：

- 每周有大量重复、清楚、低风险任务；
- 人工开会话成为可测量瓶颈；
- CI、回滚、成本和审批已成熟；
- 任务状态与工作区可可靠恢复；
- 你能及时审查产生的 PR。

最小编排器只需要：

- 轮询 ready task；
- 为每项任务保证一个隔离 Agent/workspace；
- 记录 lease/heartbeat；
- 崩溃后恢复；
- 达到 review/blocked 后停止；
- 不自动越过 human gate。

不要先实现复杂 supervisor、多个专用 Agent 角色和自动合并。先证明单 Agent + 好 harness 的收益。

---

## 13. 可复制的 Markdown 模板

### 13.1 Agent Brief

```markdown
---
task_id: JOS-000
status: ready
owner: human-name
primary_agent: unassigned
branch: null
worktree: null
risk: low | medium | high
human_gate: none | architecture | external-write | migration | merge
---

# Agent Brief — <结果导向标题>

## Objective
任务完成时，什么可观察状态必须成立？

## Why now
它解决哪个用户痛点或阻塞？

## Must read
- `AGENTS.md`
- `<相关文档>`

## Current evidence
- 当前行为：
- 代码/配置位置：
- 已验证与未验证：

## Scope
- 可以修改：
- 可以创建：

## Non-goals
- 明确不做：

## Constraints and invariants
- 不得破坏：
- 兼容性：
- 数据/隐私：

## Acceptance evidence
1. <可执行检查与预期结果>
2. <可见行为>
3. <文档/迁移/回滚证据>

## Allowed tools and data
- 允许：
- 禁止：

## Human approval gates
- 在执行 <动作> 前暂停并提交 <预览/证据>。

## Blocked stop condition
当 <条件> 成立时停止，记录尝试、证据、风险和所需输入；不要猜测或扩大范围。

## Deliverables
- 代码/文档/测试：
- Review packet：
```

### 13.2 Task Spec / ExecPlan

```markdown
---
task_id: JOS-000
status: proposed | ready | active | review | blocked | done
last_updated: YYYY-MM-DD
base_revision: <sha>
branch: <branch>
risk: low | medium | high
---

# <任务标题>

## Purpose / Big Picture
问题、用户价值、完成后的可见结果。

## Context and Orientation
相关模块、当前数据流、术语、已检查证据。

## Scope
- ...

## Non-goals
- ...

## Compatibility constraints
- API/CLI：
- 数据：
- 工作流：
- UI/导出：

## Plan of work
1. ...
2. ...

## Concrete steps
| Step | Files/commands | Expected result | Status |

## Acceptance criteria
- [ ] ...

## Validation
| Check | Expected | Actual | Evidence |

## Failure, idempotence and recovery
- 重跑：
- 部分失败：
- 回滚：

## Interfaces and dependencies
- 外部系统：
- 凭据名（不含值）：
- 前置任务：

## Human gates
- ...

## Progress
- YYYY-MM-DD：...

## Surprises and discoveries
- ...

## Decision log
- YYYY-MM-DD：决定 / 原因 / 是否提升为 ADR

## Outcomes and retrospective
- Delivered：
- Deviations：
- Residual work：
- Lessons：
```

### 13.3 Acceptance Criteria

```markdown
# Acceptance Criteria — <feature>

## Functional
- Given <初始状态>, when <动作>, then <可观察结果>.

## Data contract
- [ ] 输入不合法时 fail closed / 明确 UNKNOWN。
- [ ] 输出通过 `<schema>`。
- [ ] 旧消费者仍通过 contract test。

## Safety
- [ ] 无外部写入，或写入前有人工批准。
- [ ] 不读取真实 secrets。
- [ ] 不将推断写成个人事实。

## Reliability
- [ ] 重跑幂等。
- [ ] 部分失败可恢复。
- [ ] 日志可定位失败且不含敏感数据。

## Evidence required
- [ ] 命令与结果：
- [ ] Eval 报告：
- [ ] Screenshot/artifact：
- [ ] Rollback proof：
```

### 13.4 Architecture Decision Record

```markdown
# ADR-XXXX — <决定标题>

- Status: Proposed | Accepted | Rejected | Superseded
- Date: YYYY-MM-DD
- Deciders: <Human owner>
- Supersedes: <ADR or none>

## Context
必须作出什么决定？现有事实、约束和冲突是什么？

## Decision drivers
- ...

## Options considered

### Option A — <name>
- Benefits:
- Costs/risks:
- Reversibility:

### Option B — <name>
- Benefits:
- Costs/risks:
- Reversibility:

## Decision
选择什么；明确不选择什么。

## Consequences
- Positive:
- Negative:
- Follow-up work:

## Validation and exit criteria
如何证明决定有效？什么情况触发重审？
```

### 13.5 Bug Report

```markdown
# Bug — <可观察症状>

## Impact
影响谁、多少数据、是否阻塞或有安全风险？

## Environment
- revision:
- OS/runtime:
- database/schema version:
- config mode（不含 secret）:

## Steps to reproduce
1. ...

## Expected
...

## Actual
...

## Evidence
- logs:
- fixture:
- screenshot:

## First known occurrence
...

## Suspected scope
只写证据支持的范围，不把猜测当根因。

## Safety / data notes
是否可能影响个人数据、同步或外部动作？

## Acceptance for fix
- [ ] 先用测试重现。
- [ ] 修复后测试通过。
- [ ] 无相关回归。
- [ ] 必要的 runbook/docs 已更新。
```

### 13.6 Refactor Plan

```markdown
# Refactor Plan — <boundary>

## Motivation
可测量问题：重复、依赖方向、测试困难、故障率等。

## Behaviour to preserve
- ...

## Current dependency map
...

## Target boundary
...

## Sequence
1. 增加 characterization tests。
2. 建新接口/adapter。
3. 逐个迁移消费者。
4. 验证 parity。
5. 单独任务删除旧路径。

## Forbidden changes
- 不改变产品语义。
- 不顺便改 schema。
- 不替换未相关依赖。

## Verification
- ...

## Rollback
- ...
```

### 13.7 Experiment Log

```markdown
# Experiment — <hypothesis>

- Date:
- Owner:
- Code revision:
- Dataset version:
- Model/prompt version:
- Budget:

## Hypothesis
如果做 X，指标 Y 会改善，同时 Z 不退化。

## Baseline
| Metric | Value |

## Change under test
只描述本次变量。

## Procedure
可重复命令和环境。

## Results
| Metric/slice | Baseline | Candidate | Delta | Pass? |

## Failure examples
- fixture id:
- expected:
- actual:
- interpretation:

## Cost and latency
- ...

## Conclusion
Adopt | Iterate | Reject；原因。

## Follow-up
- ...
```

### 13.8 Review Checklist

```markdown
# Review Checklist — <PR/task>

## Intent and scope
- [ ] Diff 实现 Task Spec，而非扩大范围。
- [ ] 非目标没有被顺手实现。

## Correctness
- [ ] 验收标准有实际证据。
- [ ] 测试覆盖失败路径和 UNKNOWN。
- [ ] 未通过放宽断言/改金标准隐藏失败。

## Data and migrations
- [ ] 身份、来源和状态边界保持。
- [ ] migration 在副本演练。
- [ ] 备份、幂等和恢复已验证。

## LLM/Agent
- [ ] 输出 schema 验证。
- [ ] model/prompt/input hash 可追踪。
- [ ] 固定 eval 与高风险切片通过。
- [ ] 成本和停止条件有效。

## Security and privacy
- [ ] 无 secret/PII 泄露。
- [ ] 权限最小化。
- [ ] 外部动作停在 approval gate。

## Documentation
- [ ] owning docs 已更新。
- [ ] CURRENT/TARGET 没有混淆。
- [ ] 任务记录真实验证和已知限制。

## Operations
- [ ] 日志足以排障。
- [ ] rollback 可执行。
- [ ] 监控/观察期明确。

## Human review
- [ ] 产品语义正确。
- [ ] 个人事实由用户确认。
- [ ] 高风险改变获明确批准。
```

### 13.9 Work Log

```markdown
## Work Log

### YYYY-MM-DD HH:MM TZ
- Goal for this step:
- Action:
- Result:
- Evidence:
- Interpretation:
- Decision / next step:
- Blocker, if any:
```

---

## 14. 三个完整的指挥示例

### 示例 A：实现确定性 eligibility filter

对 Codex 说：

```markdown
先只读检查当前地点、签证、工作方式的字段和过滤路径，写 JOS-101 Task Spec；不要改代码。
把明确事实、缺失字段和推断分开。验收必须包含：UNKNOWN 不被当成 INELIGIBLE；
JD 未写 sponsorship 不得产生拒绝；每条结果保存 rule_id/version/evidence。
列出与现有 JSON、dashboard、notification 的兼容面，并给出最小实现顺序。
```

你审核 Task Spec 后再说：

```markdown
JOS-101 已批准。请在独立 worktree 实现 Milestone 1：纯规则引擎和 fixtures。
不接真实 scraper、不修改 UI。完成后运行 unit/contract tests，更新任务进度，提供 diff 和结果；不要 merge。
```

### 示例 B：改进 LLM Fit Score

```markdown
目标不是“让解释更好看”，而是提升 fit-v1 在冻结 eval 集上的排序一致性。
先跑 baseline，记录模型、prompt、代码、成本和每个切片结果。只能修改 prompts/score-fit-v2.md
和候选解析器；不能改 expected/，不能新增个人经历。候选版本若总体提升但 sponsorship_unknown
切片退化，则判定失败。最终提交 experiment log，不要自动切换生产版本。
```

### 示例 C：Notion 同步

```markdown
请实现 Notion dry-run exporter，只生成将要写入的 payload，不调用真实 Notion。
字段所有权以 ADR-0002 为准；raw JD、个人敏感字段和未确认申请状态不得进入 payload。
用固定 fixture 验证幂等 key，相同事件重跑不得产生第二条 create。
完成后给我 payload 示例、contract tests、失败重试设计和首次真实写入前的 approval checklist。
```

---

## 15. 每周与每月维护节奏

### 每个任务

- 开始：Definition of Ready；
- 进行：Agent 更新 progress/work log；
- 合并：review packet + Definition of Done；
- 完成：更新 current state，残余问题进入 backlog。

### 每周 30 分钟

- 清理 stale active/blocked task；
- 看失败最多的 CI/eval；
- 审查 Agent 新建的 backlog 建议；
- 检查成本与重试；
- 选择下一周最多 1–2 个 active 目标。

### 每月 60–90 分钟

- 运行 doc-gardening 检查；
- 重审 `AGENTS.md`，删除已无必要的指令；
- 检查架构 CURRENT 与真实代码；
- 复核权限、secret、备份恢复；
- 看人工覆盖/纠正最多的系统判断；
- 更新 eval 数据的代表性，但由 Human 审查金标准；
- 决定是否提高并行度，默认不提高。

### 每季度

- 重新确认 Job Search OS 是否真的减少人工判断；
- 检查 Notion/Obsidian 边界是否漂移；
- 演练 SQLite/权威存储恢复；
- 复核外部集成和数据保留；
- 决定下一阶段是否需要更强自动编排。

---

## 16. 最终 Definition of Done

一个 Agent 完成的任务只有同时满足以下条件才算 Done：

- [ ] 用户想要的可观察结果已实现；
- [ ] 范围没有未经批准扩大；
- [ ] 相关自动测试真实运行并记录结果；
- [ ] LLM/Agent 行为经过固定 eval，而非只看演示；
- [ ] 数据迁移在副本演练，备份与恢复可执行；
- [ ] 安全、不变量、成本和审批门仍有效；
- [ ] owning docs 反映新现实；
- [ ] CURRENT、TARGET、PROPOSED 没有混淆；
- [ ] PR/review packet 足以让人快速判断；
- [ ] 已知限制和未完成项有明确 task ID；
- [ ] Human 对高风险语义和合并作出批准；
- [ ] 下一次 Agent 可以仅凭仓库继续工作。

如果其中任何一项无法满足，正确状态是 `REVIEW` 或 `BLOCKED`，不是“差不多完成”。

---

## 17. 结论

OpenAI 的两篇文章最值得迁移的并不是“让 Agent 写所有代码”，而是把工程工作重新定义为：

1. 人写清楚意图、价值和不可越过的边界；
2. 仓库向 Agent 暴露当前事实、目标、工具和验证方法；
3. 软件把关键约束变成可执行检查；
4. Agent 在隔离环境里完成任务并产生证据；
5. 人审查结果和高风险决定；
6. 每次失败都让 harness、文档、测试或工具变得更完整。

对 Job Search OS 来说，最成功的 agent-first 结果不是每天产生更多代码或更多岗位，而是：系统可靠保存事实，把重复判断变成软件，把有限语义任务交给 LLM，把少量多步研究交给 Agent，并把你的注意力留给职业方向、真实经历、申请质量和最终决定。

---

## 参考资料

1. Ryan Lopopolo, OpenAI, [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/), 2026-02-11.
2. Alex Kotliarskyi, Victor Zhu, Zach Brock, OpenAI, [An open-source spec for Codex orchestration: Symphony](https://openai.com/index/open-source-codex-orchestration-symphony/), 2026-04-27.
3. OpenAI Developers, [Codex](https://developers.openai.com/learn/codex).
4. OpenAI Developers Cookbook, [Using Goals in Codex](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex).
