# Environment Matrix

Each method uses an isolated environment. **All rows below were re-read on disk
on 2026-09-19** by running `<venv>\Scripts\python.exe` with an import probe and
`-m pip list`; the versions are the *installed* ones, not upstream requirements.
Two earlier claims were wrong and are corrected here: there is **no
`.venv-anomalydino`**, and ReMP-AD / AdaptCLIP are no longer un-started.

## 1. Environments that exist on disk

| Method / purpose | Environment | Python | Installed versions (read) | Local status |
|---|---|---:|---|---|
| AnomalyCLIP + the frozen study pipeline | `.venv-anomalyclip` | 3.10.11 | torch 2.0.0+cu118, torchvision 0.15.1+cu118, CUDA 11.8, numpy 1.26.4, scipy 1.9.1, scikit-learn 1.2.2, faiss-cpu 1.15.0, open_clip_torch 3.3.0, timm 1.0.28, python-docx 1.2.0, matplotlib 3.10.9, pillow 12.2.0, opencv-python-headless 4.8.1.78, scikit-image 0.20.0 | `cuda_available=True`; the interpreter used by nearly every script under `scripts/**` |
| WinCLIP | `.venv-winclip` | 3.10.11 | torch 2.0.0+cu118, torchvision 0.15.1+cu118, CUDA 11.8, open_clip, timm 1.0.28 | `cuda_available=True` |
| PatchCore baseline | `.venv-patchcore` | 3.10.11 | torch 2.0.0+cu118, torchvision 0.15.1+cu118, CUDA 11.8, numpy 1.24.4, faiss-cpu 1.7.4, timm 0.6.13 | `cuda_available=True`; also used for CPU-only evaluation and early DINOv2 feature export |
| PromptAD | `.venv-promptad` | 3.10.11 | torch 2.0.0+cu118, CUDA 11.8, open_clip_torch 3.3.0, timm 1.0.28 | `cuda_available=True` |
| AdaptCLIP | `.venv-adaptclip` | 3.10.11 | torch 2.7.1+cu118, torchvision 0.22.1+cu118, numpy 2.2.6, scipy 1.15.3, scikit-learn 1.7.2, faiss-cpu 1.14.3 | `cuda_available=True` (previously listed as TBD) |
| ReMP-AD | `.venv-remp_ad` | 3.10.11 | torch 2.6.0+cu124, torchvision 0.21.0+cu124, CUDA 12.4, numpy 2.2.6, timm 1.0.28 | `cuda_available=True` (previously listed as TBD; note the **cu124** stack, unlike every other venv) |
| — (duplicate name) | `.venv-rempad` | 3.10.11 | torch 2.0.0+cu118, torchvision 0.15.1+cu118, timm 1.0.28, **no matplotlib** | Exists on disk as a second spelling; treated as a stale duplicate. Do **not** assume it is the one the ReMP-AD runs used |
| AnomalyDINO | **none** | — | — | **There is no `.venv-anomalydino`.** The AnomalyDINO baseline runs under `.venv-anomalyclip` (see `scripts/limitation_closure_20260915/anomalydino_guarded_retry.ps1` line 21). The earlier row claiming a dedicated environment was stale |
| (default `python` on PATH) | — | 3.10.11 | torch 2.12.1+**cpu**, no torchvision, **no CUDA** | Statistics / CPU stages only; **cannot encode** |

No environment has `anomalib` installed, and no script under `scripts/**`
imports it. The PatchCore baseline is the vendored implementation plus FAISS,
not the `anomalib` package.

## 2. Which workflow must use which interpreter

