# 数据目录

数据文件不提交 Git。

## MVTec AD

- 官方页面：<https://www.mvtec.com/research-teaching/datasets/mvtec-ad>
- 许可：CC BY-NC-SA 4.0，非商业使用。
- 目标目录：`data/mvtec_ad/`

官方页面要求填写表单后下载。下载完成后保留原压缩包校验和，并核验 15 个类别及像素掩码。

## VisA

- 官方登记页：<https://registry.opendata.aws/visa/>
- 官方项目：<https://github.com/amazon-research/spot-diff>
- 许可：CC BY 4.0。
- AWS 对象：`s3://amazon-visual-anomaly/VisA_20220922.tar`
- 原始目录：`data/visa_raw/`
- 单类协议目录：`data/visa_1cls/`

匿名下载命令：

```powershell
aws s3 cp --no-sign-request s3://amazon-visual-anomaly/VisA_20220922.tar data/downloads/VisA_20220922.tar
```

## Shot 清单

统一 1/2/4-shot 清单保存到 `data/splits/` 并提交 Git。清单只写相对路径，不复制数据。

## MPDD

- 来源: Hugging Face 镜像 (原始 SharePoint 下载需要机构登录)
- 许可：据提供方官方仓库 <https://github.com/stepanje/MPDD> 的 `LICENSE` 文件记录为 **CC BY-NC-SA 4.0**（非商业）；本机副本取自 Hugging Face 镜像而非官方 SharePoint 分发，具体来源与再分发范围仍待与提供方最终确认。证据记录见 `docs/paper_writing_preparation_20260830/references/REFERENCE_AUDIT.md`（§3 数据集许可证据）与 `docs/CURRENT_DYNAMIC_FUSION_STATUS.md`。
- LFS SHA256: `69f8da73eea4a31451a50251e5c261e83e0c53f2d1a39a7d4dfc78b5c434ddd6`
- 原始目录: `data/mpdd_raw/MPDD/`
- 6个类别: bracket_black, bracket_brown, bracket_white, connector, metal_plate, tubes
- 测试图片: 458张, 异常图片: 282张 (含hole类异常)
- 清单: `data/splits/mpdd/manifest.json` — SHA256 `5a6a42dd12de1de9c977c2b10695f35b474d19b37f0c1492f64a7989226a9bd8`

## BTAD

- 来源: 公共服务器 (BTAD 文献引用)
- 许可：据原始作者仓库 <https://github.com/pankajmishra000/VT-ADL> 的数据集条目记录为 **CC BY-SA 4.0**（其 `CC-BY-SA` 标签链接指向 CC BY-SA 4.0 法律文本）；本地归档 `data/btad_raw/README.txt` 记 `License type: CC-BY-SA`（该文本未印版本号，版本以作者仓库链接的 4.0 法律文本为准）。再分发原图或改动版须保留署名、标注修改、链接许可并遵守 ShareAlike，具体条款待与提供方最终确认。注意：作者仓库根目录的 MIT 文件适用于 VT-ADL 代码，不适用于 BTAD 数据。证据记录见 `docs/paper_writing_preparation_20260830/BTAD_LICENSE_EVIDENCE.md`。
- 原始目录: `data/btad_raw/`
- 3个类别 (类别03使用BMP遮罩, 需特殊处理)
- 清单: `data/splits/btad/manifest.json` — SHA256 `40696d901a78006c342dce98625dc21221b8ee9f642ebb74b7c3f3ffc5a1d215`

## KolektorSDD2

用于工作流 F 的确认集（单产品、单类别，不是多类别数据集）。

- 官方页面：<https://www.vicos.si/resources/kolektorsdd2/>
- 下载入口 <https://go.vicos.si/kolektorsdd2> 会 301 到直接地址
  <https://data.vicos.si/datasets/KSDD/KolektorSDD2.zip>（路径大小写敏感）
- 许可：CC BY-NC-SA 4.0（非商业使用；商用需联系作者）
- 归档校验：大小 `853126555` B（与官方 `Content-Length` 逐字节一致），
  SHA256 `EDCDB486809B24F1D17B785E30C52FAFC5999554DD5FE18DDF77B61CEB6F36A8`
- 原始目录：`data/kolektorsdd2_raw/`，含 `train/`、`test/`、5 个 `split_weakly_*.pyb`
- 复核结果（按掩码非空判正/负）：train 246 正 / 2085 负，test 110 正 / 894 负 —— 与官方说明逐项一致
- 图像尺寸不固定（实测约 206–236 × 615–665），宽高比约 1:2.7，几何/画布处理需按可变尺寸考虑
- 注意：官方包内自带一对多余副本 `train/10301 (copy).png` 与 `train/10301_GT (copy).png`。
  后者不以 `_GT.png` 结尾，按后缀匹配做 GT 统计时会把它误计为图像（这正是 train 目录
  “2333 张图 vs 2331 个 GT” 的原因）；管线需显式排除这两个副本。
- 下载方式：官方主机单连接仅约 25 KB/s，但聚合带宽随连接数近似线性增长
  （实测 1 连接 25 KB/s → 4 连接 59 KB/s → 12 连接 244 KB/s → 16 连接 387 KB/s），
  且连接会在分片传完前被中断，故用可续传的分片脚本：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/fetch_kolektorsdd2.ps1 -Parts 16
```

  实测 16 分片并行续传约 360–440 KB/s，813 MB 用时约 39 分钟；脚本可重复执行
  （已完成分片跳过、未完成分片从自身字节偏移续传）。


