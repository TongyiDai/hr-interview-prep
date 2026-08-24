<h1 align="center">岗位面试设计</h1>

<p align="center">
  <a href="https://github.com/TongyiDai/hr-interview-prep/actions/workflows/ci.yml"><img src="https://github.com/TongyiDai/hr-interview-prep/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/Agent%20Skill-agentskills.io-2F6BFF" alt="Agent Skill">
  <img src="https://img.shields.io/badge/license-Apache%202.0-3fb950" alt="License Apache 2.0">
  <img src="https://img.shields.io/badge/python-%3E%3D3.8-3572A5" alt="Python >=3.8">
  <img src="https://img.shields.io/badge/works%20with-Codex%20|%20Claude%20|%20Cursor%20|%20TRAE-555" alt="Works with major agents">
</p>

`hr-interview-prep`

一个可复核、可本地运行、支持多种材料来源的中文结构化面试 Skill。飞书只是可选适配，使用本地材料也能完整运行。

<p align="center">
  <img src="assets/hr-interview-prep-demo.gif" alt="岗位胜任力 → 结构化面试包（全程脱敏假数据）" width="900" />
</p>

<p align="center"><sub>岗位胜任力 → 结构化面试包（全程脱敏假数据）</sub></p>

## 价值与适用场景

它把岗位说明变成面试团队可以共同执行的面试包：先说清岗位结果，再建立胜任力、统一问题、面试官覆盖、锚定评分和复盘证据。岗位面试设计更一致，面试后的讨论也更容易回到事实。

适合这些工作：

- 新岗位启动前，设计面试轮次和面试官分工。
- 为同一岗位准备统一的行为题、情境题和追问。
- 检查面试轮次有没有重复提问或能力漏测。
- 准备 1–4 分行为锚定评分表。
- 面试官独立提交反馈后，整理证据、分歧和待验证问题。
- 把本地消息、邮件、岗位文档、历史面试材料或 HR 口述整理成统一面试框架。
- 在岗位面试包完成后，基于脱敏简历生成候选人针对性核验问题。

它帮助团队准备和整理面试材料，录用、淘汰、排序和合规判断仍由人类完成。

## 这个 Skill 产出什么

每份面试包包含：

- 岗位关键工作结果与设计假设。
- 4–6 项岗位相关胜任力和可观察行为信号。
- 面试轮次、面试官角色和能力覆盖关系。
- 每项胜任力的行为问题、情境问题和追问。
- 1–4 分行为锚定评分表。
- 独立反馈模板和结构化复盘模板。
- 未验证信息、缺失证据和人工决策边界。

候选人简历属于可选输入。它只用于在统一岗位框架下生成核验问题，不改变核心题库、评分锚定和岗位标准。

<p align="center">
  <img src="assets/boards/interview-loop.svg?v=2" alt="岗位结果经过胜任力、统一问题、评分锚定和独立复盘形成结构化面试包" />
</p>

## Agent 使用须知

本须知适用于所有能够读取 `SKILL.md`、处理用户提供材料并执行本地脚本的 Agent。Agent 可以使用本地文件和用户粘贴内容完成全部流程；外部系统属于可选能力。平台侧元数据只负责发现和触发，核心使用规则见 [AGENT-GUIDE.md](AGENT-GUIDE.md)。

Agent 开始前要确认岗位结果、评价口径、面试轮次和输出目的；先检查用户消息和本地材料；使用外部系统时再确认身份与授权范围；缺少岗位证据时明确标记假设；评分和录用决定始终保留给人类。

<p align="center">
  <img src="assets/boards/evidence-rubric.svg?v=2" alt="面试回答转成可复核证据，再按行为锚定进入人工复核" />
</p>

## 快速开始

### 使用脱敏 JSON 生成面试包

```bash
python3 scripts/build_interview_kit.py \
  --input tests/fixtures/product-manager.json \
  --format markdown \
  --output /tmp/interview-kit.md
```

### 使用本地或用户提供的材料

可以先把岗位说明、HR 消息、邮件或聊天导出整理成脱敏 JSON，再运行生成器：

```bash
python3 scripts/build_interview_kit.py \
  --input /path/to/normalized-role.json \
  --format markdown \
  --output /tmp/interview-kit.md
```

