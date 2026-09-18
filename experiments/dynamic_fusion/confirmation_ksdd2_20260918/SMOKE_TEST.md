# KSDD2 接入烟测（2026-09-18）

- 解释器：`python` 3.10.11（`cv2` 4.12.0），工作目录 `d:\STUDY\My_github\sci_project`（PowerShell）
- 范围：只做“加载图 + 加载掩码 + 缩放 + 掩码二值化 + 清单/计数”，**不跑编码器、不产出任何 KSDD2 特征文件**
- 契约：`experiments/dynamic_fusion/confirmation_ksdd2_20260918/F_SPEC.json`
  （`frozen_utc = 2026-09-18T11:59:44.573532+00:00`，`frozen_before_any_feature = true`；本次烟测不写入任何特征文件，因此不违反该冻结）

---

## 1. 形状/几何（2 张正样本 + 1 张负样本）

命令（原文，PowerShell 下执行）：

```powershell
python -c "
import sys,json,cv2,numpy as np
sys.path.insert(0,'scripts'); sys.path.insert(0,'scripts/unified_fusion_paper_support_v1')
import export_k8_cache as E
root=E.DATA_ROOT['ksdd2']
samples=E.index_ksdd2(root)['ksdd2']
print('test_samples',len(samples),'pos',sum(s.label for s in samples))
pick=[s for s in samples if s.label==1][:2]+[s for s in samples if s.label==0][:1]
for s in pick:
    img=E.read_absolute(s.image_path)
    canvas=E.ksdd2_to_canvas(img)
    raw=cv2.imread(str(s.mask_path),cv2.IMREAD_GRAYSCALE)
    m=(cv2.resize(raw,(E.KSDD2_CANVAS_WH[0],E.KSDD2_CANVAS_WH[1]),interpolation=cv2.INTER_NEAREST)>0).astype(np.uint8)
    h,w=canvas.shape[:2]
    print(json.dumps({'sample':s.sample_id,'native_wh':[img.shape[1],img.shape[0]],'canvas_hw':[h,w],'canvas_wh':[w,h],'grid_hw':[h//E.KSDD2_PATCH,w//E.KSDD2_PATCH],'grid_wh_spec':[w//E.KSDD2_PATCH,h//E.KSDD2_PATCH],'smaller_edge':min(h,w),'encoder_resolution':E.KSDD2_ENCODER_RESOLUTION,'mask_shape':list(m.shape),'mask_values':sorted(np.unique(m).tolist()),'mask_pos_pixels':int(m.sum()),'label':s.label}))
"
```

输出：

```
test_samples 1004 pos 110
{"sample": "test/20042.png", "native_wh": [227, 624], "canvas_hw": [630, 224], "canvas_wh": [224, 630], "grid_hw": [45, 16], "grid_wh_spec": [16, 45], "smaller_edge": 224, "encoder_resolution": 224, "mask_shape": [630, 224], "mask_values": [0, 1], "mask_pos_pixels": 5543, "label": 1}
{"sample": "test/20056.png", "native_wh": [230, 648], "canvas_hw": [630, 224], "canvas_wh": [224, 630], "grid_hw": [45, 16], "grid_wh_spec": [16, 45], "smaller_edge": 224, "encoder_resolution": 224, "mask_shape": [630, 224], "mask_values": [0, 1], "mask_pos_pixels": 1519, "label": 1}
{"sample": "test/20000.png", "native_wh": [231, 636], "canvas_hw": [630, 224], "canvas_wh": [224, 630], "grid_hw": [45, 16], "grid_wh_spec": [16, 45], "smaller_edge": 224, "encoder_resolution": 224, "mask_shape": [630, 224], "mask_values": [0], "mask_pos_pixels": 0, "label": 0}
```

结论①：画布 = 224 × 630（宽 × 高），`grid_wh_spec = [16, 45]`，patch = 14（224/14=16，630/14=45）；画布较小边 = 224 = `KSDD2_ENCODER_RESOLUTION`，即 DINO 包装器的 `Resize(224)` 是空操作，编码网格必然是 16×45。掩码落在同一画布上，取值只有 {0,1}（最近邻 + `>0` 二值化），正样本掩码非空、负样本掩码全零。

