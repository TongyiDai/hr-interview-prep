# 面试包输入结构

脚本接受一个 JSON 对象。输入描述岗位、材料来源摘要和面试设计，不放候选人个人资料。

## 推荐结构

```json
{
  "source_materials": [
    {"id": "role-brief", "type": "local_markdown", "label": "岗位说明.md", "status": "已确认"}
  ],
  "role": {
    "title": "产品经理",
    "level": "中级",
    "outcomes": ["明确用户问题并推动产品交付"],
    "constraints": ["需要与研发、设计和销售协作"]
  },
  "competencies": [
    {
      "id": "problem_solving",
      "name": "问题拆解",
      "definition": "把模糊问题拆成可验证的判断和行动",
      "signals": ["能明确问题边界", "能用证据排序优先级"],
      "behavioral_questions": ["讲一个你把模糊问题拆清楚的例子。", "讲一个你改变问题定义的例子。"],
      "situational_questions": ["如果多个团队对问题定义不一致，你会怎么推进？"],
      "probes": ["你本人做了什么？", "结果如何验证？"],
      "score_anchors": {"1": "关键证据缺失", "2": "有部分相关证据", "3": "证据完整且匹配岗位", "4": "证据具体并有持续结果"}
    }
  ],
  "rounds": [
    {"name": "业务面", "duration_minutes": 45, "interviewer_role": "直属主管", "competencies": ["problem_solving"]}
  ]
}
```

## 最低要求

- `source_materials` 可选；提供时，每项至少有 `id`、`type`、`label`，建议增加 `status`。
- `role.title` 必填。
- `role.outcomes` 至少 1 项。
- `competencies` 建议 4–6 项；脚本允许 3–6 项并在偏离建议范围时给出警告。
- 每项胜任力至少 2 个行为问题、1 个情境问题、2 个追问和完整的 1–4 分锚定描述。
- `rounds` 至少 1 个；每项胜任力至少被一个轮次覆盖。
- `rounds[].competencies` 只能引用已定义的胜任力 ID。

## 被拒绝的输入

脚本会拒绝候选人姓名、邮箱、电话、年龄、性别、民族、宗教、健康、家庭、婚姻和薪酬等个人或受保护字段。请先移除这些字段，再生成岗位面试包。来源摘要也不能包含原文、访问令牌或本地绝对路径。
