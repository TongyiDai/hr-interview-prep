#!/usr/bin/env python3
"""Build role-linked, candidate-specific verification questions from anonymized experience claims."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


ROLE_SCRIPT = Path(__file__).with_name("build_interview_kit.py")
ROLE_SPEC = importlib.util.spec_from_file_location("build_interview_kit", ROLE_SCRIPT)
if ROLE_SPEC is None or ROLE_SPEC.loader is None:
    raise RuntimeError("cannot load role interview-kit validator")
ROLE_MODULE = importlib.util.module_from_spec(ROLE_SPEC)
ROLE_SPEC.loader.exec_module(ROLE_MODULE)


FORBIDDEN_KEYS = {
    "full_name", "candidate_name", "candidate_full_name", "email", "phone", "mobile",
    "phone_number", "address", "home_address", "linkedin", "github", "age", "gender",
    "sex", "ethnicity", "race", "religion", "health", "disability", "medical", "family",
    "marital", "pregnancy", "salary", "compensation", "resume", "resume_text", "raw_resume",
    "full_resume", "contact", "school", "university", "education", "birth_date",
    "date_of_birth", "姓名", "邮箱", "电话", "地址", "年龄", "性别", "民族", "宗教",
    "健康", "家庭", "婚姻", "怀孕", "薪酬", "简历", "教育经历",
}


def key_name(value: Any) -> str:
    return str(value).strip().casefold().replace("-", "_").replace(" ", "_")


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def reject_forbidden_keys(value: Any, path: str = "candidate") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            current = f"{path}.{key}"
            if key_name(key) in FORBIDDEN_KEYS:
                raise ValueError(f"candidate input contains forbidden field: {current}")
            reject_forbidden_keys(child, current)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_forbidden_keys(child, f"{path}[{index}]")


def required_text(value: Any, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{label} is required")
    return text


def text_list(value: Any, label: str, minimum: int = 1) -> list[str]:
    if not isinstance(value, list) or len(value) < minimum:
        raise ValueError(f"{label} must contain at least {minimum} item(s)")
    result = [str(item).strip() for item in value]
    if any(not item for item in result):
        raise ValueError(f"{label} cannot contain empty items")
    return result


def validate_candidate(candidate: dict[str, Any], competency_ids: set[str]) -> list[dict[str, Any]]:
    reject_forbidden_keys(candidate)
    unknown_top_level = set(candidate) - {"candidate_ref", "experiences"}
    if unknown_top_level:
        raise ValueError(f"candidate input contains unsupported fields: {', '.join(sorted(unknown_top_level))}")
    candidate_ref = required_text(candidate.get("candidate_ref"), "candidate_ref")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", candidate_ref):
        raise ValueError("candidate_ref must be a de-identified reference using letters, digits, _ or -")
    experiences = candidate.get("experiences")
    if not isinstance(experiences, list) or not experiences:
        raise ValueError("experiences must contain at least 1 item")
    normalized: list[dict[str, Any]] = []
    allowed = {"experience_id", "label", "claims", "related_competencies", "evidence_gaps"}
    experience_ids: set[str] = set()
    for index, experience in enumerate(experiences, start=1):
        if not isinstance(experience, dict):
            raise ValueError(f"experiences[{index}] must be an object")
        unknown = set(experience) - allowed
        if unknown:
            raise ValueError(f"experiences[{index}] contains unsupported fields: {', '.join(sorted(unknown))}")
        experience_id = required_text(experience.get("experience_id"), f"experiences[{index}].experience_id")
        if experience_id in experience_ids:
            raise ValueError(f"duplicate experience_id: {experience_id}")
        experience_ids.add(experience_id)
        label = required_text(experience.get("label"), f"experiences[{index}].label")
        claims = text_list(experience.get("claims"), f"experiences[{index}].claims")
        related = text_list(experience.get("related_competencies"), f"experiences[{index}].related_competencies")
        unknown_competencies = sorted(set(related) - competency_ids)
        if unknown_competencies:
            raise ValueError(
                f"experiences[{index}] references unknown competencies: {', '.join(unknown_competencies)}"
            )
        gaps_value = experience.get("evidence_gaps") or []
        if not isinstance(gaps_value, list):
            raise ValueError(f"experiences[{index}].evidence_gaps must be a list")
        gaps = [str(item).strip() for item in gaps_value]
        if any(not item for item in gaps):
            raise ValueError(f"experiences[{index}].evidence_gaps cannot contain empty items")
        normalized.append({
            "experience_id": experience_id,
            "label": label,
            "claims": claims,
            "related_competencies": related,
            "evidence_gaps": gaps,
        })
    return normalized


def role_maps(role_spec: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, str], dict[str, list[str]]]:
    competencies = {item["id"]: item for item in role_spec["competencies"]}
    names = {item["id"]: item["name"] for item in role_spec["competencies"]}
    rounds: dict[str, list[str]] = {item["id"]: [] for item in role_spec["competencies"]}
    for interview_round in role_spec["rounds"]:
        for competency_id in interview_round["competencies"]:
            rounds[competency_id].append(interview_round["name"])
    return competencies, names, rounds


def build_questions(role_spec: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    role_validation = ROLE_MODULE.validate_spec(role_spec)
    competencies, names, round_names = role_maps(role_spec)
    experiences = validate_candidate(candidate, set(competencies))
    questions: list[dict[str, Any]] = []
    for experience in experiences:
        claims_text = "；".join(f"“{claim}”" for claim in experience["claims"])
        for competency_id in experience["related_competencies"]:
            competency = competencies[competency_id]
            question_set = [
                {
                    "type": "背景与目标",
                    "question": f"你在“{experience['label']}”中将经历概括为：{claims_text}。当时要解决什么问题，目标和成功标准是什么？",
                    "record": "记录背景、目标、约束和可验证的成功标准。",
                },
                {
                    "type": "本人贡献",
                    "question": f"在“{experience['label']}”中，与你所描述的“{experience['claims'][0]}”对应的工作里，你本人具体负责了什么？哪些关键动作由你完成？",
                    "record": "区分本人行动、团队行动和结果归因。",
                },
                {
                    "type": "决策与权衡",
                    "question": f"围绕“{experience['label']}”，你做过哪一个影响结果的关键判断？当时考虑了哪些选项和约束？",
                    "record": "记录决策依据、备选方案、约束和取舍。",
                },
                {
                    "type": "结果证据",
                    "question": f"这个经历最后产生了什么结果？你用什么指标或事实验证结果，结果中哪些部分可以归因于你的工作？",
                    "record": "记录结果、指标来源、时间范围和归因边界。",
                },
                {
                    "type": "迁移与复盘",
                    "question": f"如果把“{experience['label']}”中的经验迁移到当前岗位的“{competency['name']}”场景，你会保留什么、调整什么？",
                    "record": "记录迁移条件、风险和复盘后的改进。",
                },
            ]
            for gap in experience["evidence_gaps"]:
                question_set.append({
                    "type": "证据缺口",
                    "question": f"材料中提到“{gap}”。你可以补充一个具体例子和可核验的事实吗？",
                    "record": "记录该缺口是否被具体事实和证据补足。",
                })
            questions.append({
                "experience_id": experience["experience_id"],
                "experience_label": experience["label"],
                "competency_id": competency_id,
                "competency": names[competency_id],
                "rounds": round_names[competency_id],
                "questions": question_set,
            })
    return {
        "schema_version": "1.0",
        "skill": "hr-interview-prep",
        "display_name": "岗位面试设计",
        "mode": "candidate-specific-questions",
        "role_title": role_spec["role"]["title"],
        "candidate_ref": candidate["candidate_ref"],
        "role_validation": role_validation,
        "question_groups": questions,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# 岗位面试设计｜候选人针对性追问",
        "",
        f"- 岗位：{report['role_title']}",
        f"- 脱敏编号：{report['candidate_ref']}",
        "- 使用方式：保留岗位核心问题和评分标准，补充简历核验问题",
        "",
        "## 使用边界",
        "",
        "这些问题只用于澄清岗位相关经历、本人贡献和结果证据，不自动产生候选人评分、排序或录用结论。",
        "",
    ]
    for group in report["question_groups"]:
        rounds = "、".join(group["rounds"]) or "待分配面试轮次"
        lines.extend([
            f"## {group['experience_label']}｜{group['competency']}",
            "",
            f"- 面试轮次：{rounds}",
            f"- 胜任力 ID：`{group['competency_id']}`",
            "",
            "| 类型 | 针对性问题 | 记录重点 |",
            "|---|---|---|",
        ])
        lines.extend(
            f"| {item['type']} | {item['question']} | {item['record']} |"
            for item in group["questions"]
        )
        lines.append("")
    lines.extend([
        "## 面试官记录提醒",
        "",
        "- 已观察到的事实：",
        "- 候选人的本人贡献：",
        "- 可核验的结果证据：",
        "- 仍未验证的内容：",
        "- 对应岗位胜任力和评分锚定：",
        "- 需要人类面试官确认的判断：",
        "",
    ])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role-input", required=True, type=Path)
    parser.add_argument("--candidate-input", required=True, type=Path)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv or sys.argv[1:])
    try:
        role_spec = load_json(args.role_input, "role input")
        candidate = load_json(args.candidate_input, "candidate input")
        report = build_questions(role_spec, candidate)
        if args.format == "markdown":
            output = render_markdown(report)
        else:
            output = json.dumps(report, ensure_ascii=False, indent=2)
        if args.output:
            args.output.write_text(output + "\n", encoding="utf-8")
        else:
            print(output)
        return 0
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