---

## 2. 排除 `(copy)` 冗余副本 + 计数

命令：

```powershell
python -c "
import sys,json,time
sys.path.insert(0,'scripts'); sys.path.insert(0,'scripts/unified_fusion_paper_support_v1')
import export_k8_cache as E, build_support_manifest as B
root=E.DATA_ROOT['ksdd2']
t0=time.perf_counter()
train=E.ksdd2_images(root/'train'); test=E.ksdd2_images(root/'test')
raw_png=sorted((root/'train').glob('*.png'))
naive=[p.name for p in raw_png if not p.name.endswith('_GT.png')]
gt=[p.name for p in raw_png if p.name.endswith('_GT.png')]
excluded=E.KSDD2_EXCLUDED_FILES
print(json.dumps({'train_dir_files':len(raw_png),'naive_image_scan_train':len(naive),'suffix_gt_scan_train':len(gt),'pipeline_train_images':len(train),'pipeline_test_images':len(test)},indent=0))
print('copy_still_in_raw_dir',[n for n in ('10301 (copy).png','10301_GT (copy).png') if (root/'train'/n).is_file()])
print('copy_names_in_pipeline_lists',[n for n in ('10301 (copy).png','10301_GT (copy).png') if n in {p.name for p in train+test}])
print('excluded_constant',excluded)
print('pipeline_keeps_original_10301',[p.name for p in train if p.name.startswith('10301')][:6])
man=B.build_ksdd2([1,2,4,8],[0,1,2])
print('observed_counts',json.dumps(man['observed_counts']),'match_official',man['counts_match_official'],'query_n',man['query_counts'])
print('n_normal_candidates',man['n_normal_candidates'],'K1/2/4/8 seed0',[man['categories']['ksdd2']['0'][str(k)] for k in (1,2,4,8)][:1])
print('elapsed_s',round(time.perf_counter()-t0,2))
"
```

输出：

```
{
"train_dir_files": 4664,
"naive_image_scan_train": 2333,
"suffix_gt_scan_train": 2331,
"pipeline_train_images": 2331,
"pipeline_test_images": 1004
}
copy_still_in_raw_dir ['10301 (copy).png', '10301_GT (copy).png']
copy_names_in_pipeline_lists []
excluded_constant ('train/10301 (copy).png', 'train/10301_GT (copy).png')
pipeline_keeps_original_10301 ['10301.png']
observed_counts {"train": {"pos": 246, "neg": 2085}, "test": {"pos": 110, "neg": 894}} match_official True query_n {'n': 1004, 'pos': 110, 'neg': 894}
n_normal_candidates 2085 K1/2/4/8 seed0 [['train/10664.png']]
elapsed_s 4.26
```

结论②：`train/` 下 4664 个文件里，按后缀扫“非 `_GT.png`”会得到 **2333** 张“图”（把 `10301_GT (copy).png` 也算成图）而 GT 只有 2331 个；管线的 `ksdd2_images()` 得到 **2331** 张图，两个 `(copy)` 文件名都不出现在任何清单里，而原始 `10301.png` 仍保留。

结论③：正负计数与官方逐项一致 —— train 246 正 / 2085 负，test 110 正 / 894 负；查询集 1004 张（110 正 / 894 负）；参考候选 = 2085 张掩码为空的训练图。全部 3335 次掩码判定耗时 4.26 s。

---

## 3. 追加式集成的不回归检查

命令：

```powershell
python -c "
import sys; sys.path.insert(0,'scripts'); sys.path.insert(0,'scripts/unified_fusion_paper_support_v1')
import export_k8_cache as E, build_support_manifest as B, run_matrix as M, run_fullpixel as F, stats_v2 as S
print('DATA_ROOT', {k: str(v).split('sci_project')[-1] for k,v in E.DATA_ROOT.items()})
print('ROLE', E.ROLE)
print('hist mpdd B s0', E.hist_dir('mpdd','B',0))
print('hist mpdd S s0', E.hist_dir('mpdd','S',0))
print('hist visa C s1', E.hist_dir('visa','C',1))
print('hist ksdd2 B s0', E.hist_dir('ksdd2','B',0))
print('CATS run_matrix', list(M.CATS), M.CATS['ksdd2'], '| fullpixel', list(F.CATS))
print('stats CATS/DATASET_ID', list(S.CATS), S.DATASET_ID, S.METRIC_KEYS)
for d in ('mpdd','btad'):
    p = B.build(d, [1,2,4,8], [0,1,2])
    print(d, 'prefix_checks', p['n_prefix_checks'], 'all_match', p['prefix_invariance_all_match'])
"
```

