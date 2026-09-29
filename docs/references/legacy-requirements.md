> **Superseded scope — historical reference.** This document describes an earlier
> project scope and is retained without rewriting its historical content. It is
> no longer authoritative for the current Job Search OS roadmap. Current direction
> is defined by [the current roadmap](../roadmap.md); current agent operating rules are defined
> by [AGENTS.md](../../AGENTS.md). Its phase numbers and database/Notion prohibitions
> belong to that earlier scope.

# ScottCoffin Job_Scraper — Codex 分阶段改造执行方案

## 一、总体执行原则

本次改造的目标不是重写 ScottCoffin/Job_Scraper，而是在保留现有采集、去重和数据管线能力的前提下，将其逐步定制为：

> **UK-primary + China-compatible remote 的个人 Job Discovery & Triage System**

当前阶段重点解决：

> 找到正确的岗位，并让我能够快速筛选。

暂时不要扩展为完整 Career OS。

---

# 二、Codex 每一个阶段都必须遵守的规则

在任何阶段开始修改前，都遵守以下原则：

1. **先读后改**

   * 先指出涉及哪些文件；
   * 当前逻辑在哪里；
   * 哪些既有行为需要保留；
   * 哪些测试已经覆盖。

2. **最小修改**

   * 不主动重构整个 `scrape_jobs.py`；
   * 不因为“代码不够漂亮”而进行 unrelated refactor；
   * 不同时修改多个无关模块。

3. **配置优先**
   所有用户特定的：

   * 搜索关键词；
   * 地点；
   * role family；
   * seniority；
   * exclusions；
   * scoring weights；
   * remote rules；

   尽可能进入配置，而不是硬编码进 Python。

4. **Hard Filter 和 Ranking 分离**
   只有明确不适合的岗位才能 Hard Filter。

   技能不完全匹配、Senior、地点一般、remote eligibility 不明确等情况应该保留并降权，而不是直接删除。

5. **Deterministic first**
   Phase 1 不使用 Claude / LLM 决定岗位是否适合。

6. **向后兼容**
   新增字段时，旧的 JSON 数据仍应能够被加载。

7. **每阶段测试**
   每完成一个阶段：

   * 跑现有测试；
   * 新增针对该功能的测试；
   * 给出测试结果；
   * 列出修改文件；
   * 列出仍然没有处理的内容。

8. **不要提前做下一阶段**
   当前阶段 acceptance criteria 没通过前，不继续下一阶段。

---

# 三、Phase 0 — 建立可验证的 Baseline

## 目标

在修改功能之前，先让当前仓库进入一个：

> 可以可靠判断“改坏了没有”的状态。

这是整个改造里最重要但最容易被跳过的一步。

---

## Codex 任务

首先不要修改产品行为。

完成：

### 1. 安装并运行现有测试

确认：

```text
pytest
```

当前：

* 有多少测试；
* 多少通过；
* 多少失败；
* 失败原因是什么。

如果依赖缺失，建立合适的本地开发环境。

---

### 2. 验证关键入口

至少确认：

```text
scrape_jobs.py
triage_agent.py
notify.py
eval_triage.py
```

可以 import / parse。

---

### 3. 建立 baseline report

输出：

```text
Current baseline

Tests:
XX passed
XX failed

Existing known inconsistencies:
...

Enabled sources:
...

Current output schema:
...

Current workflow schedule:
...
```

---

### 4. 不修功能

这一阶段除了：

* dependency / test setup；
* 明显影响测试运行的环境问题；

不要修改业务逻辑。

---

## Phase 0 Acceptance Criteria

必须能够回答：

> 如果下一次修改破坏了现有 scraper，我是否能够知道？

如果答案还是“不知道”，Phase 0 没完成。

---

## 给 Codex 的指令

请先不要实施 UK 化或修改产品功能。

你的任务是建立当前仓库的可验证 baseline。