材料抽取和证据记录见 [通用材料整理](references/material-intake.md)。

### 使用飞书岗位材料（可选）

```bash
lark-cli auth status --json --verify
lark-cli docs +search --query "产品经理 岗位说明" --as user --json
lark-cli docs +fetch --doc "https://example.feishu.cn/docx/XXXX" --scope full --doc-format markdown --as user --json
lark-cli sheets +cells-get --url "https://example.feishu.cn/sheets/shtXXXX" --sheet-name "岗位要求" --range "A1:Z80" --include value,formula --as user --json
```

支持 `auth status --json --verify` 的环境必须确认 `identity=user`、`verified=true`。当前 CLI 构建若没有 `auth` 子命令，可退回 `contact +get-user --as user` 或 `task +get-my-tasks --as user` 做只读兼容探测。飞书只负责读取用户明确授权的岗位材料。没有飞书接口时，直接使用本地或用户提供的材料即可。日历创建、消息发送、候选人状态修改和 Offer 操作需要转交相应 Skill，并单独确认。

## 面试设计的主线

岗位结果决定胜任力，胜任力决定问题，问题决定证据，证据进入锚定评分，面试官先独立提交，再进入团队复盘。

<p align="center">
  <img src="assets/boards/panel-coverage.svg?v=2" alt="面试轮次与岗位能力的覆盖矩阵，明确每项能力的观察人" />
</p>

## 可选：候选人针对性追问

完成岗位面试包后，HR 可以提供候选人简历原件或脱敏的工作经历摘要。经用户授权读取原始简历时，Agent 先临时提取岗位相关经历并去除身份、联系方式和受保护信息，再把简历主张映射到岗位胜任力，生成针对项目背景、本人贡献、决策过程、结果证据和复盘能力的核验问题。

核心问题对同一岗位保持一致；针对性问题只负责澄清候选人材料，不用于自动评分、候选人排序或录用判断。

```bash
python3 scripts/build_candidate_questions.py \
  --role-input tests/fixtures/product-manager.json \
  --candidate-input /path/to/anonymized-candidate.json \
  --format markdown \
  --output /tmp/candidate-questions.md
```

输入结构和隐私边界见 [候选人针对性追问模式](references/candidate-question-mode.md)。生成器只接受脱敏结构化摘要；原始候选人材料只在本地或用户授权环境内临时处理，不写入岗位模板、视觉资产或公开仓库。

## 安全边界

- 默认只读本地或用户明确授权的材料；使用外部系统时再确认身份、租户和授权范围。
- 默认不创建日程、不发消息、不修改候选人状态、不发 Offer。
- 默认不读取候选人姓名、联系方式、简历全文、逐字稿和受保护属性。
- 不用气场、文化匹配、私人关系、健康、家庭、年龄、性别、民族、宗教或薪酬历史作评价依据。
- 不把总分直接改写成自动录用或淘汰建议。

<p align="center">
  <img src="assets/boards/human-review.svg?v=2" alt="Agent 整理材料和证据，人类面试团队确认并承担最终决定" />
</p>

## 验证

在仓库根目录运行：

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
# 可选：若本机已安装 skill-creator 工具，可额外校验 SKILL.md frontmatter
# python3 "$SKILL_CREATOR/scripts/quick_validate.py" .
```

当前测试覆盖输入结构、题库要求、轮次覆盖、评分锚定、敏感字段拒绝、脱敏输出和候选人针对性问题生成。

## 上游与许可证

本项目以 [Anthropic Human Resources Plugin](https://github.com/anthropics/knowledge-work-plugins/tree/658e077ffd7bdd50a12c19ec5ff36fe34c88be8a/human-resources) 的 `interview-prep` 为上游参考；同时吸收 [OPM Structured Interviews](https://www.opm.gov/policy-data-oversight/assessment-and-selection/structured-interviews) 和 [Greenhouse Scorecards](https://support.greenhouse.io/hc/en-us/articles/4414777492891-Scorecard-overview) 的公开结构化面试实践。差异和许可证见 [UPSTREAM.md](UPSTREAM.md) 与 [LICENSE](LICENSE)。