输出（关键行）：

```
DATA_ROOT {'mpdd': '\\data\\mpdd_raw\\MPDD', 'btad': '\\data\\btad_raw\\BTech_Dataset_transformed', 'mvtec': '\\data\\mvtec', 'visa': '\\data\\visa_raw', 'ksdd2': '\\data\\kolektorsdd2_raw'}
ROLE {'mpdd': 'development', 'btad': 'holdout', 'mvtec': 'external_frozen_validation', 'visa': 'in_domain_frozen_validation', 'ksdd2': 'confirmation'}
hist mpdd B s0 D:\STUDY\My_github\sci_project\outputs\dynamic_fusion\v3_direction_a\features_vitb14_s0_k4\anomalydino_visual
hist mpdd S s0 D:\STUDY\My_github\sci_project\outputs\validation_handoff_20260911\DINO_S\s0_k4
hist visa C s1 D:\STUDY\My_github\sci_project\outputs\dynamic_fusion\v3_direction_a\visa_features\s1_k4\anomalyclip_text
hist ksdd2 B s0 None
CATS run_matrix ['mpdd', 'btad', 'mvtec', 'visa', 'ksdd2'] ['ksdd2'] | fullpixel ['mpdd', 'btad', 'mvtec', 'visa', 'ksdd2']
stats CATS/DATASET_ID ['mpdd', 'btad', 'mvtec', 'visa', 'ksdd2'] {'mpdd': 1, 'btad': 2, 'mvtec': 3, 'visa': 4, 'ksdd2': 5} ('pixel_ap', 'pixel_auroc', 'image_ap', 'image_auroc')
mpdd prefix_checks 54 all_match True
btad prefix_checks 27 all_match True
```

- 4 个既有数据集的 DATA_ROOT / ROLE / 历史缓存路径逐字不变；`hist_dir('ksdd2', ...)` 返回 `None`（无历史缓存 → 全量新编码）。
- `build_support_manifest.build()` 对 mpdd（54 项）与 btad（27 项）重建的 K=1/2/4 前缀仍与历史清单逐项一致（`all_match True`），说明新增分支没有改变既有数据集的行为。
- `engine_v2` 单独导入检查：`DATASETS ('mpdd','btad','mvtec','visa','ksdd2')`，`KNOWN_BRANCHES ('B','S','C')`，`MAP_STRIDE 14`，`branch_dir('S','ksdd2',0)` = `<canonical>/S/ksdd2_s0_k8`（`FUSION_CANONICAL_ROOT` 环境变量优先逻辑未改动）。

## 4. 语法检查

```powershell
python -m py_compile scripts/unified_fusion_paper_support_v1/export_k8_cache.py scripts/unified_fusion_paper_support_v1/engine_v2.py scripts/unified_fusion_paper_support_v1/run_matrix.py scripts/unified_fusion_paper_support_v1/stats_v2.py scripts/unified_fusion_paper_support_v1/run_fullpixel.py scripts/unified_fusion_paper_support_v1/build_support_manifest.py
```

输出：`exit=0`（6 个文件全部通过）。

## 未在本次烟测中覆盖的内容

- 没有实例化 DINO/CLIP 编码器，也没有写出任何 `.npz`：编码网格 16×45 是通过“画布较小边 = `KSDD2_ENCODER_RESOLUTION` = 224，且两条边都是 14 的整数倍”这一不变量推断的（`methods/anomalydino/src/backbones.py:104-108` 的裁剪/网格算术），不是从真实编码结果读出的。
- 没有跑 `export_k8_cache.py` / `run_matrix.py` / `stats_v2.py` 的端到端矩阵（需要 GPU 与长时间预算），也没有生成 KSDD2 的支撑清单文件。

