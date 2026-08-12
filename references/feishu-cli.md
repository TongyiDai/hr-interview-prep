# 飞书 CLI 读取适配（可选）

飞书是本 Skill 的可选输入源。没有飞书接口时，使用用户提供的本地文件、消息导出或 HR 材料完成全部流程。接入飞书时，只使用用户授权的身份读取岗位说明、招聘规范、面试模板和脱敏表格，默认只读。

## 身份检查

```bash
lark-cli auth status --json --verify
```

继续条件：`identity=user`、`verified=true` 且 token 有效。账号、租户或权限存在疑问时停止。

## 文档

先搜索，再读取用户明确指定的文档：

```bash
lark-cli docs +search --query "产品经理 岗位说明" --as user --json
lark-cli docs +fetch \
  --doc "https://example.feishu.cn/docx/XXXX" \
  --scope full --doc-format markdown --as user --json
```

只读取岗位结果、职责、级别、评价标准和面试流程等必要段落。候选人简历和面试逐字稿需要独立授权，默认不读。

## Sheets

```bash
lark-cli sheets +cells-get \
  --url "https://example.feishu.cn/sheets/shtXXXX" \
  --sheet-name "岗位要求" --range "A1:Z80" \
  --include value,formula --as user --json
```

先读标题行和必要范围，再做字段映射。大表按范围分块，记录读取范围和时间。

## 日历与写入

面试包准备默认不读取日历，也不创建日程。用户明确要求安排面试时，转交日历 Skill；先输出候选时间、面试官、时区和拟写入内容，确认后再执行，并读回日程。

## 证据记录

保留数据源类型、脱敏资源标识、读取时间、读取范围、字段映射、输入摘要和脚本版本。原始岗位文档不复制进仓库，候选人个人数据不写入 Skill 包。
