# 本地补丁：`methods/anomalydino/src/backbones.py`（vendored 代码，不入版本控制）

## 为什么这里只有说明、没有 diff

`.gitignore:16` 排除了整个 `methods/`，所以 vendored 的 AnomalyDINO 代码不在仓库里，
本次对它的修改**无法用 `git add` 记录**（`git ls-files methods` 只有 2 个历史遗留文件）。
为了让"新克隆的机器也能复现"，把补丁内容与验证方式记在这里。

## 改了什么

`DINOv2Wrapper.load_model()`（原第 84–86 行）由：

```python
    def load_model(self):
        model = torch.hub.load('facebookresearch/dinov2', self.model_name)
```

改为：

```python
    def load_model(self):
        try:
            model = torch.hub.load('facebookresearch/dinov2', self.model_name,
                                   skip_validation=True)
        except TypeError:
            model = torch.hub.load('facebookresearch/dinov2', self.model_name)
```

## 为什么改

`torch.hub.load` 在**复用本地缓存**时仍会向 GitHub API 发一次校验请求
（`_validate_not_a_forked_repo`），该请求**没有超时**。本机到 GitHub 的路径不稳定：
一晚之内它三次表现为**挂死**（进程 CPU 恒为 0，最长一次两小时）、一次表现为
`RemoteDisconnected`（直接报错）。`skip_validation=True` 只跳过这一次 fork 校验，
仍然使用本地缓存的仓库与权重，**加载到的权重完全不变**（`dinov2_vits14`，ViT-S/14，
22.1M 参数，`patch_size=14`）；`except TypeError` 兜住不支持该关键字的旧 torch。

## 怎么验证（实测）

```
.venv-anomalyclip\Scripts\python.exe -c "import time, torch; t=time.time(); \
m=torch.hub.load('facebookresearch/dinov2','dinov2_vits14',skip_validation=True); \
print('%.1f s, patch=%d' % (time.time()-t, m.patch_size))"
```
实测输出：`6.3 s, patch=14` —— 不联网、加载成功。

## 重要订正：补丁并不是当时唯一的失败原因

加上这个补丁之后，VisA 的 dump **仍然失败过两次**。事后查明真正的主因是**并发资源竞争**：
那两次尝试恰好与另一个峰值 5–8 GB 的 CPU 作业（工作流 B 的 BTAD 四变体重跑）重叠。
机器空闲时，**同一条命令 22 分钟就跑完了** visa canvas（48/48），随后 rotation 也 48/48 完成。

另外如实记录一个已发现的缺陷：`scripts/limitation_closure_20260915/anomalydino_guarded_retry.ps1`
用 `Start-Process -PassThru` 的 `TotalProcessorTime` 判断停滞，会把刚启动、尚未累计 CPU 的
进程误读为 0，从而**误杀健康进程**（至少误杀两次）。后续夜里若再用它，应先修这个判据
（例如改用日志 mtime 或增大预热窗口），**不要**把它当成"网络问题"的可靠探测器。

## 复现 visadump 的命令（现在可稳定跑通）

```powershell
.venv-anomalyclip\Scripts\python.exe -u scripts\paper_evidence_closeout_20260914\run_baseline_anomalydino.py `
  --out experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines\anomalydino_mvtec_visa_canvas `
  --frame canvas --suffix _canvas --datasets visa --seeds 0 1 --shots 1 4 `
  --dump-maps experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines\region_maps\anomalydino_canvas
# rotation 变体：--rotation --suffix _canvas_rotation --dump-maps ...\anomalydino_canvas_rotation
```
结果：两个变体各 48/48（btad 12 / mpdd 24 / mvtec 60 / visa 48，两目录各 144）。