---

# 第 2 轮（2026-09-18，本轮）：D 分支编码 + 交互管线脚本的 ksdd2 支持

本轮**首次真实编码了 KSDD2 特征**（D 分支 = WideResNet50-2，3 张测试图），因此上面那节“没有写出任何 `.npz`”的声明只适用于第 1 轮。
全部烟测产物落在 **`_smoke_round2/`**（下划线前缀 = 临时/夹具目录，不属于任何 F 清单，也不属于正式结果目录）；正式 F 运行的 canonical/特征目录另建。

- 解释器（本轮编码必须用它，默认 python 没有 torchvision）：
  `.venv-anomalyclip\Scripts\python.exe` → Python 3.10.11、torch 2.0.0+cu118、torchvision 0.15.1+cu118、cv2 4.8.1、numpy 1.26.4
- 权重：`C:\Users\lynle\.cache\torch\hub\checkpoints\wide_resnet50_2-95faca4d.pth`（138 223 492 B，与 `D_BRANCH_SPEC.json` 的 sha256 一致）
- 本轮改动的脚本（详见文末清单）：`s3_new_encoder.py`（D 分支）、`s1_interaction.py`、`s2_robustness.py`、`analyze_conditions.py`、`c5_generalization_interactions.py`

---

## 5. 烟测 A：D 分支编码 + 形状断言 + 最小交互（19 个断言全过）

命令（PowerShell，cwd = 项目根）：

```powershell
.venv-anomalyclip\Scripts\python.exe -u experiments/dynamic_fusion/confirmation_ksdd2_20260918/_smoke_round2/smoke_d_branch.py
```

该脚本（`_smoke_round2/smoke_d_branch.py`）把 `FUSION_CANONICAL_ROOT` 指向它自己的 `_smoke_round2/canonical`，然后调用**真实代码路径**：`s3_new_encoder.EncoderD` → `build_features` → `score_branches` → `assemble_maps`。
B/C 两支的特征块是 3 图**夹具**（随机、逐位置单位化，npz 内带 `smoke_fixture=True` 标记；真实 canonical 需要 DINO/CLIP 编码器与 1004 图全量遍历）；**D 支是真实编码**。

原始输出（19 行 gate，末行 `ALL_GATES_PASS True`，exit=0）：

```
[gate] s3_data_root_ksdd2: PASS :: "D:\\STUDY\\My_github\\sci_project\\data\\kolektorsdd2_raw"
[gate] canonical_root_from_env: PASS :: "...\\confirmation_ksdd2_20260918\\_smoke_round2\\canonical"
[gate] s3_geometry_constants: PASS :: {"canvas_wh": [224, 630], "grid_hw": [45, 16], "patch": 14, "mpdd_btad_smaller_edge": 448, "cats": ["ksdd2"], "dataset_id": 5, "default_datasets": ["mpdd", "btad"]}
[gate] counts_train_246_2085: PASS :: {"pos": 246, "neg": 2085}
[gate] counts_test_110_894: PASS :: {"pos": 110, "neg": 894}
[gate] counts_match_official: PASS :: true
[gate] index_sizes_2331_1004: PASS :: [2331, 1004]
[gate] copy_files_in_no_list: PASS :: {"leaks": [], "copy_present_on_disk": ["10301 (copy).png", "10301_GT (copy).png"], "original_kept_in_index": true}
[gate] masks_shape_N_630_224: PASS :: [1004, 630, 224]
[gate] masks_binary_uint8: PASS :: {"dtype": "uint8", "values": [0, 1], "positive_masks": 110}
[gate] smoke_sample_masks_3_630_224: PASS :: {"sample_ids": ["test/20042.png", "test/20056.png", "test/20000.png"], "labels": [1, 1, 0], "shape": [3, 630, 224]}
[gate] ksdd2_canvas_630_224: PASS :: [630, 224, 3]
[gate] patch_features_N_45_16_1536: PASS :: {"query_shape": [3, 45, 16, 1536], "ref_shape": [8, 45, 16, 1536], "dtype": "float16", "encode_s": 6.79}
[gate] ref_patch_features_8_45_16_1536: PASS :: [8, 45, 16, 1536]
[gate] query_rows_are_unit_length: PASS :: "L2 per position, max|norm-1|=6.068e-05"
[gate] all_maps_N_45_16: PASS :: {"n_methods": 11, "shapes": [[3, 45, 16]]}
[gate] G_J_minus_L_non_negative: PASS :: {"min(G)_A1": 0.0, "min(G)_DUP": 0.0, "min(G)_TRI_D": 0.011010349, "min(G)_BAL_D": 0.009383261}
[gate] construction_arithmetic_exact: PASS :: {"A1_L": 0.0, "DUP_L": 0.0, "TRI_D_L": 0.0, "BAL_D_L": 0.0, "D_single": 0.0}
[gate] interaction_expression_finite: PASS :: {"I_TRI_D_placeholder": -0.015148, "note": "synthetic B/C, one reference: a wiring value, NOT a KSDD2 result"}
[smoke] ALL_GATES_PASS True
```

