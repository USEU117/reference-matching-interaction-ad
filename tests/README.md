# 测试入口说明（正式范围）

> 最后刷新：2026-09-20（Asia/Shanghai）
> 背景与本轮审计编号：`docs/ISSUE_REGISTER_20260920.md` R-05 / R-06；计划见 `docs/REMEDIATION_PLAN_20260920.md` P0-4 / P2-2。

## 1. 正式命令

仓库根新增 `pytest.ini`，把正式范围固化下来，因此以下两条命令等价：

```powershell
.\.venv-patchcore\Scripts\python.exe -m pytest tests -q      # 显式传 tests
.\.venv-patchcore\Scripts\python.exe -m pytest -q            # 走 testpaths
```

`.venv-anomalyclip` 同样可跑（结果相同）。

## 2. 正式范围与其实测结果

| 项 | 值 |
|---|---|
| 配置 | 仓库根 `pytest.ini`：`testpaths = tests`；`addopts = --ignore=tests/innovation_v6_dgsafe/test_wave2a_probes.py` |
| 范围 | `tests/` 递归，**唯一排除** `tests/innovation_v6_dgsafe/test_wave2a_probes.py` |
| 实测（2026-09-20，`.venv-patchcore`） | **260 passed, 0 failed, 0 errors**（约 25–41 s） |
| 实测（2026-09-20，`.venv-anomalyclip`） | **260 passed**（约 31–45 s） |
| 退出码 | 0 |

注意：**260 是当前实测值，不是历史值**。历史记录里的 81 / 122 / 123 / 141 来自不同日期或不同的 `tests/` 内容，不能当作当前 HEAD 的结论（原委见 `experiments/dynamic_fusion/validation_handoff_20260911/E8/test_scope_record.json`）。

不要并发跑两份 pytest：本机内存有限（约 16 GB，空闲常在 4–5 GB），并发会让 `tests/test_rcec.py` 的两个大数组用例报 `numpy ... Unable to allocate ...`。串行跑即通过。

## 3. 被排除的部分：原因与状态

**文件**：`tests/innovation_v6_dgsafe/test_wave2a_probes.py`

**原因（实测复现）**

1. 该用例在 import 期用 `importlib.util.spec_from_file_location` + `exec_module` 直接执行 `scripts/innovation_v6_dgsafe/run_wave2a_build_reliability.py`。
2. 该脚本第 59 行把 `methods/SubspaceAD` 插到 `sys.path`，随后第 64–68 行 `from src.subspacead...`。
3. vendored 源码**确实存在**于 `methods/SubspaceAD/src/subspacead/`，但 `src/`（仓库根）与 `methods/SubspaceAD/src/` 都是 **PEP 420 命名空间包**（两处都没有 `__init__.py`）。递归收集时，顶层 `sys.modules['src']` 已被仓库根 `src/` 占用，之后再插 `methods/SubspaceAD` 已无法让 `src.subspacead` 解析，于是报：

   ```
   E   ModuleNotFoundError: No module named 'src.subspacead'
   ```

   这是**导入路径/命名空间遮蔽**问题，不是依赖缺失。
4. 另有环境门：该脚本 import 期需要第三方 `transformers`。`.venv-anomalyclip` 有（4.48.0），`.venv-patchcore` 没有。

**状态**

| 环境 | 现状 |
|---|---|
| `.venv-patchcore` | collection 失败（`src.subspacead`） |
| `.venv-anomalyclip` | 单独调用该文件可 6 passed（本机实测），但**在整个 `tests/` 递归运行中仍因上述命名空间遮蔽而 collection 失败** |

**其它 7 个用例不受影响**：同目录的 `tests/innovation_v6_dgsafe/test_maps.py`（7 passed）已在正式范围内，**未被排除** —— 这也是与 2026-09-12 那份 E8 记录（当时 `--ignore=tests/innovation_v6_dgsafe`，253 passed）的差别：本轮只排除单个文件，因此多收回 7 个。

**修法（未执行，留待 P2-2）**：把 `run_wave2a_build_reliability.py:64-68` 的 `src.subspacead` 改成现行包结构（或改由 `scripts/innovation_v6_dgsafe/` 侧显式加载 vendored 包），并确认解释器装有 `transformers`；修好后应删掉 `pytest.ini` 里的 `--ignore` 并重新记录 N passed。**本轮未改动该实验脚本**（属冻结探针脚本，改 import 可能影响 Wave 0–3 的复现链，需单独授权）。

## 4. 复现性说明

- `--ignore` 的路径按**调用目录**解析，因此请从仓库根运行（上面两条命令即是）。
- 仓库内不存在第二套 pytest 配置（无 `pyproject.toml` / `setup.cfg` / `tox.ini` / 根 `conftest.py`）；`tests/innovation_v10_portfolio/conftest.py` 是该子目录自己的夹具，不受影响。
