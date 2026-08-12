# 上游与先例

## 上游来源

- 上游项目：[anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins)
- 上游插件：[human-resources](https://github.com/anthropics/knowledge-work-plugins/tree/658e077ffd7bdd50a12c19ec5ff36fe34c88be8a/human-resources)
- 上游 Skill：[interview-prep](https://github.com/anthropics/knowledge-work-plugins/tree/658e077ffd7bdd50a12c19ec5ff36fe34c88be8a/human-resources/skills/interview-prep)
- 固定版本：`658e077ffd7bdd50a12c19ec5ff36fe34c88be8a`
- 核验时间：2026-08-12（Asia/Shanghai）

## 保留与扩展

上游 Skill 的核心是结构化、胜任力、证据化问题、多元面试官、统一评分和复盘模板。本包保留这些概念，并补充：

- 中文岗位与面试团队工作流。
- 结构化 JSON 输入和本地 Markdown/JSON 生成器。
- 胜任力数量、问题数量、评分锚定和轮次覆盖校验。
- 本地消息、邮件、HR 文档、表格和人工口述的通用材料整理方法。
- 飞书作为可选输入源时的用户态读取顺序与最小字段边界。
- 岗位面试包完成后的脱敏简历核验问题模式；该模式只补充岗位相关追问，不做简历评分。
- 跨 Agent 使用须知、停止规则和人工决策边界。

## 公开先例

- [美国 OPM Structured Interviews](https://www.opm.gov/policy-data-oversight/assessment-and-selection/structured-interviews)：统一问题、岗位相关胜任力和一致评分是结构化面试的核心。
- [Greenhouse Scorecard Overview](https://support.greenhouse.io/hc/en-us/articles/4414777492891-Scorecard-overview)：评分表围绕预先确定的能力和属性组织，面试官提交反馈后再进行团队复盘。
- [Greenhouse Structured Hiring Guide](https://support.greenhouse.io/hc/en-us/articles/360039539772-Structured-hiring-guide)：面试开始前明确面试团队职责和评分表提交时点，复盘前先完成独立反馈。
- [University of Bristol structured interview guidance](https://www.bristol.ac.uk/hr/resourcing/practicalguidance/selection/interviewtechnique.html)：在统一面试计划下，可以针对申请材料中不清楚的经历做澄清追问。
- [Canada structured interview guidance](https://www.canada.ca/en/public-service-commission/services/public-service-hiring-guides/appointment-processes-how-conduct-interviews.html)：追问用于补足回答信息，不应借此引入全新的评价主题。
- [飞书开放平台：面试轮次类型](https://open.feishu.cn/document/server-docs/hire-v1/recruitment-related-configuration/interview-settings/list-2)：飞书招聘提供面试轮次配置相关接口。
- [飞书帮助中心：协调多人面试时间](https://www.feishu.cn/hc/zh-cn/articles/360042124534)：飞书日历适合查找忙闲、创建面试日程和邀请面试官。

## 许可证

上游仓库声明 Apache License 2.0。本包保留许可证文本和上游归属信息，不声称得到 Anthropic、OPM、Greenhouse 或飞书官方维护或背书。
