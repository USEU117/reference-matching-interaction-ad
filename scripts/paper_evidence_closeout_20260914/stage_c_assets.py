"""Stage C assets: verified literature difference table, claim->table map, paper draft.

Literature verification was done against the live records on 2026-09-14:
  M3DM            arXiv:2303.00601v2 (CVPR 2023)     - abstract read
  Fusion arch.    arXiv:2412.17297v1                 - abstract read
  CIF             arXiv:2511.05966v2 (AAAI 2026)     - abstract read
  Sea-CLIP        WACV 2026 open access listing      - title/authors/venue read

None of the four studies the same construction as this work: two are multimodal
(RGB + point cloud) 3D-AD, one is a CLIP semantic-representation method for few-shot
AD, one studies fusion architecture for 3D-AD.  Page-level verification of their
experiment sections is still outstanding and is marked as such.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S = (ROOT / "experiments/dynamic_fusion/paper_evidence_closeout_20260914").resolve()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_csv(path: Path, rows, fields=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    fields = fields or list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


WORKS = [
    {"work": "M3DM", "venue": "CVPR 2023", "version_checked": "arXiv:2303.00601v2",
     "link": "https://arxiv.org/abs/2303.00601",
     "modality": "RGB + point cloud (MVTec-3D AD)",
     "same_rgb_multi_encoder": "no", "normal_k_shot": "no (trained on the full normal set)",
     "fixed_weights": "no (patch-wise contrastive feature fusion learned; decision-layer fusion)",
     "shared_support_row": "no (separate memory bank per modality)",
     "copy_control": "no", "JL_intervention": "no", "budget_condition_analysis": "no",
     "evidence": "abstract: 'hybrid fusion ... unsupervised feature fusion with patch-wise "
                 "contrastive learning ... decision layer fusion with multiple memory banks'",
     "difference": ("related on 'multiple memory banks' but multimodal RGB+3D, learned fusion, no "
                    "controlled shared-vs-independent reference-row intervention and no support "
                    "budget study"),
     "verification_status": "abstract_verified"},
    {"work": "Revisiting Multimodal Fusion for 3D-AD",
     "venue": "arXiv preprint", "version_checked": "arXiv:2412.17297v1",
     "link": "https://arxiv.org/abs/2412.17297",
     "modality": "RGB + point cloud (3D-AD)",
     "same_rgb_multi_encoder": "no",
     "normal_k_shot": "partly (mentions few-shot 3D-AD as a use case)",
     "fixed_weights": "no (searches fusion strategies and modules)",
     "shared_support_row": "no", "copy_control": "no", "JL_intervention": "no",
     "budget_condition_analysis": "no",
     "evidence": "abstract: 'systematic study on the impact of multimodal fusion architecture ... "
                 "3D-ADNAS ... exhibits great potential in dealing with few-shot 3D-AD tasks'",
     "difference": ("also a controlled study of fusion design, but it varies architecture/topology "
                    "and searches modules on 3D-AD, not the reference-matching axis of a fixed "
                    "weighted multi-encoder memory under a support budget"),
     "verification_status": "abstract_verified"},
    {"work": "Sea-CLIP", "venue": "WACV 2026", "version_checked": "CVF open-access listing",
     "link": ("https://openaccess.thecvf.com/content/WACV2026/papers/Guo_Sea-CLIP_Mining_"
              "Semantic-Aware_Representations_for_Few-Shot_Anomaly_Detection_with_CLIP_WACV_"
              "2026_paper.pdf"),
     "modality": "RGB + CLIP text semantics",
     "same_rgb_multi_encoder": "no", "normal_k_shot": "yes (few-shot)",
     "fixed_weights": "n/a (learned semantic-aware representation)",
     "shared_support_row": "not verified", "copy_control": "no", "JL_intervention": "no",
     "budget_condition_analysis": "not verified",
     "evidence": "WACV 2026 open-access entry: Guo, Chen, Castillo, Wang, Liu - 'Sea-CLIP: Mining "
                 "Semantic-Aware Representations for Few-Shot Anomaly Detection with CLIP'",
     "difference": ("few-shot + CLIP, but no multi-RGB-encoder fusion and no controlled "
                    "reference-matching comparison; page-level reading of its experiments is still "
                    "outstanding"),
     "verification_status": "listing_verified_page_level_pending"},
    {"work": "CIF (Commonality In Few)", "venue": "AAAI 2026",
     "version_checked": "arXiv:2511.05966v2", "link": "https://arxiv.org/abs/2511.05966",
     "modality": "RGB + point cloud (MVTec 3D-AD, Eyecandies)",
     "same_rgb_multi_encoder": "no", "normal_k_shot": "yes (few-shot multimodal)",
     "fixed_weights": "no (hypergraph construction + message passing)",
     "shared_support_row": ("partly - a hyperedge-guided memory search module, but no controlled "
                            "shared-vs-independent comparison"),
     "copy_control": "no", "JL_intervention": "no",
     "budget_condition_analysis": "no (few-shot setting is fixed, K is not varied against a "
                                  "fixed weighting)",
     "evidence": "abstract: 'few-shot unsupervised multimodal ... hypergraphs to capture the "
                 "structural commonality ... memory bank ... hyperedge-guided memory search "
                 "module ... MVTec 3D-AD and Eyecandies'",
     "difference": ("closest in spirit: few-shot + memory bank + a memory-search mechanism; but "
                    "multimodal 3D+RGB, no fixed-weight copy control, and no K-budget effect "
                    "analysis"),
     "verification_status": "abstract_verified"},
]


def literature() -> dict:
    path = S / "03_paper/literature_difference_verified.csv"
    write_csv(path, WORKS)
    lines = ["# 最相近文献差异表（2026-09-14 核对）", "",
             "核对方式：读取 arXiv 摘要页/CVF 公开条目原文元数据（见 `version_checked` 列）。"
             "M3DM、arXiv:2412.17297、CIF 读到摘要全文；Sea-CLIP 只核到条目级（标题/作者/会议），"
             "其正文实验尚未逐页核对，已标注。", "",
             "| 工作 | 会议/版本 | 模态 | 同一 RGB 多编码器 | 正常 K-shot | 固定权重 | 共同支持行 | "
             "复制对照 | J/L 干预 | 预算与条件分析 | 核查状态 | 与本研究的差别 |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for w in WORKS:
        lines.append("| " + " | ".join([
            f"[{w['work']}]({w['link']})", f"{w['venue']} / {w['version_checked']}", w["modality"],
            w["same_rgb_multi_encoder"], w["normal_k_shot"], w["fixed_weights"],
            w["shared_support_row"], w["copy_control"], w["JL_intervention"],
            w["budget_condition_analysis"], w["verification_status"], w["difference"]]) + " |")
    lines += ["", "## 核对结论", "",
              "1. 四篇都没有做本研究的问题设定：**同一 RGB 多编码器、固定非负权重、同一正常参考库、"
              "共同选参考行 vs 各自选参考行的受控对照，并在 K 预算上检验其变化**。",
              "2. M3DM 与 arXiv:2412.17297 是 3D 多模态（RGB+点云）融合；CIF 是 5-shot 多模态"
              "记忆库方法；Sea-CLIP 是 CLIP 语义表征的少样本方法。它们与本研究共享动机"
              "（记忆库、少样本、融合），但不共享受控变量。",
              "3. 因此可写的定位是「本工作在检索/匹配这一轴向上补齐了受控对照与预算条件分析」，"
              "**不能**写「首次多分支融合」「首次独立近邻」「无人做过」。",
              "4. 论文投稿前仍需对这些工作做正文级核对（尤其 Sea-CLIP 与各文的分支数/权重设定），"
              "以及扩展检索（如 RGB-only 多编码器融合、joint/independent KNN 的其他领域应用）。", ""]
    (S / "03_paper/literature_difference_verified.md").write_text("\n".join(lines), encoding="utf-8")
    return {"n_works": len(WORKS),
            "statuses": sorted({w["verification_status"] for w in WORKS})}


def claim_map() -> dict:
    rows = [
        {"claim_id": "C1", "claim": "独立选参考优于共同选参考",
         "figure_table": "fig3_kl_curves.png; 主推断表 MAIN_INFERENCE_RECONCILIATION.csv",
         "source": "01_statistics/AGGREGATED_EFFECTS.csv"},
        {"claim_id": "C2", "claim": "复制分支改变权重会变差",
         "figure_table": "fig2_aggregated_effects.png（左）", "source": "01_statistics/AGGREGATED_EFFECTS.csv"},
        {"claim_id": "C3", "claim": "新增视觉表征的收益依赖数据集",
         "figure_table": "fig2_aggregated_effects.png（右）", "source": "01_statistics/AGGREGATED_EFFECTS.csv"},
        {"claim_id": "C4", "claim": "K 无统一规律",
         "figure_table": "fig3_kl_curves.png", "source": "R/p1_statistics/matching_effect_curve.csv"},
        {"claim_id": "C5", "claim": "类别条件与留一类别",
         "figure_table": "fig4_category_conditions.png", "source": "R/p2_conditions/leave_one_category_out.csv"},
        {"claim_id": "C6", "claim": "缺陷面积分组的描述性差异（附录）",
         "figure_table": "附录表", "source": "R/p2_conditions/defect_size_contrasts.csv"},
        {"claim_id": "C7", "claim": "全像素方向（含一处反转反例）",
         "figure_table": "00_audit/STRIDE_SENSITIVITY.csv", "source": "R/p4_fullpixel/stride1_vs_stride8.csv"},
        {"claim_id": "C8", "claim": "BTAD 三类冻结复核",
         "figure_table": "fig3_kl_curves.png（btad 面板）", "source": "R/p3_external/"},
        {"claim_id": "C9", "claim": "与原生 AnomalyDINO/PatchCore 的性能参照",
         "figure_table": "02_baselines/baseline_macro.csv", "source": "02_baselines/"},
        {"claim_id": "C10", "claim": "文献差异",
         "figure_table": "03_paper/literature_difference_verified.md", "source": "03_paper/"},
        {"claim_id": "C11", "claim": "裁剪画布上的归一化对齐与 BTAD-03 掩码口径",
         "figure_table": "附录表 04_recheck/btad03_mask_variants.csv", "source": "00_audit/"},
    ]
    write_csv(S / "03_paper/claim_to_table.csv", rows)
    return {"n_rows": len(rows)}


def draft() -> dict:
    effects = {}
    path = S / "01_statistics/AGGREGATED_EFFECTS.csv"
    with path.open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            if row["metric"] == "pixel_ap":
                effects[(row["dataset"], row["contrast"])] = row

    def cell(dataset, contrast):
        row = effects.get((dataset, contrast))
        if not row:
            return "n/a"
        return (f"{float(row['point_delta_raw']):+.5f} "
                f"[{float(row['ci_low']):+.5f}, {float(row['ci_high']):+.5f}]")

    lines = [
        "# 《少样本工业异常检测中固定多编码器融合的收益与局限》中文草稿（阶段 C）", "",
        f"生成时间：{utcnow()}。所有数字来自本收口包与 R 的机器表；图表对应见 `claim_to_table.csv`。", "",
        "## 题目与摘要（草案）", "",
        "**中文题目**：少样本工业异常检测中固定多编码器融合的收益与局限：权重、参考匹配与支持预算的"
        "受控研究。",
        "**英文题目**：Understanding Fixed Multi-Encoder Fusion for Few-Shot Industrial Anomaly "
        "Detection: Weighting, Reference Matching, and Support Budget。", "",
        "摘要要点（不含任何“首次”主张）：我们在少量正常参考下，用冻结的 DINOv2-B、DINOv2-S 与 "
        "AnomalyCLIP 视觉特征构造固定权重的多编码器记忆库，把「各分支共同选择同一参考行（J）」与"
        "「各分支各自选择参考行（L）」写成同一权重下的两个端点，并加入一个复制已有分支的权重对照。"
        "在 MPDD（六类，development）与 BTAD（三类，已知数据集上的冻结复核）上，"
        "以 K∈{1,2,4,8}、参考 seed∈{0,1,2}/{0,1}、1000 次图像级配对 bootstrap 评估："
        "独立匹配在固定条件下有稳定的平均优势；把同一分支复制后融合会改变有效权重并使性能下降；"
        "真正加入第二个视觉编码器的收益依赖数据集；参考数量没有跨数据集一致的规律。"
        "我们还给出全像素点估计、原生 AnomalyDINO 与 PatchCore 的性能参照，以及一处必须写入正文的"
        "方向反转反例。", "",
        "## 1. 研究问题", "",
        "在少量正常参考下，多编码器融合的收益究竟来自有效权重、真实的新表征，还是参考匹配方式？"
        "这些效应是否随支持预算 K、类别与缺陷条件变化？", "",
        "## 2. 相关工作（要点）", "",
        "- 正常记忆库方法（PatchCore 一类）用单一特征库做最近邻；",
        "- 多模态（RGB+3D）融合方法 M3DM、arXiv:2412.17297 与 CIF 使用多记忆库/结构共性，"
        "但研究对象是模态与架构，不是参考匹配的受控变量；",
        "- Sea-CLIP 一类少样本 CLIP 工作关注语义表征。差异逐项见 "
        "`literature_difference_verified.md`。", "",
        "## 3. 受控协议", "",
        "- 分支：B=DINOv2-B、S=DINOv2-S、C=AnomalyCLIP 视觉特征（检查点含 VisA 训练来源）。",
        "- 构造与权重：A1 B/C=1/2；DUP B/Bcopy/C=1/3（无新表征，B 家族权重升到 2/3）；"
        "TRI B/S/C=1/3；BAL B/S=1/4、C=1/2。",
        "- 端点：J=min_r Σ w_b d_b(q,r)，L=Σ w_b min_r d_b(q,r)，G=J−L≥0；"
        "G 非负是基本代数事实，不是本文定理，G 大也不等于 AP 损失大。",
        "- 共同画布：B/S 保长宽比缩放后左上裁剪到 14 的倍数（MPDD 1024²→448²；BTAD-03 "
        "600×800→448×597→448×588，丢弃右侧 9 px）；C 为方形 518×518 输入得到 37×37 后重网格，"
        "属近似归一化对齐。",
        "- 统计：同一测试集、同一图像复制索引贯穿所有方法/seed/K；K 与 seed 都不独立；"
        "两项预注册主推断用 Bonferroni 调整后的 97.5% 区间，其余为 95% 探索性区间；"
        "实用效应尺度 0.005。", "",
        "## 4. 受控发现", "",
        "### 4.1 权重控制", "",
        f"- MPDD `DUP_J−A1_J`：{cell('mpdd', 'DUP_J - A1_J')}（原始点差、95% 聚合区间）；",
        f"- BTAD `DUP_J−A1_J`：{cell('btad', 'DUP_J - A1_J')}。",
        "即「多一个分支」本身不是收益来源：复制已有分支只改变权重，结果变差。", "",
        "### 4.2 表征替换（相同家族权重）", "",
        f"- MPDD `TRI_J−DUP_J`：{cell('mpdd', 'TRI_J - DUP_J')}；`TRI_L−DUP_L`："
        f"{cell('mpdd', 'TRI_L - DUP_L')}；`BAL_J−A1_J`：{cell('mpdd', 'BAL_J - A1_J')}；"
        f"`BAL_L−A1_L`：{cell('mpdd', 'BAL_L - A1_L')}（四个端点区间均含零）。",
        f"- BTAD `TRI_J−DUP_J`：{cell('btad', 'TRI_J - DUP_J')}；`TRI_L−DUP_L`："
        f"{cell('btad', 'TRI_L - DUP_L')}；`BAL_J−A1_J`：{cell('btad', 'BAL_J - A1_J')}；"
        f"`BAL_L−A1_L`：{cell('btad', 'BAL_L - A1_L')}（四个端点区间均不含零）。",
        "同一操作在两个数据集上结论不同 → 只能写条件性收益；不写「三支总比两支强」，"
        "也不写「三支没有价值」；缺乏显著收益不等于统计等价。", "",
        "### 4.3 匹配效应", "",
        f"- MPDD `A1_L−A1_J`：{cell('mpdd', 'A1_L - A1_J')}；预注册主推断（97.5%）区间 "
        "[+0.003372, +0.009774]；",
        f"- BTAD `A1_L−A1_J`：{cell('btad', 'A1_L - A1_J')}；预注册主推断（97.5%）区间 "
        "[+0.006649, +0.010858]；",
        "- TRI/BAL 两个三支构造的匹配效应更大，DUP 最小；20 个条件的 stride-8 与 stride-1 "
        "点差均为正。", "",
        "## 5. 支持预算与条件效应", "",
        f"- `(A1_L−A1_J)|K8 − (…)|K1`：MPDD +0.002186（97.5% [−0.002674, +0.006907]，含零）；"
        "BTAD −0.002188（[−0.004417, −0.000019]，上界贴近 0）。两个数据集方向不同，"
        "中间 K2/K4 也不单调 → 保留「预算条件下的实证结果」，不宣称规律。",
        "- 类别：逐类与留一类别表见 `fig4_category_conditions.png`；A1 的匹配效应在 MPDD 72 项、"
        "BTAD 24 项留一条件中均未翻转，但规模差异明显。",
        "- 缺陷面积分组只有探索性点估计，且各组类别构成不同，仅作附录描述。", "",
        "## 6. 稳健性与实际语境", "",
        "- 全像素：96 单元 × 13 方法的 stride-1 点估计；180 个对照中 9 个符号相反，"
        "1 个达到实用尺度（MPDD seed1 K8 的 `TRI_J−DUP_J`：stride-8 +0.00126 vs 全像素 −0.00645），"
        "必须作为反例写入；全像素没有配对区间。",
        "- 原生与强基线（K1/K4、seed0/1，两数据集完整）：受控 A1 的宏像素 AP 在两个数据集、两个 K "
        "上均不低于原生 AnomalyDINO 与 PatchCore（后者 128 px + 10% coreset，仅作上下文）。"
        "MPDD 上原生 AnomalyDINO 的像素图与受控 S 分支一致，因此它不是更强的对手。",
        "- BTAD-03 的掩码口径：用管线忠实掩码（保长宽比缩放后裁剪）重算，绝对像素 AP 平均偏低 "
        "0.0067（最大 0.0136），但匹配效应变化 ≤0.0007；绝对水平按该口径加注，结论不变。", "",
        "## 7. 局限", "",
        "- MPDD 为 development；区间只覆盖固定类别、固定支持集合下的测试图像重采样不确定性。",
        "- BTAD 是已知数据集上的冻结复核，不是首次未见验证。",
        "- seed 与 K 不独立；3/2 组支持不足以刻画支持抽样总体。",
        "- C 的预训练含 VisA 训练来源，不能当作完全无工业数据关联的无监督编码器；"
        "本轮也不能回答「加入文本是否有效」。",
        "- 峰值内存与全像素阶段耗时未记录；未做全像素配对区间。", "",
        "## 8. 结论（草案）", "",
        "在少量正常参考下，固定多编码器融合的收益主要来自**参考匹配方式**与**有效权重控制**，"
        "而不是「多一个分支」；新增视觉编码器的收益是条件性的，参考数量没有跨数据集一致的规律。"
        "这些结论支持一篇受控实证分析论文，而不是一个宣称全面领先的新融合模块。", ""]
    (S / "03_paper/draft_CN.md").write_text("\n".join(lines), encoding="utf-8")
    return {"draft": "03_paper/draft_CN.md", "lines": len(lines)}


def main() -> int:
    (S / "03_paper").mkdir(parents=True, exist_ok=True)
    summary = {"created_utc": utcnow(), "literature": literature(), "claim_map": claim_map(),
               "draft": draft()}
    (S / "03_paper/STAGE_C_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