1. 安装并运行现有测试。
2. 记录测试总数、通过数、失败数和失败原因。
3. 检查主要 Python 入口是否可以正常 import/parse。
4. 总结当前启用的数据源、主数据 Schema、关键 GitHub Actions。
5. 列出你之前识别到的已知不一致，但本阶段先不要修复。
6. 除测试环境或依赖问题外，不进行业务重构。

最后给出：

* 修改文件；
* 测试结果；
* baseline 状态；
* 下一阶段开始前仍存在的问题。

完成后停止，不要继续修改其他功能。

---

# 四、Phase 1 — 清理原项目遗留领域配置

## 目标

把原作者个人求职领域留下的：

* toxicology；
* environmental science；
* biotech；
* US government；
* California；

等内容从你的实际运行路径中清出去。

但不是现在就删除所有代码。

重点是：

> **disable，而不是 destructive rewrite。**

---

## Codex 任务

### 1. 修复明确 bug

例如：

```text
--biotech-only
```

和：

```text
--priority-only
```

不一致的问题。

先判断该 workflow 对未来是否还有用途。

如果本身完全属于旧 Priority Digest：

优先 disable workflow，而不是给它继续加兼容代码。

---

### 2. Disable US-specific sources

默认关闭：

```text
USAJOBS
CalCareers
CalOpps
CSU Careers
GovernmentJobs / NEOGOV
```

代码暂时保留。

---

### 3. Disable AI Triage

暂时关闭：

```text
Nightly AI Triage
eval_triage
Anthropic scoring workflow
```

不要删除：

```text
triage_agent.py
eval_triage.py
```

只是让它们不参与当前 production workflow。

---

### 4. 统一 30-day retention

把：

```text
14 days
30 days
```

不一致的文档 / 配置统一为：

```text
30-day rolling operational job store
```

---

### 5. 清理示例领域配置

确保默认运行时不会继续使用 toxicology / environmental-science 的示例设置。

---

## Phase 1 Acceptance Criteria

运行系统时：

* 不会主动抓美国公共部门岗位；
* 不会自动启动旧 AI scoring；
* 不再依赖 toxicology / biotech 配置；
* 30-day retention 描述一致；
* 原有通用 scraper 能力没有被删除。

---

# 五、Phase 2 — 建立新的 Personal Config

## 目标

这一阶段**先不增加复杂算法**。

先把系统真正改成：

> Ivy / Wei 的搜索范围。

---

## 核心原则

个人需求应该尽量集中在：

```text
config.json
```

或专门的 configuration section。

不要散落在：

```python
if "AI Engineer" ...
if location == "London" ...
```

这样的代码中。

---

## Role Families

建立：

```text
AI Application / AI Engineer
Product Engineer
Full-stack
Frontend + AI
Frontend
Software Engineer
Solutions / Developer Tools
Graduate / Early Career
Other
```

---

## Primary Search Terms

包括：

```text
AI Engineer
Applied AI Engineer
AI Application Engineer
Generative AI Engineer
GenAI Engineer
LLM Engineer
AI Product Engineer

Product Engineer

Full Stack Engineer
Full-stack Software Engineer

Frontend Engineer
Frontend Software Engineer

Software Engineer
Software Developer

Developer Tools Engineer
Developer Experience Engineer
Developer Productivity Engineer
```

---

## UK Search Geography

包括：

```text
United Kingdom
London
Birmingham
Coventry
Manchester
Cambridge
Oxford
Bristol
Edinburgh
Leeds
Reading
UK Remote
```

---

## International Remote Search

额外建立独立 remote search bucket：

```text
Remote
Worldwide
Global
Anywhere
APAC
Asia
China
```

注意：

> 这些只是 discovery query。

不能因为搜索结果写 `Remote` 就自动认定 China Eligible。

---

## Relevant Skills

配置：

### Existing strengths

```text
React
TypeScript
JavaScript
Vue
Frontend
Web Application
API
Data Visualisation
Developer Tools
```

### AI transition strengths

