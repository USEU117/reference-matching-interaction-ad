"""Render the morning report for the 2026-09-17/18 night run.

Why this is a Python file and not part of the PowerShell driver: Windows PowerShell 5.1 decodes a
``.ps1`` file as ANSI (GBK on this machine) unless it carries a UTF-8 BOM, so Chinese text inside
the driver broke the whole script at parse time.  Keeping the driver ASCII-only and rendering the
Chinese report here removes that failure mode entirely.

Usage:
    .venv-anomalyclip/Scripts/python.exe scripts/limitation_closure_20260915/night_report.py

Reads  : <night dir>/NIGHT_RUN_STATUS.json
Writes : <night dir>/NIGHT_RUN_REPORT_CN.md
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NIGHT = ROOT / "scripts/limitation_closure_20260915/_night_20260917"

PHASE_LABEL = {
    "preflight": "环境预检",
    "visa_matrix": "VisA 剩余矩阵",
    "analysis_chain": "C 统计链",
    "btad03_matrix": "G BTAD-03 矩阵",
    "swin_t": "E3 Swin-T 与五编码器表",
    "d3_seed_variance": "D 支持集方差",
}

RESULT_LABEL = {
    "pass": "通过",
    "FAILED": "失败",
    "needs_attention": "需人工确认",
    "skipped": "跳过",
    "skipped_already_done": "已有产物，跳过",
    "started": "已启动",
}


def read_json(path: Path):
    if not path.exists():
        return None
    # utf-8-sig, not utf-8: the status file is written by PowerShell 5.1's Set-Content -Encoding utf8,
    # which emits a BOM, and json.loads rejects a BOM under plain utf-8
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", type=Path, default=NIGHT / "NIGHT_RUN_STATUS.json")
    parser.add_argument("--out", type=Path, default=NIGHT / "NIGHT_RUN_REPORT_CN.md")
    args = parser.parse_args()

    state = read_json(args.status)
    if state is None:
        print(f"[report] no status file at {args.status}")
        return 1

    lines = ["# 夜间运行报告（2026-09-17/18）", ""]
    lines.append(f"- 启动：{state.get('started')}")
    lines.append(f"- 结束：{state.get('finished') or '（仍在运行）'}")
    lines.append(f"- 状态机：`{args.status.as_posix()}`")
    lines.append("")

    lines.append("## 一、各阶段结果")
    lines.append("")
    lines.append("| 阶段 | 名称 | 结果 | 说明 |")
    lines.append("|---|---|---|---|")
    for name, entry in (state.get("phases") or {}).items():
        result = RESULT_LABEL.get(entry.get("result"), entry.get("result"))
        note = str(entry.get("note", "")).replace("|", "/")
        lines.append(f"| `{name}` | {PHASE_LABEL.get(name, name)} | {result} | {note} |")
    lines.append("")

    checks = state.get("checks") or {}
    if checks:
        lines.append("## 二、产物核对")
        lines.append("")
        lines.append("| 项 | 状态 |")
        lines.append("|---|---|")
        for key, value in checks.items():
            lines.append(f"| {key} | {value} |")
        lines.append("")

    d3 = (state.get("phases") or {}).get("d3_seed_variance", {})
    e3 = (state.get("phases") or {}).get("swin_t", {})
    lines.append("## 三、必须人工判断的三个数")
    lines.append("")
    lines.append(
        "1. **C 统计链**：`analysis_chain` 若不是「通过」，去 "
        "`experiments/dynamic_fusion/seeds_extension_20260917/logs_analysis.txt` 看是哪一步退出码非零；"
        "缺哪个产物就从那一步单独补跑（`run_fullpixel.py` / `stats_v2.py` / `analyze_conditions.py` / "
        "`c5_generalization_interactions.py` 都支持单独执行）。"
    )
    lines.append(
        f"2. **D 的 VD.3 回归（BTAD 三类）**：`n_compared={d3.get('vd3_btad_n_compared')}`、"
        f"`max_abs_delta={d3.get('vd3_btad_max_abs_delta')}`、"
        f"`within_1e-9={d3.get('vd3_btad_within_1e_9')}`。"
        "新补的 BTAD-03 单元应与已发布 study 值一致；若量级远大于 1e-9，说明 03 的口径与矩阵不是同一套，"
        "这批数先别写进论文。"
    )
    lines.append(
        "3. **E3 与五编码器表**：确认 `05_extra_encoders/E3/VERIFICATION.json` 的 "
        "`VE_2_single_branch_auroc.pass` 为 true（单支 AUROC 不应掉到 0.5 附近），"
        "并确认 `S10_SUMMARY.json` 已从 4 行扩到 5 行。"
    )
    lines.append("")
    lines.append("## 四、下一步（论文侧）")
    lines.append("")
    lines.append(
        "- 只要 C 的统计链与 C5 落地，第三节「正文缺口」里的四数据集交互表就可以开始写；\n"
        "- D 的方差结论对应「换一批正常参考图结论是否改变」那一节；\n"
        "- E3 落地后 VE.5 表从 4 行变 5 行，图 3/图 4 的槽位要一并重绘；\n"
        "- BTAD-03 的 rev_correct（faithful GT + 坐标正确重网格）仍是独立问题，"
        "需要新代码路径，留给白天，不影响 D 的三类结论。"
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[report] wrote {args.out} at {datetime.now().isoformat(timespec='seconds')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
