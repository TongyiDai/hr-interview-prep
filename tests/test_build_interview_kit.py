import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_interview_kit.py"

spec = importlib.util.spec_from_file_location("build_interview_kit", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class InterviewKitTest(unittest.TestCase):
    def setUp(self):
        with (ROOT / "tests/fixtures/product-manager.json").open(encoding="utf-8") as handle:
            self.input = json.load(handle)
        self.input["source_materials"] = [
            {"id": "role-brief", "type": "local_markdown", "label": "岗位说明.md", "status": "已确认"},
            {"id": "hr-chat", "type": "chat_export", "label": "招聘负责人消息导出", "status": "待确认"},
        ]
        self.report = module.build_report(self.input)

    def test_validates_role_competencies_and_coverage(self):
        validation = self.report["validation"]
        self.assertEqual(validation["competency_count"], 4)
        self.assertEqual(validation["missing_competencies"], [])
        self.assertEqual(validation["warnings"], [])

    def test_renders_complete_kit(self):
        markdown = self.report["markdown"]
        for expected in ("岗位结果", "胜任力与行为信号", "面试轮次与覆盖", "题库与追问", "评分表", "独立反馈模板", "团队复盘模板"):
            self.assertIn(expected, markdown)
        self.assertIn("问题拆解", markdown)
        self.assertIn("4 分", markdown)
        self.assertIn("材料来源与证据状态", markdown)
        self.assertIn("岗位说明.md", markdown)

    def test_local_source_metadata_is_preserved_without_raw_content(self):
        self.assertEqual(self.report["validation"]["source_material_count"], 2)
        self.assertEqual(self.report["source_materials"][0]["type"], "local_markdown")
        self.assertNotIn("raw", json.dumps(self.report, ensure_ascii=False))

    def test_source_materials_reject_raw_content_and_paths(self):
        invalid = json.loads(json.dumps(self.input))
        invalid["source_materials"][0]["path"] = "role.md"
        with self.assertRaisesRegex(ValueError, "metadata only"):
            module.build_report(invalid)

    def test_sensitive_fields_are_rejected(self):
        with (ROOT / "tests/fixtures/invalid-sensitive.json").open(encoding="utf-8") as handle:
            invalid = json.load(handle)
        with self.assertRaisesRegex(ValueError, "sensitive fields"):
            module.build_report(invalid)

    def test_unknown_round_competency_is_rejected(self):
        invalid = json.loads(json.dumps(self.input))
        invalid["rounds"][0]["competencies"].append("missing")
        with self.assertRaisesRegex(ValueError, "unknown competency"):
            module.build_report(invalid)

    def test_report_contains_no_candidate_data(self):
        serialized = json.dumps(self.report, ensure_ascii=False)
        self.assertNotIn("candidate_name", serialized)
        self.assertNotIn("示例候选人", serialized)
        self.assertEqual(self.report["display_name"], "岗位面试设计")


if __name__ == "__main__":
    unittest.main()