```text
Python
LLM
Generative AI
AI Agents
RAG
Machine Learning
AI API
Evaluation
```

### Development opportunities

```text
AWS
Docker
Kubernetes
FastAPI
PostgreSQL
Vector Database
LangChain
LlamaIndex
Observability
CI/CD
```

第三类不能成为 exclusion。

---

## Negative / exclusion domains

例如：

```text
Data Analyst
Business Analyst
Research Scientist
Quant Research
Embedded
Firmware
Hardware
IT Support
Manual QA
UX Designer
```

注意不要简单做 substring filter。

例如：

> Software Engineer building analytics tools

不能因为出现 analytics 就被过滤。

---

## Phase 2 Acceptance Criteria

配置文件本身能够清楚回答：

> 我在找什么工作？

且以后调整职业方向时，不需要大量修改 scraper Python。

---

# 六、Phase 3 — Role Classification

## 目标

让系统不仅知道：

```text
title = Software Engineer
```

而且知道：

```text
role_family = AI Application / AI Engineer
```

---

## 实现方式

第一版只做 deterministic classifier。

输入可以包含：

```text
title
description
company context
```

但 title 权重最高。

---

## 重要要求

允许一个岗位有：

```text
primary_role_family
```

第一版不需要复杂 multi-label taxonomy。

例如：

```text
AI Product Engineer
→ AI Application / AI Engineer
```

```text
Senior Frontend Engineer — AI Platform
→ Frontend + AI
```

```text
Software Engineer
→ Software Engineer
```

---

## 必须增加测试

建立 representative cases：

```text
AI Application Engineer
Frontend Engineer, AI
Senior Product Engineer
Software Engineer — Generative AI
Data Scientist
Staff AI Engineer
```

检查分类。

---

## Acceptance Criteria

抽样至少 30 个真实 / fixture title：

> 大部分分类结果符合人的直觉。

---

# 七、Phase 4 — Geography 与 Remote Eligibility

这是整个需求中最容易写错的一层，因此独立实现。

---

## 目标

区分：

```text
work_mode
```

和：

```text
remote_geo_eligibility
```

---

## Work Mode

统一：

```text
Remote
Hybrid
On-site
Unknown
```

---

## Remote Geo Eligibility

统一：

```text
UK Only
China Eligible
Global / Worldwide
APAC — China Included
APAC — China Unclear
Remote — Region Restricted
Location Unclear
Not Remote
```

---

## 判断来源

不能只读 `location`。

需要综合：

```text
location
description
employment eligibility text
timezone text
```

---

## 关键行为

### Case 1

```text
Remote — US only
```

→ Remote
→ Region Restricted

### Case 2

```text
Remote worldwide
```

→ Remote
→ Global / Worldwide

### Case 3

```text
Remote across APAC, including China
```

→ Remote
→ APAC — China Included

### Case 4

```text
Fully remote
```

没有其他说明。

→ Remote
→ Location Unclear

不能自动变成 China Eligible。

---

## 重要原则

`Unclear`：

> 保留。

不要 Hard Filter。

---

## 必须加入单元测试

至少测试：

* US only；
* UK only；
* Europe only；
* worldwide；
* anywhere；
* APAC；
* APAC including China；
* remote without geography；
* hybrid London；
* China remote。

---

# 八、Phase 5 — Experience / Seniority Extraction

## 目标

解决：

> 一个岗位职位名看起来合适，但实际上要求 10 年怎么办？

---

## 新增

```text
seniority
experience_min
experience_max
```

---

## Seniority

至少：

```text
Graduate
Junior
Mid
Senior
Staff
Principal
Manager
Unknown
```

---

## Hard Exclusions

明确：

```text
Staff
Principal
Director
VP
Engineering Manager
Head of ...
```

默认排除。

---

## Senior 不自动排除

例如：

```text
Senior Software Engineer
4+ years
```

仍然可以保留。

---

## Experience

尝试识别：

