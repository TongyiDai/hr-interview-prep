#!/usr/bin/env python3
"""Validate and render a role-based structured interview kit."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SENSITIVE = {
    "full_name", "candidate_name", "candidate_full_name", "email", "phone", "mobile",
    "age", "gender", "sex", "ethnicity", "race", "religion", "health",
    "disability", "medical", "family", "marital", "pregnancy", "salary",
    "compensation", "薪酬", "姓名", "邮箱", "电话", "年龄", "性别", "民族",
    "宗教", "健康", "家庭", "婚姻", "怀孕",
}


def key_name(value: Any) -> str:
    return str(value).strip().casefold().replace("-", "_").replace(" ", "_")


def walk_keys(value: Any, path: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            current = f"{path}.{key}" if path else str(key)
            if key_name(key) in SENSITIVE:
                hits.append(current)
            hits.extend(walk_keys(child, current))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(walk_keys(child, f"{path}[{index}]"))
    return hits


def require_list(value: Any, label: str, minimum: int = 1) -> list[Any]:
    if not isinstance(value, list) or len(value) < minimum:
        raise ValueError(f"{label} must contain at least {minimum} item(s)")
    return value


def validate_source_materials(spec: dict[str, Any]) -> list[dict[str, str]]:
    sources = spec.get("source_materials") or []
    if not isinstance(sources, list):
        raise ValueError("source_materials must be a list")
    normalized: list[dict[str, str]] = []
    forbidden_keys = {"raw", "content", "body", "token", "access_token", "password", "path", "absolute_path"}
    for index, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            raise ValueError(f"source_materials[{index}] must be an object")
        if forbidden_keys.intersection(key_name(key) for key in source):
            raise ValueError(f"source_materials[{index}] must contain metadata only")
        values: dict[str, str] = {}
        for field in ("id", "type", "label"):
            value = str(source.get(field, "")).strip()
            if not value:
                raise ValueError(f"source_materials[{index}].{field} is required")
            values[field] = value
        values["status"] = str(source.get("status", "待确认")).strip() or "待确认"
        normalized.append(values)
    return normalized


def validate_spec(spec: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(spec, dict):
        raise ValueError("input root must be an object")
    sensitive_hits = walk_keys(spec)
    if sensitive_hits:
        raise ValueError("sensitive fields are not allowed: " + ", ".join(sensitive_hits))
    source_materials = validate_source_materials(spec)
    role = spec.get("role")
    if not isinstance(role, dict) or not str(role.get("title", "")).strip():
        raise ValueError("role.title is required")
    outcomes = require_list(role.get("outcomes"), "role.outcomes")
    if any(not str(item).strip() for item in outcomes):
        raise ValueError("role.outcomes cannot contain empty items")
    competencies = require_list(spec.get("competencies"), "competencies", 3)
    warnings: list[str] = []
    if len(competencies) < 4 or len(competencies) > 6:
        warnings.append("competencies should usually contain 4–6 items")
    ids: set[str] = set()
    for index, competency in enumerate(competencies, start=1):
        if not isinstance(competency, dict):
            raise ValueError(f"competencies[{index}] must be an object")
        competency_id = str(competency.get("id", "")).strip()
        if not competency_id:
            raise ValueError(f"competencies[{index}].id is required")
        if competency_id in ids:
            raise ValueError(f"duplicate competency id: {competency_id}")
        ids.add(competency_id)
        for field in ("name", "definition"):
            if not str(competency.get(field, "")).strip():
                raise ValueError(f"competencies[{index}].{field} is required")
        signals = require_list(competency.get("signals"), f"competencies[{index}].signals")
        if any(not str(signal).strip() for signal in signals):
            raise ValueError(f"competencies[{index}].signals cannot contain empty items")
        behavioral = require_list(competency.get("behavioral_questions"), f"competencies[{index}].behavioral_questions", 2)
        situational = require_list(competency.get("situational_questions"), f"competencies[{index}].situational_questions", 1)
        probes = require_list(competency.get("probes"), f"competencies[{index}].probes", 2)
        if any(not str(item).strip() for item in behavioral + situational + probes):
            raise ValueError(f"competencies[{index}] question fields cannot contain empty items")
        anchors = competency.get("score_anchors")
        if not isinstance(anchors, dict) or set(map(str, anchors.keys())) != {"1", "2", "3", "4"}:
            raise ValueError(f"competencies[{index}].score_anchors must contain exactly 1, 2, 3, 4")
        if any(not str(anchors[str(score)]).strip() for score in range(1, 5)):
            raise ValueError(f"competencies[{index}].score_anchors cannot contain empty items")
    rounds = require_list(spec.get("rounds"), "rounds")
    covered: set[str] = set()
    round_names: set[str] = set()
    for index, interview_round in enumerate(rounds, start=1):
        if not isinstance(interview_round, dict):
            raise ValueError(f"rounds[{index}] must be an object")
        round_name = str(interview_round.get("name", "")).strip()
        if not round_name:
            raise ValueError(f"rounds[{index}].name is required")
        if round_name in round_names:
            raise ValueError(f"duplicate round name: {round_name}")
        round_names.add(round_name)
        duration = interview_round.get("duration_minutes")
        if not isinstance(duration, int) or duration <= 0:
            raise ValueError(f"rounds[{index}].duration_minutes must be a positive integer")
        if not str(interview_round.get("interviewer_role", "")).strip():
            raise ValueError(f"rounds[{index}].interviewer_role is required")
        round_competencies = require_list(interview_round.get("competencies"), f"rounds[{index}].competencies")
        for competency_id in round_competencies:
            if competency_id not in ids:
                raise ValueError(f"rounds[{index}] references unknown competency: {competency_id}")
            covered.add(competency_id)
    missing = sorted(ids - covered)
    if missing:
        warnings.append("uncovered competencies: " + ", ".join(missing))
    return {
        "warnings": warnings,
        "competency_count": len(competencies),
        "covered_competencies": sorted(covered),
        "missing_competencies": missing,
        "source_material_count": len(source_materials),
    }


def load_spec(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON input: {exc}") from exc


def render_markdown(spec: dict[str, Any], validation: dict[str, Any]) -> str:
    role = spec["role"]
    competencies = spec["competencies"]
    rounds = spec["rounds"]
    lines = [
        f"# 面试包｜{role['title']}",
        "",
        f"- 级别：{role.get('level') or '未指定'}",
        f"- 胜任力数量：{len(competencies)}",
        f"- 面试轮次：{len(rounds)}",
        "",
        "## 岗位结果",
        "",
    ]
    lines.extend(f"- {outcome}" for outcome in role["outcomes"])
    sources = validation.get("source_materials") or spec.get("source_materials") or []
    if sources:
        lines.extend(["", "## 材料来源与证据状态", "", "| 来源 | 类型 | 状态 |", "|---|---|---|"])
        lines.extend(
            f"| {source['label']} | {source['type']} | {source.get('status') or '待确认'} |"
            for source in sources
        )
    constraints = role.get("constraints") or []
    if constraints:
        lines.extend(["", "## 设计约束", ""])
        lines.extend(f"- {constraint}" for constraint in constraints)
    lines.extend(["", "## 胜任力与行为信号", "", "| 胜任力 | 定义 | 观察信号 |", "|---|---|---|"])
    for competency in competencies:
        signals = "；".join(str(signal) for signal in competency["signals"])
        lines.append(f"| {competency['name']} | {competency['definition']} | {signals} |")
    lines.extend(["", "## 面试轮次与覆盖", "", "| 轮次 | 时长 | 面试官角色 | 覆盖胜任力 |", "|---|---:|---|---|"])
    names = {item["id"]: item["name"] for item in competencies}
    for interview_round in rounds:
        coverage = "、".join(names[item] for item in interview_round["competencies"])
        lines.append(f"| {interview_round['name']} | {interview_round['duration_minutes']} 分钟 | {interview_round['interviewer_role']} | {coverage} |")
    lines.extend(["", "## 题库与追问", ""])
    for competency in competencies:
        lines.extend([f"### {competency['name']}", "", "行为问题："])
        lines.extend(f"- {question}" for question in competency["behavioral_questions"])
        lines.append("")
        lines.append("情境问题：")
        lines.extend(f"- {question}" for question in competency["situational_questions"])
        lines.append("")
        lines.append("追问：")
        lines.extend(f"- {probe}" for probe in competency["probes"])
        lines.append("")
    lines.extend(["## 评分表", "", "先独立评分，再进入团队复盘。评分必须引用岗位相关证据。", "", "| 胜任力 | 1 分 | 2 分 | 3 分 | 4 分 |", "|---|---|---|---|---|"])
    for competency in competencies:
        anchors = competency["score_anchors"]
        lines.append(f"| {competency['name']} | {anchors['1']} | {anchors['2']} | {anchors['3']} | {anchors['4']} |")
    lines.extend([
        "", "## 独立反馈模板", "", "- 观察到的事实：", "- 关键证据：", "- 候选人的本人贡献：", "- 结果与影响：", "- 对应胜任力与评分：", "- 仍未验证的内容：", "- 需要补充的问题：", "",
        "## 团队复盘模板", "", "- 共同确认的事实：", "- 证据一致处：", "- 证据分歧处：", "- 可能的解释：", "- 仍缺失的证据：", "- 需要人工决策者确认的结论：", "",
        "## 校验结果", "",
        f"- 胜任力：{validation['competency_count']} 项",
        f"- 已覆盖：{len(validation['covered_competencies'])} 项",
        f"- 未覆盖：{', '.join(validation['missing_competencies']) or '无'}",
        f"- 警告：{'；'.join(validation['warnings']) or '无'}",
        "",
        "本面试包只整理岗位相关证据和人工复核材料，不自动作出录用或淘汰决定。",
        "",
    ])
    return "\n".join(lines)


def build_report(spec: dict[str, Any]) -> dict[str, Any]:
    validation = validate_spec(spec)
    validation["source_materials"] = validate_source_materials(spec)
    return {
        "schema_version": "1.0",
        "skill": "hr-interview-prep",
        "display_name": "岗位面试设计",
        "role_title": spec["role"]["title"],
        "source_materials": validation["source_materials"],
        "validation": validation,
        "markdown": render_markdown(spec, validation),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv or sys.argv[1:])
    try:
        report = build_report(load_spec(args.input))
        output = report["markdown"] if args.format == "markdown" else json.dumps({key: value for key, value in report.items() if key != "markdown"}, ensure_ascii=False, indent=2)
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