结构化结果另存 `_smoke_round2/SMOKE_RESULTS.json`（`gates` / `facts` / `all_gates_pass`）。

### 5.1 三条指定断言的结论

| 断言 | 结果 | 证据 |
|---|---|---|
| `patch_features` 形状 = `(N, 45, 16, 1536)`、掩码 = `(N, 630, 224)` | **通过** | query `[3, 45, 16, 1536]`（float16）、ref `[8, 45, 16, 1536]`；`masks_on_canvas('ksdd2','ksdd2',(45,16))` = `[1004, 630, 224]` uint8、取值 ⊂ {0,1}、正样本掩码 110 张 |
| 两个 `(copy)` 文件不出现在任何清单 | **通过** | 参考集 ∪ 查询集（含掩码）里 `leaks = []`；两个副本仍留在磁盘上（`train/10301 (copy).png`、`train/10301_GT (copy).png`），而 `10301.png` 仍在索引里 |
| train 246/2085、test 110/894 | **通过** | `build_ksdd2` 的 `observed_counts` 逐项相等且 `counts_match_official = true`；索引规模 2331 图 / 1004 图 |

补充：编码画布 = `[630, 224, 3]`（= grid 45×16 × patch 14），且 D 的输出逐位置 L2（`max|norm−1| = 6.1e-05`，来自 float16 往返）。
最小交互计算里还核对了引擎的代数不变量：`G = J − L ≥ 0`（四种构造全部 ≥ 0，见上），以及 L 图的加权和逐位相等（`max|Δ| = 0.0`）。

> 注意一处**我自己写反了的断言**：最初把不变量写成 `J ≤ L`，烟测直接报 FAIL（差 0.089）。引擎（`engine_v2.py:16-19`）的定义是 `J = min_r Σ w·d`、`L = Σ w·min_r d`，因此恒有 **`G = J − L ≥ 0`**；改为这一方向后通过。这是断言写错、不是代码 bug。

---

## 6. 烟测 B：`s3_new_encoder.py --smoke --datasets ksdd2` 全流程单单元

命令：

```powershell
$env:FUSION_CANONICAL_ROOT='D:\STUDY\My_github\sci_project\experiments\dynamic_fusion\confirmation_ksdd2_20260918\_smoke_round2\canonical'
.venv-anomalyclip\Scripts\python.exe -u scripts/representation_matching_interaction_20260914/s3_new_encoder.py `
  --datasets ksdd2 --smoke --device cpu `
  --out experiments/dynamic_fusion/confirmation_ksdd2_20260918/_smoke_round2/out_run `
  --support-dir experiments/dynamic_fusion/confirmation_ksdd2_20260918/_smoke_round2/p0_support