```text
3+ years
3-5 years
minimum five years
at least 8 years
```

---

## 用户目标

大体优先：

```text
2–6 years
```

但不要把：

```text
experience unknown
```

删除。

---

# 九、Phase 6 — Canonical Job Schema

前五阶段稳定以后，再统一 Schema。

不要一开始就把几十个字段全部加进去。

---

## 第一版真正需要的新增字段

建议先增加：

```text
role_family

work_mode
remote_geo_eligibility

seniority
experience_min
experience_max

matched_keywords

match_score
match_reasons
```

其他例如：

```text
timezone_fit
remote_employment_model
visa_note
```

可以下一轮加。

---

## 要求

更新：

```text
schema/jobs.schema.json
```

同时做到：

> 老数据缺新字段时仍然可以加载。

不要要求迁移 438 条旧数据才能打开 Dashboard。

---

# 十、Phase 7 — Deterministic Matching

这个阶段才开始真正回答：

> 哪些岗位应该排前面？

---

## 不要做成一个巨大公式

建议分成几组 signal：

```text
Role Fit
Technical Fit
AI Relevance
Experience Fit
Geography Fit
Penalty
```

然后合成：

```text
match_score
```

---

## 示例

Role:

```text
Target role family +20
Secondary role family +8
```

Technical:

```text
React +3
TypeScript +3
Python +3
```

AI:

```text
LLM +5
Generative AI +5
AI agent +5
RAG +4
```

Career crossover：

```text
Frontend + AI +5
Product engineering +4
Developer tools +4
```

Geography:

```text
UK eligible +4
China eligible remote +4
Global remote +3
```

Penalty：

```text
Staff -30
Principal -40
10+ years -30
US-only -30
```

具体权重以后通过结果调。

---

## 最重要的输出不是 Score

同时必须生成：

```text
match_reasons
```

例如：

```text
React · TypeScript · LLM · AI product
```

这样才能人工判断算法有没有犯傻。

---

# 十一、Phase 8 — Dashboard 改造

**只有数据层已经稳定以后才改 UI。**

否则 Codex 会同时 debug Python 和 2600 行 HTML。

---

## 第一版首页

不要先做复杂 redesign。

建立两个主要 View：

```text
UK Opportunities
Remote Opportunities
```

---

## 默认状态

```text
Past 7 days
+
Unreviewed
+
Sort by Match Score / Freshness
```

---

## Job Card

最重要展示：

```text
Company
Role
Role Family

Location
Work Mode
Remote Eligibility

Posted / First Seen

Match Score
Match Reasons

Experience

Salary

Direct Apply
```

---

## Filters

第一版：

```text
Role Family
Location
Work Mode
Remote Eligibility
Seniority
Freshness
Match Score
Source
```

其他 later。

---

# 十二、Phase 9 — Initial Triage State

现在再实现：

```text
Unreviewed
Shortlist
Skip
```

而不是一口气做：

```text
Applied
OA
Interview
Offer
...
```

---

## 当前目标

你每天应该可以：

```text
20 new jobs
     ↓
5 Shortlist
15 Skip
```

---

## localStorage

Phase 1 可以保留。

但是确认：

* Export；
* Import；

是否仍然可用。

如果没有，补一个最小 backup/export。

---

# 十三、Phase 10 — GitHub Actions

这一阶段最后做，而不是一开始改 scheduler。

先确认 scraper 本地效果正确。

---

## 删除 / Disable

不需要的：

```text
US government watchers
old priority watchers
AI triage workflow
old domain digest
```

---

## 第一版 Schedule

不要全部 hourly。

例如：

```text
LinkedIn        every 4–6h
Google Jobs     every 4–6h

Indeed          2–4 times/day
Glassdoor       2–4 times/day
HiringCafe      2–4 times/day
```

后续 ATS：

```text
1–2 times/day
```

---

## 必须继续保留

现有：

```text
job-scraper-commit-push
```

一类 concurrency protection。

