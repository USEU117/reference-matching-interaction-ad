# AnomalyCLIP 检查点来源复核（2026-09-23）

结论：当前使用的两个系列、各 15 个 epoch 的检查点来自项目保留的上游源码归档，30 个文件与归档内成员逐字节 SHA-256 一致，不应写成“本项目自行训练”。核验清单见同名 JSON；不加载 checkpoint 中的 Python 对象。

- 归档：`methods/anomalyclip-main-full.zip`，629,887,164 B。
- SHA-256：`533ed87b6658cdb247d063a249cefea54ab81623cb11683c6f02345b9a6ceafe`。
- 历史获取记录：`docs/reproduction_notes.md`；记录的代码提交为 `3911738c0867544f545a076ad78f3f11d9ecbfdf`。
- VisA 系列 epoch 15：`415c5dcb52668b8c33fb9c1a351c686d632b919df5b384d63fa9ce7a2338ced4`。
- MVTec 系列 epoch 15：`94ce202da3e6486a864b904fdfed5057de75846c5834e446fd1d2fe7f97acb44`。

保留了代码提交、归档哈希、原获取记录和逐文件身份链。原下载 URL 没有完整保留，本轮没有独立重新认证远端下载地址，因此不把本机字节核验写成远端身份认证。连续 epoch 文件的存在不能证明这些文件在本项目训练过。

## 两条使用路径必须分开

1. **受控 A1 的 C 视觉分支**：`scripts/export_anomalyclip_mpdd_features.py` 先从基础 CLIP 加载视觉编码器，再把检查点加载到独立的 `prompt_learner`。实际特征导出调用 `model.encode_image`，不调用 prompt learner，检查点也未被加载到视觉模型。因此这些 prompt 权重不改变 C 路径的视觉描述子。DPAM 替换属于保留的上游视觉路径。VisA 的 in-domain 标签按历史方案保守保留；它不是“prompt 学习已改变视觉特征”的证据。
2. **扩展表 AnomalyCLIP 零样本方法**：使用学习后的 prompt 生成文本特征，与视觉特征计算异常分数；对 MVTec 使用 VisA 训练的 prompt，对其余三个数据集使用 MVTec 训练的 prompt。目标域不再做梯度训练，不能说整个模型从未训练。

历史 `05_baselines_ext_20260921/PREFLIGHT.json` 中的重训疑问原样保留，用本文与核验 JSON 追加结案，不回写冻结证据。运行器的旧注释已更正；未改模型实现、预测、指标或实验数据。
