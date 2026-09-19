"""Night 2 (2026-09-18) validator: per-phase gates, the phase-0 key-coverage audit and the
final acceptance report.

The orchestrator (`night_run_2_20260918.ps1`) owns the sequence, the lock and the status file.
This script owns every judgement that needs to read an artefact: a phase gate returns a JSON
document with one row per check (`what / expected / actual / pass / evidence`), which the
orchestrator copies into `STATUS.json` and turns into `pass / gate_failed`.

Three modes
-----------
    # one phase gate; the JSON is the verdict, the exit code is 0 unless the file cannot be read
    python night2_validate_20260918.py --phase 2 --out _night2_20260918/gate_phase2.json

    # phase-0 npz key completeness (informational: a missing key is listed, never fatal)
    python night2_validate_20260918.py --keys-coverage --out _night2_20260918/keys_coverage.json

    # final report: VALIDATION_20260918.json + VALIDATION_20260918.md, in Chinese
    python night2_validate_20260918.py --report --status _night2_20260918/STATUS.json \
        --out-json _night2_20260918/VALIDATION_20260918.json \
        --out-md _night2_20260918/VALIDATION_20260918.md

All paths in the JSON are absolute.  Chinese text lives here (Python reads UTF-8), never in the
.ps1 (Windows PowerShell 5.1 decodes an extension-less BOM-less .ps1 as GBK).
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NIGHT = ROOT / "scripts/limitation_closure_20260915/_night2_20260918"
GEN = ROOT / "experiments/dynamic_fusion/generalization_mvtec_visa_20260915"
F = ROOT / "experiments/dynamic_fusion/confirmation_ksdd2_20260918"
NEW = ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
FIGDOCS = ROOT / "docs/figures_reference_matching_20260914"
MSDOCS = ROOT / "docs/manuscript_reference_matching_20260914/figures"

METRIC_KEYS = ("pixel_ap", "pixel_auroc", "image_ap", "image_auroc")
CATS = {
    "mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector", "metal_plate",
             "tubes"],
    "btad": ["01", "02", "03"],
    "mvtec": ["bottle", "cable", "capsule", "carpet", "grid", "hazelnut", "leather",
              "metal_nut", "pill", "screw", "tile", "toothbrush", "transistor", "wood",
              "zipper"],
    "visa": ["candle", "capsules", "cashew", "chewinggum", "fryum", "macaroni1", "macaroni2",
             "pcb1", "pcb2", "pcb3", "pcb4", "pipe_fryum"],
    "ksdd2": ["ksdd2"],
}
# Generalization scope of the phase-0 key audit.
GEN_DATASETS = ("mvtec", "visa")
SEEDS = (0, 1, 2)
SHOTS = (1, 2, 4, 8)
# KSDD2 branches: the DINO branches sit on the frozen 224x630 canvas (patch 14 -> grid 45x16,
# masks 630x224), the AnomalyCLIP branch keeps its own 518x518 preprocess (37x37 grid, 518x518
# masks), exactly as in the published study (verified on
# outputs/.../canonical/C/btad_s0_k8/01.npz = (70,37,37,768) / (70,518,518)).  Asserting the
# DINO canvas for C would fail on a correct export.
KSDD2_BRANCH_SHAPES = {
    "B": {"grid": (45, 16), "dim": 768, "mask": (630, 224)},
    "S": {"grid": (45, 16), "dim": 384, "mask": (630, 224)},
    "C": {"grid": (37, 37), "dim": 768, "mask": (518, 518)},
}
KSDD2_N_QUERY = 1004          # official test split: 110 positive + 894 negative
KSDD2_UNITS = 12              # seeds {0,1,2} x K {1,2,4,8}
FAST_PARITY_TOLERANCE = 1e-12
EXPECTED_SYNC_FILES = 30

NOTES = [
    "KSDD2 的判据是 95% 区间 (ci95)：确认集只有 4 个单元（2 分支 x 2 对比）的单一族，"
    "不套用研究主表的 4 格 Bonferroni 校正 (ci9875)，也不套用 8 格的 ci99375；"
    "c5_generalization_interactions.py 的 PRIMARY_SCOPE 与 CI_LEVELS 未被改动，"
    "KSDD2 只登记在 CATS/ROLE 里，因此它不会进入已发布的四数据集表。",
    "C 分支的画布断言按分支区分：B/S 走 KSDD2 冻结画布 (45,16) / (630,224)，"
    "C 保留自己的 37x37 / 518x518（与已发表研究一致），"
    "engine_v2 在打分时把 C 重网格到 B 的画布。",
    "阶段 3 扩展 E1/E2/E3 后刷新 S10：S10 的 S/D 两列仍来自研究表（seed{0,1} x K{1,4}，"
    "4 个条件），而 E1/E2/E3 的池化改为 12 个条件 (seed{0,1,2} x K{1,2,4,8})。"
    "encoder_comparison_three.csv 的 n_conditions 列会体现这个差别，"
    "encoder_vs_S_difference.csv 的配对差值因此不再是同条件配对——这是本轮的已知口径变化，"
    "需在论文里注明或另行为 S 补跑同范围条件。",
    "编排器相对给定命令的四处有意偏差（均已对照被调脚本核实）："
    "① build_support_manifest 显式加 --out-name support_manifest_ksdd2.json"
    "（单值 --dataset 时其默认名是 support_manifest.json，与下一步 --support-manifest 不一致）；"
    "② run_matrix 与 run_fullpixel 加 --resume（已完成单元无论如何都会跳过，"
    "但 run_matrix 在 PROTOCOL.json 已存在时会直接报错，-Phase 2 补跑将无法继续）；"
    "③ fast_parity_gate.py 用 --output 把本轮证据写进 _night2_20260918，"
    "不覆盖 2026-09-17 的记录；"
    "④ 防休眠改用 Python watchdog 调用同一个 kernel32 接口，因为本机 Add-Type 无法编译任何类型"
    "（Add-Type 会把源码写到 TEMP 后报“找不到源文件”，用一行类型即可复现），"
    "此前夜脚本里的就地 P/Invoke 实际上是静默失效的。",
]


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path):
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:                                    # noqa: BLE001
        return {"_read_error": f"{type(exc).__name__}: {exc}"}


def csv_rows(path: Path):
    if not path.is_file():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def chk(cid: str, what: str, expected, actual, ok: bool, evidence) -> dict:
    return {"id": cid, "what": what, "expected": expected, "actual": actual,
            "pass": bool(ok), "evidence": evidence if isinstance(evidence, list) else [str(evidence)]}


def rel(path) -> str:
    try:
        return str(Path(path).relative_to(ROOT))
    except ValueError:
        return str(path)


def finish(phase, checks, extra=None) -> dict:
    doc = {"phase": phase, "created_utc": utcnow(), "pass": all(c["pass"] for c in checks),
           "checks": checks}
    if extra:
        doc.update(extra)
    doc["n_failed"] = sum(1 for c in checks if not c["pass"])
    return doc


# --------------------------------------------------------------------------- phase 0
def gate_phase0() -> dict:
    checks = []
    p2 = GEN / "p2_conditions"
    files = sorted(p for p in p2.glob("*") if p.is_file() and p.stat().st_size > 0) \
        if p2.is_dir() else []
    checks.append(chk("p2_conditions_nonempty", "阶段 0 的条件分析产物目录非空",
                      ">=1 个非空文件", "%d 个文件: %s" % (len(files), ", ".join(
                          p.name for p in files[:8])),
                      bool(files), rel(p2)))
    effects = p2 / "per_category_effects.csv"
    rows = csv_rows(effects)
    checks.append(chk("p2_conditions_effects_rows", "per_category_effects.csv 有数据行",
                      ">0 行", "%d 行" % len(rows), len(rows) > 0, rel(effects)))
    gen_csv = GEN / "interaction_generalization.csv"
    gen_rows = csv_rows(gen_csv)
    checks.append(chk("interaction_generalization_rows",
                      "interaction_generalization.csv 存在且行数 > 0",
                      ">0 行", "%d 行" % len(gen_rows), len(gen_rows) > 0, rel(gen_csv)))
    return finish(0, checks)


# --------------------------------------------------------------------------- phase 1
def gate_phase1() -> dict:
    checks = []
    par = NIGHT / "FAST_ESTIMATOR_PARITY.json"
    doc = load_json(par)
    passed = bool(isinstance(doc, dict) and doc.get("pass") is True)
    checks.append(chk("fast_estimator_parity", "既有快估计器门（fast_parity_gate.py）通过",
                      "pass=True, 阈值 1e-9",
                      json.dumps({k: doc.get(k) for k in
                                  ("pass", "max_abs_delta", "tolerance", "n_units_compared",
                                   "units_compared")} if isinstance(doc, dict) else doc,
                                 ensure_ascii=False) if doc else "文件缺失",
                      passed, rel(par)))
    if isinstance(doc, dict):
        worst = doc.get("max_abs_delta")
        checks.append(chk("fast_estimator_delta", "最大逐副本偏差不超过 1e-9",
                          "<= 1e-9", worst, isinstance(worst, (int, float)) and worst <= 1e-9,
                          rel(par)))

    ks = NIGHT / "FAST_PARITY_KSDD2.json"
    kdoc = load_json(ks)
    kpass = bool(isinstance(kdoc, dict) and kdoc.get("pass") is True)
    checks.append(chk("ksdd2_fast_parity", "KSDD2 真单元上的快/慢实现对照通过",
                      "pass=True, R=20, max|delta| <= 1e-12",
                      json.dumps({k: kdoc.get(k) for k in
                                  ("pass", "replicates", "max_abs_delta_arrays",
                                   "point_max_abs_delta", "n_units_compared", "units")}
                                 if isinstance(kdoc, dict) else kdoc, ensure_ascii=False)
                      if kdoc else "文件缺失（阶段 2 之后补跑，或矩阵不存在）",
                      kpass, rel(ks)))
    if isinstance(kdoc, dict):
        worst = kdoc.get("max_abs_delta_arrays")
        checks.append(chk("ksdd2_fast_parity_tolerance", "KSDD2 逐副本最大偏差 <= 1e-12",
                          "<= 1e-12",
                          worst, isinstance(worst, (int, float)) and worst <= FAST_PARITY_TOLERANCE,
                          rel(ks)))
    return finish(1, checks)


# --------------------------------------------------------------------------- phase 2
def ksdd2_matrix_units() -> list:
    root = F / "p1_matrix/units"
    return sorted(root.glob("ksdd2_s*_k*/ksdd2/DONE.json")) if root.is_dir() else []


def gate_phase2() -> dict:
    checks = []
    for branch in ("B", "S", "C"):
        shapes = KSDD2_BRANCH_SHAPES[branch]
        paths = [F / "canonical" / branch / f"ksdd2_s{seed}_k8" / "ksdd2.npz" for seed in SEEDS]
        missing = [rel(p) for p in paths if not p.is_file()]
        checks.append(chk(f"canonical_{branch}_exists", f"canonical {branch} 三份 k8 缓存存在",
                          "3/3 存在", "缺 %d 个" % len(missing), not missing,
                          [rel(p) for p in paths] if not missing else missing))
        if missing:
            checks.append(chk(f"canonical_{branch}_shape", f"canonical {branch} 形状断言",
                              "跳过（文件缺失）", "n/a", False, missing))
            continue
        bad, seen = [], []
        for path in paths:
            with np.load(path, allow_pickle=False) as z:
                pf = np.asarray(z["patch_features"]).shape
                mk = np.asarray(z["imgs_masks"]).shape
                gr = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
            seen.append({"file": rel(path), "patch_features": list(pf), "imgs_masks": list(mk),
                         "grid_size": list(gr)})
            if len(pf) != 4 or (pf[1], pf[2]) != shapes["grid"] or pf[3] != shapes["dim"]:
                bad.append("%s patch_features=%s != (N,%d,%d,%d)"
                           % (rel(path), pf, shapes["grid"][0], shapes["grid"][1], shapes["dim"]))
            if len(mk) != 3 or (mk[1], mk[2]) != shapes["mask"]:
                bad.append("%s imgs_masks=%s != (N,%d,%d)"
                           % (rel(path), mk, shapes["mask"][0], shapes["mask"][1]))
            if gr != shapes["grid"]:
                bad.append("%s grid_size=%s != %s" % (rel(path), gr, shapes["grid"]))
            if pf[0] != KSDD2_N_QUERY:
                bad.append("%s N=%d != %d" % (rel(path), pf[0], KSDD2_N_QUERY))
        checks.append(chk(f"canonical_{branch}_shape", f"canonical {branch} 形状断言",
                          "patch_features (N,%d,%d,%d), imgs_masks (N,%d,%d), N=%d"
                          % (shapes["grid"][0], shapes["grid"][1], shapes["dim"],
                             shapes["mask"][0], shapes["mask"][1], KSDD2_N_QUERY),
                          "全部符合" if not bad else "; ".join(bad), not bad, seen))

    units = ksdd2_matrix_units()
    checks.append(chk("matrix_done_units", "KSDD2 矩阵 12 个单元 DONE.json 齐全",
                      "%d/12" % KSDD2_UNITS, "%d/12" % len(units),
                      len(units) >= KSDD2_UNITS, rel(F / "p1_matrix")))

    npz = F / "p1_statistics/bootstrap_samples.npz"
    if not npz.is_file():
        checks.append(chk("statistics_keys", "bootstrap_samples.npz 键覆盖 12 条件",
                          "12 条件 x 全部 method x 4 metric", "文件缺失", False, rel(npz)))
    else:
        with np.load(npz, allow_pickle=False) as z:
            keys = list(z.files)
            per_condition, deficits = [], []
            for seed in SEEDS:
                for shot in SHOTS:
                    cond = f"ksdd2_s{seed}_k{shot}"
                    mdir = F / "p1_matrix/units" / cond / "ksdd2/metrics.csv"
                    methods = [r["method"] for r in csv_rows(mdir)]
                    prefix = f"percat__{cond}__"
                    miss = []
                    for method in methods:
                        for metric in METRIC_KEYS:
                            key = f"{prefix}{method}__{metric}"
                            if key not in keys:
                                miss.append(f"{method}/{metric}")
                    shape_ok = True
                    if methods:
                        ref = f"{prefix}{methods[0]}__pixel_ap"
                        if ref in keys:
                            arr = np.asarray(z[ref])
                            shape_ok = arr.ndim == 2 and arr.shape[1] == 1
                    per_condition.append({"condition": cond, "n_methods": len(methods),
                                          "n_missing_slots": len(miss),
                                          "first_missing": miss[:4], "shape_ok": shape_ok})
                    if miss or not methods or not shape_ok:
                        deficits.append(cond)
                    if not methods:
                        deficits.append(cond + "(无 metrics.csv)")
            checks.append(chk("statistics_keys", "bootstrap_samples.npz 键覆盖 12 条件",
                              "12 条件 x 全部 method x 4 metric（类别维 = 1）",
                              "%d/%d 条件无缺口; 缺口: %s"
                              % (len(per_condition) - len([d for d in deficits]),
                                 12, ", ".join(deficits) or "无"),
                              not deficits and len(per_condition) == 12 and len(units) >= 12,
                              rel(npz)))
        checks.append(chk("statistics_npz_keys", "bootstrap_samples.npz 至少含 ksdd2 键",
                          ">0", "%d 个键" % len(keys), len(keys) > 0, rel(npz)))

    ibc = F / "02_interaction/interaction_by_condition.csv"
    rows = csv_rows(ibc)
    checks.append(chk("interaction_by_condition_rows", "02_interaction/interaction_by_condition.csv 行数 > 0",
                      ">0 行", "%d 行" % len(rows), len(rows) > 0, rel(ibc)))
    ine = F / "04_new_encoder/interaction_new_encoder.csv"
    rows2 = csv_rows(ine)
    checks.append(chk("interaction_new_encoder_rows", "04_new_encoder/interaction_new_encoder.csv 行数 > 0",
                      ">0 行", "%d 行" % len(rows2), len(rows2) > 0, rel(ine)))
    # provenance only: the two intermediate tables are not part of the gate
    extra = {"info": {
        "03_robustness_K_curve": rel(NEW / "03_robustness/interaction_K_curve.csv"),
        "F_03_robustness_K_curve": rel(F / "03_robustness/interaction_K_curve.csv"),
        "p4_fullpixel_csv": rel(F / "p4_fullpixel/fullpixel_metrics.csv"),
        "p4_fullpixel_csv_exists": (F / "p4_fullpixel/fullpixel_metrics.csv").is_file(),
    }}
    return finish(2, checks, extra)


# --------------------------------------------------------------------------- phase 3
def gate_phase3() -> dict:
    checks = []
    expected = len(CATS["mpdd"]) * len(SEEDS) * len(SHOTS) * 1 \
        + len(CATS["btad"]) * len(SEEDS) * len(SHOTS) * 2
    for branch in ("E1", "E2", "E3"):
        root = NEW / "05_extra_encoders" / branch / "units"
        found = sorted(root.rglob("evaluation_scores.npz")) if root.is_dir() else []
        ids = {str(p.relative_to(root)).replace("\\", "/") for p in found}
        checks.append(chk(f"units_{branch}", f"{branch} 单元数达到扩展后的预期",
                          ">= %d (MPDD 6x3x4x1 + BTAD 3x3x4x2)" % expected,
                          "%d" % len(ids), len(ids) >= expected, rel(root)))
    s10 = NEW / "05_extra_encoders/S10_SUMMARY.json"
    doc = load_json(s10)
    encoders = list((doc or {}).get("encoders") or {}) if isinstance(doc, dict) else []
    checks.append(chk("s10_five_encoders", "S10 五编码器表含 5 个编码器",
                      "{'S','D','E1','E2','E3'}",
                      "%d 个: %s" % (len(encoders), ",".join(encoders)),
                      set(encoders) >= {"S", "D", "E1", "E2", "E3"}, rel(s10)))
    if isinstance(doc, dict):
        rows = csv_rows(NEW / "05_extra_encoders/encoder_comparison_three.csv")
        counts = sorted({r.get("n_conditions") for r in rows
                         if r.get("encoder_key") in ("E1", "E2", "E3")} - {None, ""})
        counts_s = sorted({r.get("n_conditions") for r in rows
                           if r.get("encoder_key") == "S"} - {None, ""})
        checks.append(chk("s10_condition_scope",
                          "S10 记录的条件数（E 分支已扩展，S/D 仍为研究范围）",
                          "E 分支 12，S/D 4（已知口径变化，仅记录）",
                          "E=%s, S=%s" % (counts, counts_s),
                          True, rel(NEW / "05_extra_encoders/encoder_comparison_three.csv")))
    return finish(3, checks)


# --------------------------------------------------------------------------- phase 4
def gate_phase4() -> dict:
    checks = []
    out = NEW / "05_baselines_multi_dataset"
    files = sorted(p for p in out.glob("*") if p.is_file()) if out.is_dir() else []
    checks.append(chk("multi_dataset_dir", "05_baselines_multi_dataset 目录有结果文件",
                      ">=4 个文件", "%d 个" % len(files), len(files) >= 4, rel(out)))
    csv_path = out / "baseline_common_region.csv"
    rows = csv_rows(csv_path)
    have = sorted({r.get("dataset") for r in rows if r.get("dataset")})
    want = ["mpdd", "btad", "mvtec", "visa"]
    checks.append(chk("common_region_four_datasets", "共同区域表覆盖 4 个数据集",
                      "含 %s" % ",".join(want), "含 %s" % ",".join(have),
                      set(want) <= set(have), rel(csv_path)))
    summary = out / "S8_SUMMARY.json"
    checks.append(chk("s8_summary", "S8_SUMMARY.json 存在", "存在", summary.is_file(),
                      summary.is_file(), rel(summary)))
    pc = NEW / "05_baselines/patchcore_official224"
    units = sorted(p.name for p in pc.glob("*_s*_k*") if p.is_dir()) if pc.is_dir() else []
    checks.append(chk("patchcore_units", "PatchCore official224 单元目录（信息记录）",
                      "记录", "%d 个: %s" % (len(units), ",".join(units[:10])),
                      True, rel(pc)))
    return finish(4, checks)


# --------------------------------------------------------------------------- phase 5
def parse_log(path: Path) -> str:
    """Read a phase log, sniffing the encoding.

    The orchestrator redirects native-command output with PowerShell 5.1's `1>>`, which writes
    UTF-16LE with a BOM.  Reading such a file as UTF-8 yields NUL-interleaved text in which no
    ASCII marker matches, which is exactly how the phase-5 gate came to report "log line
    missing" for lines that were present in the log (`TOTAL PROBLEMS: 0`, the font floor line
    and the sync summary).  Sniff the BOM; fall back to utf-8.
    """
    if not path.is_file():
        return ""
    raw = path.read_bytes()
    for bom, encoding in ((b"\xff\xfe", "utf-16"), (b"\xfe\xff", "utf-16"),
                          (b"\xef\xbb\xbf", "utf-8-sig")):
        if raw.startswith(bom):
            return raw.decode(encoding, errors="replace")
    return raw.decode("utf-8", errors="replace")


def gate_phase5(log_dir: Path) -> dict:
    checks = []
    log = parse_log(log_dir / "phase_5_figures.log")
    err = parse_log(log_dir / "phase_5_figures.err")

    m = None
    for line in log.splitlines():
        if "TOTAL PROBLEMS:" in line:
            m = line.split("TOTAL PROBLEMS:")[-1].strip()
    checks.append(chk("qa_layout_zero_problems", "qa_layout.py 几何/字号门禁 0 problem",
                      "TOTAL PROBLEMS: 0", "TOTAL PROBLEMS: %s" % m if m is not None else "日志中无该行",
                      m == "0", [rel(log_dir / "phase_5_figures.log")]))

    floors = []
    for line in log.splitlines():
        if "BODY_PT=" in line:
            floors.append(line.strip())
    ok_floor = bool(floors) and "floor_ok=True" in floors[-1]
    checks.append(chk("font_gate_floor", "figure_font_gate.py 下限配置 >= 11 pt",
                      "BODY_PT>=11 且 DEFAULT_PT>=11", floors[-1] if floors else "未运行",
                      ok_floor, [rel(log_dir / "phase_5_figures.log")]))

    total = copied = identical = None
    for line in log.splitlines():
        hit = re.search(r"\[sync\]\s*(\d+)\s*file\(s\):\s*(\d+)\s*new,\s*(\d+)\s*to update,"
                        r"\s*(\d+)\s*already identical", line)
        if hit:
            total, identical = int(hit.group(1)), int(hit.group(4))
        hit = re.search(r"\[sync\]\s*copied\s+(\d+)\s*file\(s\)", line)
        if hit:
            copied = int(hit.group(1))
    handled = (None if total is None else
               (identical if identical == total else (identical or 0) + (copied or 0)))
    ok_sync = total is not None and total > 0 and handled == total
    checks.append(chk("sync_all_files", "sync_to_manuscript.py --apply 清单全部成功",
                      "全部 %d 个文件（复制或已一致）" % EXPECTED_SYNC_FILES,
                      "total=%s identical=%s copied=%s" % (total, identical, copied),
                      ok_sync, [rel(log_dir / "phase_5_figures.log")]))
    checks.append(chk("sync_count_matches_note", "同步文件数与本轮预期一致（仅记录）",
                      "%d" % EXPECTED_SYNC_FILES,
                      str(total), True, [rel(log_dir / "phase_5_figures.log")]))

    pngs = sorted(p.name for p in FIGDOCS.glob("*.png")) if FIGDOCS.is_dir() else []
    checks.append(chk("figure_pngs", "图件目录有 PNG 产物", ">=7 个", "%d 个" % len(pngs),
                      len(pngs) >= 7, rel(FIGDOCS)))
    # Informational: node/matplotlib can write warnings to stderr on a fully successful run, so
    # this is recorded rather than enforced (the step exit codes and the parsed assertions above
    # are the actual verdict).
    checks.append(chk("stderr_record", "阶段 5 stderr 记录（信息性，不作门禁）",
                      "记录", "%d 字符: %s" % (len(err.strip()), err.strip()[:200] or "(empty)"),
                      True, [rel(log_dir / "phase_5_figures.err")]))
    return finish(5, checks)


# --------------------------------------------------------------------------- key coverage
def keys_coverage(npz: Path) -> dict:
    doc = {"npz": str(npz), "created_utc": utcnow(),
           "note": ("信息性检查：缺键只记录并写入验收报告，不中断后续阶段"),
           "metrics": list(METRIC_KEYS), "seeds": list(SEEDS), "shots": list(SHOTS)}
    if not npz.is_file():
        doc.update({"exists": False, "n_conditions_expected": len(GEN_DATASETS) * len(SEEDS)
                    * len(SHOTS), "n_conditions_full": 0, "conditions": []})
        return doc
    with np.load(npz, allow_pickle=False) as z:
        keys = list(z.files)
        perfiles = [k for k in keys if k.startswith("percat__")]
        doc["exists"] = True
        doc["n_keys"] = len(keys)
        doc["n_percat_keys"] = len(perfiles)
        expected_methods = {}
        conditions = []
        for dataset in GEN_DATASETS:
            methods_seen = set()
            for k in perfiles:
                head = k[len("percat__"):]
                if "__" not in head:
                    continue
                cond, rest = head.split("__", 1)
                if not cond.startswith(f"{dataset}_s"):
                    continue
                methods_seen.add(rest.rsplit("__", 1)[0])
            expected_methods[dataset] = sorted(methods_seen)
        doc["datasets"] = {d: {"expected_methods": expected_methods[d], "categories": CATS[d]}
                           for d in GEN_DATASETS}
        for dataset in GEN_DATASETS:
            for seed in SEEDS:
                for shot in SHOTS:
                    cond = f"{dataset}_s{seed}_k{shot}"
                    prefix = f"percat__{cond}__"
                    present = {}
                    for k in perfiles:
                        if not k.startswith(prefix):
                            continue
                        rest = k[len(prefix):]
                        if "__" not in rest:
                            continue
                        method, metric = rest.rsplit("__", 1)
                        present.setdefault(method, {})[metric] = k
                    if not present:
                        conditions.append({"dataset": dataset, "seed": seed, "shot": shot,
                                           "present": False, "n_methods_present": 0,
                                           "missing_methods": expected_methods[dataset],
                                           "missing_metric_slots": len(expected_methods[dataset])
                                           * len(METRIC_KEYS), "shape_anomalies": [
                                               "条件在 npz 中完全缺失"]})
                        continue
                    missing_methods = [m for m in expected_methods[dataset] if m not in present]
                    slots, anomalies, shapes = [], [], {}
                    for m, metrics in sorted(present.items()):
                        for metric in METRIC_KEYS:
                            if metric not in metrics:
                                slots.append(f"{m}/{metric}")
                        ref = metrics.get("pixel_ap")
                        if ref is not None:
                            arr = np.asarray(z[ref])
                            shapes[m] = list(arr.shape)
                            if arr.ndim != 2 or arr.shape[1] != len(CATS[dataset]):
                                anomalies.append("%s pixel_ap array=%s != (R,%d)"
                                                 % (m, list(arr.shape), len(CATS[dataset])))
                    conditions.append({
                        "dataset": dataset, "seed": seed, "shot": shot, "present": True,
                        "n_methods_present": len(present),
                        "n_methods_expected": len(expected_methods[dataset]),
                        "missing_methods": missing_methods,
                        "missing_metric_slots": len(slots),
                        "first_missing_slots": slots[:6],
                        "shape_anomalies": anomalies,
                        "shapes": shapes})
        doc["n_conditions_expected"] = len(GEN_DATASETS) * len(SEEDS) * len(SHOTS)
        doc["n_conditions_full"] = sum(1 for c in conditions if c["present"]
                                       and not c["missing_methods"]
                                       and not c["missing_metric_slots"]
                                       and not c["shape_anomalies"])
        doc["n_conditions_missing"] = sum(1 for c in conditions if not c["present"])
        doc["conditions_incomplete"] = [
            {k: c[k] for k in ("dataset", "seed", "shot", "n_methods_present",
                               "missing_methods", "missing_metric_slots", "shape_anomalies")}
            for c in conditions
            if (not c["present"] or c["missing_methods"] or c["missing_metric_slots"]
                or c["shape_anomalies"])]
        doc["conditions"] = conditions
    return doc


# --------------------------------------------------------------------------- report
def verdict_of(status: dict) -> str:
    # `pass_reverified` is a phase whose gate was re-run after the blocking issue was fixed and
    # whose gate JSON now records `pass: true` (the original status stays in the record's
    # `status_before_reconcile` and the reason in `reconcile_note`).  See
    # night2_refresh_gate_snapshots.py.
    phases = (status or {}).get("phases") or {}
    if not phases:
        return "unknown"
    bad = [p for p in phases.values() if p.get("status") not in
           ("pass", "pass_reverified", "skipped", "skipped_by_request")]
    return "pass" if not bad else ("partial" if any(
        p.get("status") in ("pass", "pass_reverified", "skipped") for p in phases.values())
        else "fail")


def flatten_checks(status: dict) -> list:
    out = []
    for pid in sorted((status or {}).get("phases") or {}, key=lambda k: str(k)):
        phase = (status["phases"][pid] or {})
        gate = phase.get("gate") or {}
        for c in (gate.get("checks") or []):
            out.append({"phase": pid, "status": phase.get("status"), **c})
    return out


CN_NUM = ("零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十")


def md_report(doc: dict) -> str:
    lines = []
    section = {"n": 0}

    def head(title: str) -> None:
        section["n"] += 1
        lines.append("## %s、%s" % (CN_NUM[section["n"]], title))
        lines.append("")

    lines.append("# 2026-09-18 夜间批次验收报告")
    lines.append("")
    lines.append("- 生成时间（UTC）：%s" % doc["created_utc"])
    lines.append("- 编排器：`scripts/limitation_closure_20260915/night_run_2_20260918.ps1`")
    lines.append("- 状态文件：`%s`" % rel(doc["status_path"]))
    lines.append("- 总体结论：**%s**" % doc["verdict"])
    lines.append("")
    head("口径说明（先读）")
    for note in doc["notes"]:
        lines.append("- %s" % note)
    lines.append("")
    head("阶段总览")
    lines.append("| 阶段 | 名称 | 状态 | 退出码 | 开始(UTC) | 结束(UTC) | 门禁 | 产物 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for pid, phase in sorted(doc["phases"].items(), key=lambda kv: str(kv[0])):
        gate = phase.get("gate") or {}
        gate_s = "未跑" if not gate else ("PASS" if gate.get("pass") else "FAIL(%s)" %
                                          gate.get("n_failed"))
        arts = "<br>".join("`%s`" % a for a in (phase.get("artifacts") or [])[:6])
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            pid, phase.get("name", ""), phase.get("status", ""),
            phase.get("exit_code", ""), phase.get("started_utc", ""),
            phase.get("finished_utc", ""), gate_s, arts))
    lines.append("")
    head("逐项检查（阶段 / 检查项 / 期望 / 实测 / 结果 / 证据）")
    lines.append("| 阶段 | 检查项 | 期望 | 实测 | 结果 | 证据 |")
    lines.append("|---|---|---|---|---|---|")
    for c in doc["checks"]:
        evidence = "<br>".join("`%s`" % e for e in (c.get("evidence") or [])[:3])
        lines.append("| %s | %s | %s | %s | %s | %s |" % (
            c["phase"], c.get("what", c.get("id")), str(c.get("expected"))[:160],
            str(c.get("actual"))[:160], "PASS" if c.get("pass") else "FAIL", evidence))
    lines.append("")
    if doc.get("keys_coverage"):
        kc = doc["keys_coverage"]
        head("阶段 0 键完整性（信息性，不阻断）")
        lines.append("- npz：`%s`（存在=%s，键数=%s）" % (kc.get("npz"), kc.get("exists"),
                                                          kc.get("n_keys")))
        lines.append("- 条件：完整 %s / %s，完全缺失 %s" % (
            kc.get("n_conditions_full"), kc.get("n_conditions_expected"),
            kc.get("n_conditions_missing")))
        for dataset, info in (kc.get("datasets") or {}).items():
            lines.append("- %s：method %s，类别 %d 个" % (
                dataset, ",".join(info.get("expected_methods") or []),
                len(info.get("categories") or [])))
        incomplete = kc.get("conditions_incomplete") or []
        if incomplete:
            lines.append("")
            lines.append("| 条件 | method 数 | 缺失 method | 缺失槽位 | 形状异常 |")
            lines.append("|---|---|---|---|---|")
            for c in incomplete:
                lines.append("| %s_s%s_k%s | %s | %s | %s | %s |" % (
                    c["dataset"], c["seed"], c["shot"], c.get("n_methods_present"),
                    ",".join(c.get("missing_methods") or []) or "-",
                    c.get("missing_metric_slots"), "; ".join(c.get("shape_anomalies") or []) or "-"))
        else:
            lines.append("- 24 个条件的 method x 4 metric x 类别维均完整")
        lines.append("")
    if doc.get("ps_parse_check"):
        head("编排器解析自检（PowerShell 解析器 0 error）")
        lines.append("```json")
        lines.append(json.dumps(doc["ps_parse_check"], ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")
    git = doc.get("git") or {}
    head("git 收口")
    lines.append("- 分支：%s" % git.get("branch"))
    lines.append("- 提交前 `git status --porcelain` 行数：%s" % git.get("status_lines"))
    lines.append("")
    lines.append("提交前 `git status --porcelain` 摘要（前 40 行）：")
    lines.append("")
    lines.append("```")
    for line in git.get("status_head") or []:
        lines.append(line)
    lines.append("```")
    lines.append("")
    lines.append("提交前 `git diff --stat` 摘要：")
    lines.append("")
    lines.append("```")
    lines.append((git.get("diff_stat") or "").strip()[:4000])
    lines.append("```")
    lines.append("")
    for commit in git.get("commits") or []:
        lines.append("- `%s` %s" % (commit.get("sha"), commit.get("subject")))
    if git.get("tag"):
        lines.append("- tag：`%s`" % git["tag"])
    if git.get("skipped"):
        lines.append("- 未提交（-NoGit）：%s" % git["skipped"])
    lines.append("")
    head("未决与不确定性")
    for item in doc.get("uncertainties") or []:
        lines.append("- %s" % item)
    lines.append("")
    return "\n".join(lines)


UNCERTAINTIES = [
    "`figure_font_gate.py` 没有命令行入口（它只提供 assert_min_font_pt 等函数，由 matplotlib "
    "图脚本内部调用），因此阶段 5 的“字号门禁”实测证据是 qa_layout.py 的 "
    "TOTAL PROBLEMS/min pt 行 + 该模块的下限常量自检；若需要真正的逐 artist 断言，"
    "要重跑 build_qualitative_figures.py / build_figS2_ablation.py / build_figS3_extra_cases.py。",
    "阶段 1 的 KSDD2 对照依赖阶段 2 产出的矩阵单元；若阶段 2 未产出任何 DONE.json，"
    "该检查记为 gate_failed（不是 pass），并在报告里保留原因。",
    "阶段 4 的 PatchCore 剩余单元数（任务描述为 6）未在脚本层面重新核验，"
    "编排器按 -SkipExisting 全量串行跑，实际单元数以日志清单为准。",
    "阶段 5 只在阶段 0 的 gate 通过时才保证图 4(b) 的 MVTec/VisA 行出现；"
    "若阶段 0 失败，阶段 5 仍会运行（软依赖），图 4(b) 会退回只画 MPDD/BTAD，"
    "该情况会记录在 STATUS.json 的 dependencies 字段。",
]


def build_report(args) -> int:
    status = load_json(Path(args.status)) or {}
    doc = {
        "created_utc": utcnow(),
        "kind": "night2_validation",
        "status_path": str(Path(args.status).resolve()),
        "verdict": verdict_of(status),
        "notes": NOTES,
        "phases": status.get("phases") or {},
        "checks": flatten_checks(status),
        "keys_coverage": load_json(NIGHT / "keys_coverage.json"),
        "ps_parse_check": load_json(NIGHT / "PS_PARSE_CHECK.json"),
        "git": {
            "branch": status.get("git", {}).get("branch"),
            "status_lines": status.get("git", {}).get("status_lines"),
            "status_head": (NIGHT / "git_status.txt").read_text(encoding="utf-8-sig").splitlines()[:40]
            if (NIGHT / "git_status.txt").is_file() else [],
            "diff_stat": (NIGHT / "git_diff_stat.txt").read_text(encoding="utf-8-sig")
            if (NIGHT / "git_diff_stat.txt").is_file() else None,
            "commits": status.get("git", {}).get("commits") or [],
            "tag": status.get("git", {}).get("tag"),
            "skipped": status.get("git", {}).get("skipped"),
        },
        "uncertainties": UNCERTAINTIES,
        "environment": status.get("environment") or {},
    }
    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    md = md_report(doc)
    Path(args.out_md).write_text(md + "\n", encoding="utf-8")
    print("[validate] verdict=%s phases=%d checks=%d" % (doc["verdict"], len(doc["phases"]),
                                                         len(doc["checks"])))
    print("[validate] wrote %s" % out_json)
    print("[validate] wrote %s" % args.out_md)
    return 0


# --------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", type=int, choices=(0, 1, 2, 3, 4, 5))
    ap.add_argument("--keys-coverage", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--status", type=Path, default=NIGHT / "STATUS.json")
    ap.add_argument("--out-json", type=Path, default=NIGHT / "VALIDATION_20260918.json")
    ap.add_argument("--out-md", type=Path, default=NIGHT / "VALIDATION_20260918.md")
    ap.add_argument("--log-dir", type=Path, default=NIGHT)
    args = ap.parse_args()

    if args.report:
        return build_report(args)
    if args.keys_coverage:
        doc = keys_coverage(GEN / "p1_statistics/bootstrap_samples.npz")
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({k: v for k, v in doc.items() if k != "conditions"}, ensure_ascii=False,
                         indent=2))
        return 0
    if args.phase is None:
        ap.error("one of --phase / --keys-coverage / --report is required")

    docs = {0: gate_phase0, 1: gate_phase1, 2: gate_phase2, 3: gate_phase3, 4: gate_phase4}
    doc = gate_phase5(args.log_dir) if args.phase == 5 else docs[args.phase]()
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[gate] phase %d pass=%s failed=%d" % (doc["phase"], doc["pass"], doc["n_failed"]))
    for c in doc["checks"]:
        print("  %-28s %s  expected=%s actual=%s" % (
            c["id"], "PASS" if c["pass"] else "FAIL", str(c["expected"])[:70],
            str(c["actual"])[:90]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