```

原始输出：

```
[S3] D features ksdd2/ksdd2/s0: query 4.65s, refs 5.62s
[S3] scored ksdd2/ksdd2/s0/k1/study: load 0.6s score 0.3s
[S3] smoke run finished; full scope not executed
exit=0
```

产物（`_smoke_round2/out_run/`）：

- `unit_status.csv`：`ksdd2,ksdd2,0,1,study,completed,5,4,0.61,0.31,B=799968bd…;C=91dec14f…;D=f7595218…`
  （5 个新 D 条件 + 4 个对照；三个源文件摘要）
- `units/ksdd2_s0_k1/ksdd2__study/`：`evaluation_scores.npz`（`pixel_scores (9, 3, 79, 28)`、`pixel_masks (3, 79, 28)`、`grid [45, 16]`、`stride 8`）、`patch_scores.npz`、`metrics.csv`、`per_image.csv`、`flip_stats.csv`、`region_stats.csv`、`sample_pairs.npz`
- `feature_manifest.csv`：`ksdd2,ksdd2,0,"[45, 16]",3,8,…,True,True,4.65,5.62,"[3, 45, 16, 1536]","[8, 45, 16, 1536]",False`
- `D_BRANCH_SPEC.json`：本跑新增的 `confirmation_set_extension` 生效 ——
  `scope = {"datasets": ["ksdd2"], "categories": {"ksdd2": ["ksdd2"]}, "seeds": [0], "shots": [1], "units": 1, "new_method_conditions": 5, …}`，
  `confirmation_set_extension = {"note": "…the frozen 2026-09-14 scope and does not apply to them", "datasets": ["ksdd2"]}`。
  说明：**已存在的 `D_BRANCH_SPEC.json` 不会被覆盖**（本轮加的守卫），因此历史 `04_new_encoder/D_BRANCH_SPEC.json` 仍是 2026-09-14 冻结内容。

**必须声明的标签接触**：`--smoke` 会跑 `diagnostics_v2.evaluate_case`，于是这个 3 图单元里出现了 `pixel_ap` 等数字（例如 `D 0.8605`）。
这些数字是在**合成 B/C 特征**上得到的、只覆盖 3 张测试图，**不是结果、不得进任何表**；但严格说这 3 张图的标签被碰过一次。
本轮 F 的冻结口径（F_SPEC 的 `one_shot_rule`）针对的是“最终数字只算一次、事后不得回头调整”，此处既无选择依赖、也无口径改动；
若要保持“零标签接触”的记录，可删掉 `_smoke_round2/out_run/units/` 只留日志与特征（不影响 5.1 的三条断言，那三条不依赖任何度量）。

收尾复跑（本轮所有编辑完成后的最终状态）：
`smoke_d_branch.py` → `ALL_GATES_PASS True`、无 FAIL 行、exit=0；上面第 6 节那条命令 → `[S3] D features ksdd2/ksdd2/s0: query 0.97s, refs 2.42s` / `[S3] scored ksdd2/ksdd2/s0/k1/study: load 0.4s score 0.1s` / `exit=0`，写出的 `D_BRANCH_SPEC.json` 仍是 `scope.datasets = ["ksdd2"]`、`units = 1`。

---

## 7. 本轮**没有**覆盖的内容（第 3 轮或正式运行补）

- B/S/C 三支的 canonical（`export_k8_cache.py`）与 `run_matrix.py` / `run_fullpixel.py` / `stats_v2.py` 的 KSDD2 端到端（GPU、小时级），所以 `s1_interaction.py` / `s2_robustness.py` / `analyze_conditions.py` 的 ksdd2 分支只做了**静态注册 + 语法/导入检查**，没有真实数据流过。
- `s3_new_encoder.py` 的真实统计阶段（`collect_replicates` / 1000 次自助 / `--workers`）没有跑。
- `verify_replay_and_nesting.py` / `finalize_study.py` / `recompute_inferences.py` / `render_paper.py`（报告阶段）**本轮未改**，仍硬编码 CATS/DATASETS，原因与改法见下面的“报告阶段”一节。

---

## 8. 本轮改动清单（全部为纯追加；既有数据集行为不变）

| 文件 | 改了什么 | 关键位置 |
|---|---|---|
| `scripts/representation_matching_interaction_20260914/s3_new_encoder.py` | D 分支支持 ksdd2 | `import os` + `CANONICAL` 读 `FUSION_CANONICAL_ROOT`（第 51-59 行）；`KSDD2*` 几何常量 + `DATA_ROOT`/`CATS`/`DATASET_ID` + `DEFAULT_DATASETS`（第 66-95 行）；`write_spec(out, datasets, seeds, shots)` + `confirmation_set_extension`（第 154-244 行）；`EncoderD.__init__(device, dataset)` + KSDD2 固定画布分支（第 256-289 行）；`build_features(..., support_dir)` + 网格守卫（第 339-361 行）；`run()` 的 `--datasets/--seeds/--shots`、spec 不覆盖守卫、KSDD2 专用编码器（第 682-712 行）；`revisions` 只走 study（第 768-770、850-852、870-872 行）；统计阶段改用本次 seeds/shots（第 848-849、871 行）；`--study-statistics`（第 971-975、1062-1096 行） |
| `scripts/representation_matching_interaction_20260914/s1_interaction.py` | 02_interaction 支持 ksdd2 | `SEEDS["ksdd2"] = [0,1,2]` + `DATASETS`（第 45-52 行）；`load_inputs(study_root)`（第 88-96 行）；`main` 新增 `--study-root`（第 218-231 行） |
| `scripts/representation_matching_interaction_20260914/s2_robustness.py` | 03_robustness 支持 ksdd2 | `import os`（第 29 行）；`CATS`/`SEEDS` 追加 ksdd2 + `MATRIX_DIR` + `DATASETS`（第 48-60 行）；`--study-root`/`--interaction-root`（第 184-188 行）；`revisions["ksdd2"]`（第 219 行）；8 处数据集循环改用 `DATASETS`；图件茎改随 `--output`（第 204、477 行）；S1 表格改从 `--interaction-root` 读（第 352-361 行）；两处矩阵根改 `MATRIX_DIR[dataset]`（第 497、601 行）；`render_cases` 读 `FUSION_CANONICAL_ROOT` + ksdd2 图像根（第 586-594 行） |
| `scripts/unified_fusion_paper_support_v1/analyze_conditions.py` | 条件表支持 ksdd2 | `import os` + `CANONICAL` 读 `FUSION_CANONICAL_ROOT`（第 22-34 行）；`CATS["ksdd2"]`（第 43-49 行） |
| `scripts/limitation_closure_20260915/c5_generalization_interactions.py` | C5 表登记 ksdd2 | `CATS["ksdd2"]`（第 47-53 行）、`ROLE["ksdd2"] = "confirmation"`（第 56-60 行）；`PRIMARY_SCOPE` 刻意不变（CI 家族冻结） |
| `experiments/.../confirmation_ksdd2_20260918/_smoke_round2/smoke_d_branch.py` | 新增：本轮烟测夹具 + 19 条断言 | 全文 |
| `experiments/.../confirmation_ksdd2_20260918/F_SPEC.json` | 追加 `post_freeze_amendments`（不动 `frozen_utc` 与既有字段） | 见该文件 |

语法检查（5 个 .py 全部通过）：

```powershell
python -m py_compile scripts/representation_matching_interaction_20260914/s3_new_encoder.py scripts/representation_matching_interaction_20260914/s1_interaction.py scripts/representation_matching_interaction_20260914/s2_robustness.py scripts/unified_fusion_paper_support_v1/analyze_conditions.py scripts/limitation_closure_20260915/c5_generalization_interactions.py
```

## 9. 报告阶段（`verify_replay_and_nesting.py` / `finalize_study.py` / `recompute_inferences.py` / `render_paper.py`）：本轮**故意不改**

这 4 个脚本不是“产出 S/D/C 三支特征与结果”的链上脚本，而且它们的 `CATS` 是**无条件遍历**（例如 `verify_replay_and_nesting.py:65` 的 `for dataset, cats in CATS.items()`），加入 `ksdd2` 会让**既有（非 F）报告运行**去找并不存在的 KSDD2 单元而报错。
因此本轮不动它们；正式 F 收尾时若要这些报告覆盖 KSDD2，需要**带开关**地追加（例如 `--datasets` 参数 + 默认保持 mpdd/btad），这不是纯追加能解决的。


