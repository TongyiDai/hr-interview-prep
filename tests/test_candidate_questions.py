import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROLE_SCRIPT = ROOT / "scripts" / "build_interview_kit.py"
CANDIDATE_SCRIPT = ROOT / "scripts" / "build_candidate_questions.py"

role_spec_loader = importlib.util.spec_from_file_location("role_builder_for_candidate_test", ROLE_SCRIPT)
assert role_spec_loader is not None and role_spec_loader.loader is not None
role_builder = importlib.util.module_from_spec(role_spec_loader)
role_spec_loader.loader.exec_module(role_builder)

candidate_spec_loader = importlib.util.spec_from_file_location("candidate_questions", CANDIDATE_SCRIPT)
assert candidate_spec_loader is not None and candidate_spec_loader.loader is not None
candidate_questions = importlib.util.module_from_spec(candidate_spec_loader)
candidate_spec_loader.loader.exec_module(candidate_questions)


class CandidateQuestionTest(unittest.TestCase):
    def setUp(self):
        with (ROOT / "tests/fixtures/product-manager.json").open(encoding="utf-8") as handle:
            self.role = json.load(handle)
        self.candidate = {
            "candidate_ref": "candidate-001",
            "experiences": [
                {
                    "experience_id": "exp-001",
                    "label": "支付产品改版项目",
                    "claims": [
                        "负责从需求分析到上线的产品推进",
                        "推动研发与运营协作完成交付",
                    ],
                    "related_competencies": ["problem_solving", "collaboration"],
                    "evidence_gaps": ["本人具体决策和贡献需要核验", "结果指标和验证方式未明确"],
                }
            ],
        }

    def test_generates_questions_linked_to_role_competencies(self):
        report = candidate_questions.build_questions(self.role, self.candidate)
        self.assertEqual(report["display_name"], "岗位面试设计")
        self.assertEqual(report["mode"], "candidate-specific-questions")
        self.assertEqual(len(report["question_groups"]), 2)
        self.assertEqual(report["question_groups"][0]["competency_id"], "problem_solving")
        self.assertIn("本人具体负责了什么", report["question_groups"][0]["questions"][1]["question"])
        self.assertIn("推动研发与运营协作完成交付", report["question_groups"][0]["questions"][0]["question"])
        self.assertIn("结果指标和验证方式未明确", report["question_groups"][0]["questions"][-1]["question"])

    def test_candidate_ref_is_deidentified(self):
        invalid = json.loads(json.dumps(self.candidate))
        invalid["candidate_ref"] = "张三"
        with self.assertRaisesRegex(ValueError, "de-identified"):
            candidate_questions.build_questions(self.role, invalid)

    def test_forbidden_candidate_fields_are_rejected(self):
        invalid = json.loads(json.dumps(self.candidate))
        invalid["full_name"] = "示例姓名"
        with self.assertRaisesRegex(ValueError, "forbidden field"):
            candidate_questions.build_questions(self.role, invalid)

    def test_unknown_competency_is_rejected(self):
        invalid = json.loads(json.dumps(self.candidate))
        invalid["experiences"][0]["related_competencies"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "unknown competencies"):
            candidate_questions.build_questions(self.role, invalid)

    def test_markdown_contains_boundary_and_no_personal_identity(self):
        report = candidate_questions.build_questions(self.role, self.candidate)
        markdown = candidate_questions.render_markdown(report)
        self.assertIn("不自动产生候选人评分", markdown)
        self.assertIn("支付产品改版项目", markdown)
        self.assertNotIn("姓名", markdown)


if __name__ == "__main__":
    unittest.main()
