#!/usr/bin/env python3
"""Render the four role-interview Geometry Board scenes as local SVGs."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


W, H = 1200, 675
BLACK = "#111111"
LINE = "#222222"
GRAY = "#666666"
MUTED = "#999999"
GUIDE = "#B8B8B8"
LIGHT = "#E8E8E8"
FILL = "#F5F5F5"
BLUE = "#2F6BFF"
FONT = "-apple-system,BlinkMacSystemFont,'PingFang SC','Noto Sans CJK SC',sans-serif"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def txt(x: float, y: float, value: str, size: int = 16, fill: str = BLACK, anchor: str = "middle", weight: int = 400, letter: float = 0) -> str:
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" '
        f'font-size="{size}px" font-weight="{weight}" letter-spacing="{letter}px" fill="{fill}">{esc(value)}</text>'
    )


def two_lines(x: float, y: float, first: str, second: str, size: int = 16, fill: str = BLACK, gap: int = 20, weight: int = 600) -> str:
    return txt(x, y - gap / 2 + 5, first, size, fill, weight=weight) + txt(x, y + gap / 2 + 5, second, size, fill, weight=weight)


def line(x1: float, y1: float, x2: float, y2: float, color: str = LINE, width: float = 1.5, arrow: bool = False, dashed: bool = False) -> str:
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    dash = ' stroke-dasharray="5 7"' if dashed else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{dash}{marker} />'


def path(d: str, color: str = LINE, width: float = 1.5, arrow: bool = False, dashed: bool = False) -> str:
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    dash = ' stroke-dasharray="5 7"' if dashed else ""
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{dash}{marker} />'


def title(scene: dict) -> str:
    intent = scene["intent"]
    subtitle = intent.get("subtitle", "岗位面试设计 · 结构化面试")
    return "".join([
        txt(96, 78, intent["core_message"], 32, BLACK, "start", 650),
        txt(96, 108, subtitle, 14, GRAY, "start", 400),
        line(96, 136, 1104, 136, LIGHT, 1),
    ])


def render_interview(scene: dict) -> str:
    body = [title(scene)]
    y = 350
    body.append(line(138, y, 1070, y, GUIDE, 1))
    for start, end in ((250, 325), (450, 535), (665, 755), (886, 955)):
        body.append(line(start, y, end, y, LINE, 1.5, arrow=True))

    body.extend([
        '<rect x="138" y="290" width="108" height="120" fill="none" stroke="#222222" stroke-width="1.5" />',
        line(154, 322, 230, 322, GUIDE, 1),
        line(154, 350, 230, 350, GUIDE, 1),
        line(154, 378, 230, 378, GUIDE, 1),
        txt(192, 447, "岗位结果", 16, BLACK, weight=600),
        txt(192, 474, "结果 · 约束 · 协作", 12, GRAY),
        '<circle cx="386" cy="350" r="45" fill="none" stroke="#222222" stroke-width="1.5" />',
        '<circle cx="357" cy="326" r="9" fill="#F5F5F5" stroke="#222222" stroke-width="1.2" />',
        '<circle cx="421" cy="333" r="9" fill="#F5F5F5" stroke="#222222" stroke-width="1.2" />',
        '<circle cx="388" cy="382" r="9" fill="#F5F5F5" stroke="#222222" stroke-width="1.2" />',
        txt(386, 447, "岗位胜任力", 16, BLACK, weight=600),
        '<circle cx="600" cy="350" r="58" fill="#2F6BFF" />',
        two_lines(600, 348, "统一", "问题", 18, "#FFFFFF", 22, 650),
        txt(600, 447, "同岗同题", 13, GRAY),
        line(816, 292, 816, 408, LINE, 1.5),
        line(805, 304, 846, 304, LINE, 1.2),
        line(805, 335, 846, 335, LINE, 1.2),
        line(805, 366, 846, 366, LINE, 1.2),
        line(805, 397, 846, 397, LINE, 1.2),
        txt(858, 309, "1", 12, GRAY, "start"),
        txt(858, 340, "2", 12, GRAY, "start"),
        txt(858, 371, "3", 12, GRAY, "start"),
        txt(858, 402, "4", 12, GRAY, "start"),
        txt(830, 447, "评分锚定", 16, BLACK, weight=600),
        '<rect x="970" y="305" width="76" height="94" fill="none" stroke="#222222" stroke-width="1.5" />',
        '<rect x="980" y="295" width="76" height="94" fill="#FFFFFF" stroke="#B8B8B8" stroke-width="1" />',
        line(992, 328, 1036, 328, GUIDE, 1),
        line(992, 348, 1036, 348, GUIDE, 1),
        line(992, 368, 1036, 368, GUIDE, 1),
        txt(1012, 447, "独立复盘", 16, BLACK, weight=600),
        path("M 1012 430 C 1012 538 192 538 192 430", GUIDE, 1.2, True),
        txt(602, 568, "复盘结果回到岗位标准", 12, GRAY),
    ])
    return "".join(body)


def dot(x: float, y: float, active: bool) -> str:
    if active:
        return f'<circle cx="{x}" cy="{y}" r="13" fill="#2F6BFF" /><path d="M {x - 5} {y} l 4 4 l 8 -9" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />'
    return f'<circle cx="{x}" cy="{y}" r="6" fill="#FFFFFF" stroke="#B8B8B8" stroke-width="1.2" />'


def render_matrix(scene: dict) -> str:
    body = [title(scene)]
    left, top, cell_w, cell_h = 410, 250, 190, 78
    body.extend([
        txt(698, 210, "岗位能力", 13, GRAY, weight=600),
        txt(340, 388, "面试轮次", 13, GRAY, anchor="middle", weight=600),
        '<path d="M 368 250 h -14 v 234 h 14" fill="none" stroke="#B8B8B8" stroke-width="1" />',
    ])
    col_labels = ["业务判断", "跨团队协作", "执行推进"]
    row_labels = ["直属主管", "跨团队伙伴", "业务负责人"]
    for index, label in enumerate(col_labels):
        x = left + cell_w * index + cell_w / 2
        body.append(txt(x, 236, label, 15, BLACK, weight=600))
    for index, label in enumerate(row_labels):
        y = top + cell_h * index + cell_h / 2 + 5
        body.append(txt(335, y, label, 15, BLACK, "end", 500))
    for col in range(4):
        body.append(line(left + col * cell_w, top, left + col * cell_w, top + 3 * cell_h, LIGHT, 1))
    for row in range(4):
        body.append(line(left, top + row * cell_h, left + 3 * cell_w, top + row * cell_h, LIGHT, 1))
    active = {(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)}
    for row in range(3):
        for col in range(3):
            x = left + col * cell_w + cell_w / 2
            y = top + row * cell_h + cell_h / 2
            body.append(dot(x, y, (row, col) in active))
    body.extend([
        '<circle cx="425" cy="566" r="7" fill="#2F6BFF" />',
        txt(442, 571, "本轮负责观察", 13, GRAY, "start"),
        line(636, 566, 764, 566, LIGHT, 1),
        txt(780, 571, "每项能力至少一轮", 13, BLACK, "start", 600),
    ])
    return "".join(body)


def render_evidence(scene: dict) -> str:
    body = [title(scene)]
    body.extend([
        txt(210, 252, "面试回答", 16, BLACK, weight=600),
        line(142, 285, 280, 285, GUIDE, 1.5),
        line(142, 316, 250, 316, GUIDE, 1.5),
        line(142, 347, 272, 347, GUIDE, 1.5),
        '<circle cx="303" cy="285" r="5" fill="#FFFFFF" stroke="#222222" stroke-width="1.2" />',
        '<circle cx="274" cy="316" r="5" fill="#FFFFFF" stroke="#222222" stroke-width="1.2" />',
        '<circle cx="296" cy="347" r="5" fill="#FFFFFF" stroke="#222222" stroke-width="1.2" />',
        path("M 311 285 C 395 285 418 320 490 331", LINE, 1.5, True),
        path("M 282 316 C 390 316 412 332 490 341", LINE, 1.5, True),
        path("M 304 347 C 390 347 412 352 490 351", LINE, 1.5, True),
        '<circle cx="555" cy="342" r="65" fill="#2F6BFF" />',
        two_lines(555, 339, "可复核", "证据", 18, "#FFFFFF", 22, 650),
        txt(555, 435, "事实 · 行动 · 结果", 13, GRAY),
        line(623, 342, 725, 342, LINE, 1.5, True),
        txt(810, 252, "行为锚定", 16, BLACK, weight=600),
        line(744, 307, 908, 307, LINE, 1.5),
        line(744, 342, 908, 342, LINE, 1.5),
        line(744, 377, 908, 377, LINE, 1.5),
        line(744, 412, 908, 412, LINE, 1.5),
        txt(726, 312, "1", 13, GRAY),
        txt(726, 347, "2", 13, GRAY),
        txt(726, 382, "3", 13, GRAY),
        txt(726, 417, "4", 13, GRAY),
        line(912, 342, 973, 342, LINE, 1.5, True),
        '<circle cx="1032" cy="342" r="36" fill="#F5F5F5" stroke="#222222" stroke-width="1.5" />',
        two_lines(1032, 340, "人工", "复核", 14, BLACK, 18, 650),
        '<circle cx="258" cy="525" r="11" fill="#FFFFFF" stroke="#B8B8B8" stroke-width="1.2" stroke-dasharray="4 4" />',
        txt(280, 530, "没有证据：未验证", 13, GRAY, "start"),
    ])
    return "".join(body)


def render_section(scene: dict) -> str:
    body = [title(scene)]
    body.extend([
        '<rect x="112" y="202" width="476" height="326" fill="#F5F5F5" />',
        '<rect x="706" y="202" width="382" height="326" fill="#FFFFFF" stroke="#E8E8E8" stroke-width="1" />',
        line(647, 196, 647, 544, GUIDE, 1, dashed=True),
        txt(350, 232, "Agent 可以做", 15, GRAY, weight=600),
        txt(897, 232, "人负责", 15, GRAY, weight=600),
        '<rect x="174" y="292" width="114" height="88" fill="#FFFFFF" stroke="#222222" stroke-width="1.5" />',
        line(192, 320, 270, 320, GUIDE, 1),
        line(192, 342, 258, 342, GUIDE, 1),
        txt(231, 409, "整理材料", 15, BLACK, weight=600),
        line(318, 336, 412, 336, LINE, 1.5, True),
        line(432, 286, 432, 385, LINE, 1.5),
        line(420, 302, 467, 302, LINE, 1.2),
        line(420, 329, 467, 329, LINE, 1.2),
        line(420, 356, 467, 356, LINE, 1.2),
        txt(432, 409, "按标准整理", 15, BLACK, weight=600),
        path("M 480 336 C 548 336 563 366 614 366", LINE, 1.5, True),
        '<circle cx="647" cy="366" r="18" fill="#2F6BFF" />',
        txt(647, 414, "复核点", 13, BLUE, weight=650),
        line(669, 366, 754, 366, LINE, 1.5, True),
        '<circle cx="876" cy="356" r="75" fill="#FFFFFF" stroke="#222222" stroke-width="1.5" />',
        '<circle cx="876" cy="356" r="52" fill="none" stroke="#E8E8E8" stroke-width="1" />',
        '<circle cx="876" cy="356" r="8" fill="#2F6BFF" />',
        txt(876, 438, "面试团队", 16, BLACK, weight=650),
        txt(876, 467, "确认结论 · 承担决定", 13, GRAY),
        txt(350, 496, "整理事实与提示", 13, GRAY),
        txt(897, 496, "录用、淘汰与排序", 13, GRAY),
    ])
    return "".join(body)


def render(scene: dict) -> str:
    composition = scene["intent"]["composition"]
    if composition == "axis-flow":
        body = render_interview(scene)
    elif composition == "matrix-2d":
        body = render_matrix(scene)
    elif composition == "input-process-output":
        body = render_evidence(scene)
    elif composition == "section-space":
        body = render_section(scene)
    else:
        raise ValueError(f"unsupported composition: {composition}")
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>{esc(scene["intent"]["core_message"])}</title>
  <desc>Geometry Board for the 岗位面试设计 skill.</desc>
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="strokeWidth">
      <path d="M 0 0 L 8 4 L 0 8 z" fill="{LINE}" />
    </marker>
  </defs>
  <rect width="1200" height="675" fill="#FFFFFF" />
  {body}
</svg>
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for scene_path in sorted(args.scene_dir.glob("*.json")):
        scene = json.loads(scene_path.read_text(encoding="utf-8"))
        output_path = args.output_dir / f"{scene_path.stem}.svg"
        output_path.write_text(render(scene), encoding="utf-8")
        print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