避免 workflow 互相覆盖 Git commit。

---

# 十四、Phase 11 — 真实数据验收

这个阶段非常关键。

**不能只靠 pytest 通过判断成功。**

实际跑一次：

```text
UK searches
+
remote searches
```

然后随机人工检查至少：

```text
50–100 jobs
```

---

## 统计

让 Codex 输出：

```text
Total collected

UK:
xx

Remote:
xx

Role distribution:
...

Hard filtered:
...

Unclear geography:
...

Senior/Staff:
...

Top 20 score:
...
```

---

## 你人工回答三个问题

### Question 1

前 20 个岗位里：

> 有多少是真正会考虑申请的？

### Question 2

被过滤的岗位里：

> 有没有明显应该保留却被系统删掉的？

### Question 3

Remote View 中：

> 有没有大量 US-only / EU-only 被错误认为适合？

这三个比 unit test 更重要。

---

# 十五、不要让 Codex 做的事情

整个 Phase 1 周期明确禁止：

```text
Do not rewrite scrape_jobs.py from scratch.

Do not migrate the project to a new framework.

Do not introduce a backend server.

Do not add a database.

Do not add Notion integration.

Do not implement auto-apply.

Do not rebuild triage.html using React.

Do not re-enable Claude scoring.

Do not redesign every workflow simultaneously.

Do not remove existing generic scrapers simply because they are currently disabled.
```

---

# 十六、建议的 Git Commit 节奏

建议每阶段独立 commit。

例如：

```text
chore: establish test baseline

chore: disable legacy domain workflows

feat: add UK and international remote search config

feat: classify target role families

feat: classify remote geographic eligibility

feat: extract experience and seniority

feat: extend canonical job schema

feat: add deterministic job fit scoring

feat: update triage dashboard for UK and remote views

feat: add initial review states

chore: simplify and reschedule job watchers
```

这样一旦某一步效果不好，非常容易回退。

---

# 十七、每次给 Codex 的标准任务模板

以后每一个阶段都可以使用下面这个模板：

## Task

Implement **[PHASE NAME]** only.

## Context

This repository is being adapted into a:

> UK-primary + China-compatible remote Job Discovery & Triage System.

The priority is search precision and explainability, not large-scale architectural refactoring.

## Before coding

First inspect the relevant implementation and report:

1. Which files are involved.
2. What the current behaviour is.
3. Which existing behaviour must remain unchanged.
4. Which existing tests cover this area.
5. Your proposed minimal implementation.

Do not modify code until this analysis is complete.

## Implementation constraints

* Do not refactor unrelated code.
* Do not redesign `scrape_jobs.py`.
* Prefer configuration over user-specific hard coding.
* Preserve backward compatibility with existing JSON.
* Keep hard filtering conservative.
* Do not introduce LLM dependencies.
* Do not modify unrelated GitHub Actions.
* Do not proceed to later phases.

## Tests

Add tests covering the new behaviour and regression cases.

Run the relevant test suite after implementation.

## Completion report

When complete, report:

1. Files changed.
2. Behaviour added/changed.
3. Tests added.
4. Test results.
5. Any known limitations.
6. Any assumptions made.
7. What remains for the next phase.

Then stop.

---

# 十八、推荐实际执行顺序

最终执行顺序：

```text
Phase 0
Baseline
   ↓
Phase 1
Legacy cleanup
   ↓
Phase 2
Personal config
   ↓
Phase 3
Role classification
   ↓
Phase 4
UK / Remote geography
   ↓
Phase 5
Experience / seniority
   ↓
Phase 6
Schema
   ↓
Phase 7
Deterministic scoring
   ↓
Phase 8
Dashboard
   ↓
Phase 9
Triage state
   ↓
Phase 10
GitHub Actions
   ↓
Phase 11
Real-world evaluation
```

核心原则是：

> **先让数据判断正确，再让 UI 好用，最后再让它自动运行。**

不要倒过来。
