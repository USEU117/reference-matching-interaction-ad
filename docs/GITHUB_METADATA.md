# GitHub 元数据（供人工复制到 GitHub 网页）

- 日期：2026-09-21（Asia/Shanghai）
- 用途：仓库改名收尾时，把下面各段**逐字复制**到 GitHub 网页对应字段。所有数字与链接均从盘上产物或本机 git 实读，未编造。
- 改名前后对照：远端仓库 `USEU117/sci_project` → `USEU117/reference-matching-interaction`（远端改名由人手动做）。
- 相关脚本：`tools/rename_folder_to_reference_matching_interaction.ps1`（本地物理目录改名，**本文件只给网页与命令行步骤，不执行任何动作**）。

---

## 1. Repository description（About 面板的 Description）

> **≤160 字符。** 下面这条实测 **157 字符**（英文，单句）。

```text
Few-shot industrial anomaly detection: how the normal-reference matching rule interacts with adding a new visual representation branch under frozen encoders.
```

字符数核对（PowerShell，可直接复跑）：

```powershell
$d = 'Few-shot industrial anomaly detection: how the normal-reference matching rule interacts with adding a new visual representation branch under frozen encoders.'
$d.Length   # -> 157
```

---

## 2. Topics（10–15 个，小写连字符；逐条与仓库内容相符）

共 **14** 个：

```text
few-shot-learning
industrial-anomaly-detection
anomaly-detection
anomaly-localization
reference-matching
representation-learning
pytorch
dinov2
anomalyclip
anomalydino
patchcore
bootstrap-statistics
reproducible-research
mvtec-ad
```

依据（各自在仓库里的落点）：

| Topic | 依据 |
|---|---|
| `few-shot-learning` | 支持集为 1/2/4/8 张正常参考图（`data/splits/*/manifest.json`） |
| `industrial-anomaly-detection` | 四个工业数据集 MPDD/BTAD/MVTec AD/VisA + 确认集 KolektorSDD2 |
| `anomaly-detection` / `anomaly-localization` | 图像级检测 + 像素级定位，报告 pixel AUROC 与 pixel AP（`interaction_generalization.csv` 的 `metric` 列） |
| `reference-matching` | 研究对象即"正常参考的匹配方式"（`J` 共用参考行 vs `L` 各自最近行） |
| `representation-learning` | 研究对象即"新增/替换视觉表征分支"的收益（B/S/C/D/E1–E3） |
| `pytorch` | 依赖清单 `requirements_repro.txt`（torch 2.0.0+cu118） |
| `dinov2` | 分支 B = DINOv2-B/14、S = DINOv2-S/14 |
| `anomalyclip` | 分支 C = AnomalyCLIP ViT-L/14@336 |
| `anomalydino` | 外部对比方法之一（`anomalydino_canvas`、`anomalydino_canvas_rotation`） |
| `patchcore` | 外部对比方法之一（`PatchCore_native_local128`、`PatchCore_native_official224`） |
| `bootstrap-statistics` | 主口径为 1000 次自助区间；`n_replicates = 1000` |
| `reproducible-research` | `dist/replication_package_20260920/`（2488 文件，含 `SHA256SUMS`、`SOURCE_COMMIT.txt`）与 `docs/REPRODUCIBILITY_PACKAGE.md` |
| `mvtec-ad` | 四数据集之一（15 类） |

说明：**没有**使用 `sota`、`benchmark`、`state-of-the-art` 等字样——仓库纪律明确"不得声称击败成熟基线"（`docs/HANDOVER_20260919.md` §7.5）。

---

## 3. 网页改名步骤（GitHub 上手动）

1. 打开 **`https://github.com/USEU117/sci_project`** 并登录有权限的账号。
2. 进入 **Settings**（仓库页右上角 `Settings` 标签）。
3. 左侧 **General** 页，找到 **Repository name** 输入框。
4. 把名称改为 **`reference-matching-interaction`**，点 **Rename**。（GitHub 会在弹窗里提示影响范围，确认即可。）
5. **重定向说明**：GitHub 自动为旧地址 `USEU117/sci_project` 建立重定向——旧的网页链接、`git clone`、`git fetch`/`push` 到旧 URL 都会被转到新仓库名。重定向**只在旧名没有被他人占用**时生效；如果之后有人新建了同名 `sci_project` 仓库，重定向会失效。因此**建议尽快把本地与各处引用改成新 URL**（见第 4 节），不要长期依赖重定向。
6. 顺带在 **Settings → General → Social preview** 上传一张预览图（可选，本仓库图源见 `docs/figures_reference_matching_20260914/`）。
7. 网页改名**不会**改动本地磁盘上的任何目录名；本地物理目录的改名是另一件事（见 `tools/rename_folder_to_reference_matching_interaction.ps1`）。

---

## 4. 改完名之后的本地收尾命令（PowerShell，可直接粘贴）

> 路径一律用**新名** `D:\STUDY\My_github\reference-matching-interaction`。当前该路径是指向物理目录 `D:\STUDY\My_github\sci_project` 的 junction，两者是同一份文件，用哪个名字都能跑。

```powershell
# 1) 进入仓库（新名路径）
Set-Location 'D:\STUDY\My_github\reference-matching-interaction'

# 2) 把 origin 指到改名后的远端（旧 URL 会重定向，但显式改成新 URL 更稳）
git remote set-url origin https://github.com/USEU117/reference-matching-interaction.git

# 3) 核对：应打印 fetch/push 两条新 URL
git remote -v

# 4) 拉取远端改名后的引用（远端改名后本地 tracking 分支信息需要刷新）
git fetch --prune origin

# 5) 推送本地 main 与全部 tag（推送前请确认工作区状态：git status --porcelain）
git push origin main --tags
```

要点与注意事项：

- 第 5 步会真正改动远端，**属于作者决定**；执行前先看 `git status --porcelain` 与 `git log --oneline origin/main..main`。
- 如果只是想让本地 remote 显示正确、暂时不推送，执行到第 4 步即可。
- 若远端改名后发现本地 `origin/main` 仍指向旧名，`git fetch --prune origin` 后 `git branch -vv` 应显示新的 tracking 信息。
- **不要**用 `git remote remove + add`（会丢 remote 上的跟踪分支与 tag 关联习惯）；用 `set-url`。
- `dist/replication_package_20260920/`（2488 文件 / 470.7 MB）已被 `.gitignore` 第 73 行的 `dist/` 排除，不会进版本库（`git check-ignore -v dist` 实读：`.gitignore:73:dist/`）。推送前仍建议先跑 `git status --porcelain` 确认待提交内容（见 `docs/ISSUE_REGISTER_20260920.md` R-12 的历史记录）。

---

## 5. 其它网页字段在哪改（提醒）

- **About 面板**：仓库主页右侧 **About** 右侧齿轮 → 可改 **Description**（第 1 节）、**Website**（主页链接）、**Topics**（第 2 节）。同一处还能勾选 **Releases / Packages / Deployments** 等展示开关。
- **Homepage / Website**：同上 About 面板里的 `Website` 字段；若之后有 arXiv/Zenodo 归档，填那里。
- **Social preview 图**：**Settings → General → Social preview**。
- **仓库头像/显示名等组织级字段**：属账号/组织设置，不在单个仓库页。
- 仓库内文档里的链接一律写成**仓库相对路径**（新 README 已如此），因此改名后仓库内链接不需要跟着改。