| Workflow | Interpreter | Evidence |
|---|---|---|
| Branch encoding / matrices (B, S, C, D; canonical `k8` caches), E1–E3 extra encoders, generalization (MVTec/VisA), KSDD2 confirmation set, workflow A (BTAD-03 corrected grid), B1/B2 correspondence, C5 interaction table, D-seed variance, figures and statistics scripts | `.venv-anomalyclip` | `scripts/limitation_closure_20260915/{c_encode_generalization,run_matrices,run_analysis,run_d_btad,e_chain_20260918,f_chain_20260918,p0_fixes_20260919,s10_matched_scope_20260919}.ps1` all set `$py = .venv-anomalyclip\Scripts\python.exe`; `night_run_20260917.ps1` / `night_run_2_20260918.ps1` default `-Python` to it |
| AnomalyDINO baseline dumps | `.venv-anomalyclip` | `anomalydino_guarded_retry.ps1` L21 |
| PatchCore baseline | `.venv-patchcore` | e.g. `scripts/audit_submission_repro_package.py` L268, `scripts/build_manuscript_figure_package.py` |
| CPU-only statistics / older figure scripts | `.venv-patchcore` (older v10–v12/v7 scripts) or the default `python` | e.g. `scripts/innovation_v7_global_text/run_phase0_audit.py` documents `.venv-patchcore`; the default `python` is CPU-only torch and is only safe for pure-numpy/scipy/pandas phases |
| WinCLIP / PromptAD / AdaptCLIP / ReMP-AD baselines | their own venv | `.venv-{winclip,promptad,adaptclip,remp_ad}` |

Hard rules (unchanged): encoding must use `.venv-anomalyclip`; the default
`python` silently falls back to CPU and will only produce statistics.

## 3. Reproducing the record

When an environment changes, re-export its own record before using it:

```powershell
python -m pip freeze > outputs/logs/environment/<method>-pip-freeze.txt
python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"
```

For the current study pipeline the package set that matters is the one read from
`.venv-anomalyclip`; a top-level list of the third-party packages actually
imported by `scripts/**` is kept in [`../requirements_repro.txt`](../requirements_repro.txt).

## 4. Known issues

Both items below were re-checked on disk on 2026-09-19 with an import probe.

### 4.1 `.venv-rempad` is a stale duplicate of `.venv-remp_ad`

Two environments with almost the same name exist, and only one of them is used:

| | `.venv-remp_ad` (in use) | `.venv-rempad` (stale) |
|---|---|---|
| Referenced by `scripts/**` | **Yes** — `scripts/start_remp_ad_mvtec.ps1` L9 and `scripts/monitor_baselines.ps1` L31 both hardcode `.venv-remp_ad\Scripts\python.exe` | **No** — no script, config or `.ps1` under `scripts/**` resolves this path (repo-wide text search) |
| torch / CUDA | 2.6.0+cu124, `cuda_available=True` | 2.0.0+cu118, `cuda_available=True` |
| torchvision | 0.21.0+cu124 | 0.15.1+cu118 |
| numpy | 2.2.6 | 1.24.4 |
| matplotlib | installed | **missing** |
| Disk | ≈ 5.16 GB | ≈ 5.30 GB |

Evidence that `.venv-rempad` is the earlier spelling of the same purpose:
`build_progress_report.py` L457 records that "the isolated environment
`.venv-rempad` has been created", and `docs/reproduction_notes.md` L244 records
that `.venv-rempad` then imported torch 2.0.0+cu118 with numpy pinned to 1.24.4
— which is exactly the stack now found on disk. The ReMP-AD audit conclusions
(`docs/remp_ad_adaptclip_audit.md`) were drawn after the cu124 stack was
installed, and the two runner scripts call `.venv-remp_ad`; therefore
**`.venv-remp_ad` is the environment the ReMP-AD runs used, and
`.venv-rempad` is residue that should not be assumed to be it** (the root
`README.md` already says so). Removing the residue would reclaim ≈ 5.3 GB, but
it is not removed here: deletion is an author decision, not a correctness fix.

### 4.2 `psutil` is imported but not installed — optional, not a defect

`import psutil` appears in exactly two scripts, both inside a `try/except` with
a working fallback, and neither path is on the frozen pipeline:

| Script | Line | Behaviour without `psutil` |
|---|---|---|
| `scripts/validation_handoff_20260911/e0_preflight.py` | 46–50 | falls back to `os.sysconf(...)` and then to `None` for total RAM |
| `scripts/validation_handoff_20260911/univad_stage2_eval.py` | 42–45 | falls back to a dependency-free `ctypes`/psapi resident-memory query |

So this is an **optional import, not a defect**: no frozen result depends on it,
and `requirements_repro.txt` deliberately leaves `psutil` commented out. The
only visible consequence is that the E1/E4 cost tables report peak RAM as
"not instrumented", which is recorded honestly rather than filled with zeros
(`experiments/dynamic_fusion/validation_handoff_20260911/E4/DECISION.md` L42).
