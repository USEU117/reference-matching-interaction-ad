# 模型权重清单与来源边界（2026-09-23）

以下为 2026-09-20 的 46 项本机权重库存，保留其原有哈希、目标路径和获取线索；并非所有库存都进入当前论文。当前 Table 11/12 的外部家族为 AnomalyDINO、PatchCore、SubspaceAD、WinCLIP+、AnomalyCLIP；AdaptCLIP/ReMP 等库存不得据此写成本文已评估基线。

本轮重新核验了 AnomalyCLIP 的 30 个检查点：与保留源码 ZIP 全部一致，证据见 [来源复核](ANOMALYCLIP_CHECKPOINT_PROVENANCE_20260923.md) 和同名 JSON。其余 16 项沿用 09-20 记录，不冒称本轮重读。原归档下载地址没有完整记录，按记录的提交和 SHA-256 识别文件，不猜测未证实的下载地址。

权重许可须与模型发布方分别核对。仓库根 MIT 不自动覆盖外部预训练权重；本包不再分发权重。代码来源及固定 revision 见复现包 `methods/README.md`；其中没有明确列出的权重授权状态记为待确认，不补写臆测许可证。

## 历史逐文件库存（日期和数值保持原记录）

# 模型权重的来源、目标路径与 SHA-256

**本包不携带任何大权重**（体积 + 许可双重原因）。本文件保留历史权重清单：每一条给出
目标路径、字节数、SHA-256 与获取方式。所有 SHA-256 都是 **2026-09-20 在本机对盘上文件实读**
（`hashlib.sha256`，4 MiB 分块），不是抄录、不是估算。

- 本机实读时间：2026-09-20（Asia/Shanghai）
- 实读方式：`python -c "hashlib.sha256(...)"`，逐文件 —— 逐条命令见 §4
- 共 **46** 个权重文件（项目内 35 + 环境缓存 11），合计 **12,858,068,253 B ≈ 12.0 GiB**

> 约定：下表"目标路径"一列，`<PKG>/` = 本包根目录；`<USER>/` = `%USERPROFILE%`
> 。把权重放到这些路径后，包内脚本即可直接运行 —— 脚本里的
> 路径都是相对 `Path(__file__).resolve().parents[2]` 或 `%USERPROFILE%\.cache` 解析的，
> 不含任何硬编码的机器名。

---

## 1. 项目内权重（35 个，须放在本包 `methods/` 下）

### 1.1 AnomalyCLIP 检查点（30 个，678.95 MB；随上游源码归档提供）

被 `scripts/export_deva_references.py`、`scripts/run_a1_visa_export_queue.py`、
`scripts/start_v3_2_adaptclip_branches.ps1` 等**硬编码引用**：

```text
CHECKPOINT = <PKG>/methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale_visa/epoch_15.pth
```

| 目标路径（`<PKG>/methods/AnomalyCLIP-main/checkpoints/` 下） | 字节数 | SHA-256 |
|---|---|---|
| `9_12_4_multiscale_visa/epoch_15.pth` ← **冻结结果实际加载的那一个** | 22,631,975 | `415c5dcb52668b8c33fb9c1a351c686d632b919df5b384d63fa9ce7a2338ced4` |
| `9_12_4_multiscale/epoch_15.pth` | 22,631,975 | `94ce202da3e6486a864b904fdfed5057de75846c5834e446fd1d2fe7f97acb44` |
| 其余 28 个（两目录各 epoch 1–14） | 见表末机器可读块 | 见表末机器可读块 |

**来源（2026-09-23 更正）**：这两个目录的检查点**随上游 `AnomalyCLIP` 源码归档一并提供**
（归档 commit `3911738c0867544f545a076ad78f3f11d9ecbfdf`，ZIP SHA-256
`533ED87B6658CDB247D063A249CEFEA54AB81623CB11683C6F02345B9A6CEAFE`；第一手记录见
`docs/reproduction_notes.md:13-23`，与下载同日）。它们是**上游发布的辅助域训练权重**
（具体 depth、n_ctx 与 text_n_ctx 以加载参数为准），**不是本项目自行训练**的产物。
本项目只做**零样本评估**：每个被评估数据集所用的 prompt learner 都不是在该数据集上训练的
（`9_12_4_multiscale_visa` 用于 MVTec AD 列；`9_12_4_multiscale` 用于 VisA / MPDD / BTAD 列
—— 即上游"从不用在某数据集上拟合过的 learner 去评估该数据集"的约定），**目标域未做拟合**。
旁证：30 个文件的 mtime 均为源时间戳 `2025-07-08 03:59:38`，而本项目目录 2026-07-24 才建立。
取法：解压上游归档即得，无需本地训练。`epoch_15.pth` 是全部导出脚本引用的那一个；
其余 epoch 只为审计保留。

### 1.2 其他方法权重（5 个）

| 目标路径 | 字节数 | SHA-256 | 来源 |
|---|---:|:---:|---|
| `<PKG>/methods/adaptclip/adaptclip_checkpoints/12_4_128_train_on_visa_3adapters_batch8/epoch_15.pth` | 7,520,074 | `777821da141eb57d159acef46868440faf773a2dd0acf5c276ec3f258c27edee` | 本项目在 AdaptCLIP 官方代码上微调（`methods/adaptclip/scripts/train_adaptclip.sh`）；上游无此权重。被 `scripts/start_adaptclip_mvtec_gate_a.ps1` 等引用 |
| `<PKG>/methods/remp_ad/result/mvtec/epoch_15.pth` | 12,598,041 | `9a5b16f97a5b79b27b0f06dedd65c82839900921d9de272972970a3ed9ec99a0` | 本项目 ReMP-AD 训练产物（`methods/remp_ad/run_mvtec.sh`）；`scripts/start_remp_ad_mvtec.ps1` 使用 |
| `<PKG>/methods/SubspaceAD/checkpoints/dinov2-with-registers-giant/model.safetensors` | 4,546,030,112 | `c03832d44691e99b62ae28c4dfa2f134853a3614b3756c94f525109cce5a5051` | **HF 公开可下载**：`https://huggingface.co/facebook/dinov2-with-registers-giant/resolve/main/model.safetensors`（与 `experiments/dynamic_fusion/validation_handoff_20260911/E8/REPRODUCE.md` 第 45 行记录一致）。旁证：本机 HF 缓存里该文件的下载残片名为 `c03832d4…5051.incomplete`，**与实读 SHA-256 完全一致** |
| `<PKG>/methods/univad_official/pretrained_ckpts/groundingdino_swint_ogc.pth` | 693,997,677 | `3b3ca2563c77c69f651d7bd133e97139c186df06231157a64c507099c52bc799` | `https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth`（`scripts/validation_handoff_20260911/univad_local_run/fetch_assets.py` L28） |
| `<PKG>/methods/univad_official/pretrained_ckpts/sam_hq_vit_h.pth` | 2,570,940,653 | `a7ac14a085326d9fa6199c8c698c4f0e7280afdbb974d2c4660ec60877b45e35` | `https://huggingface.co/lkeab/hq-sam/resolve/main/sam_hq_vit_h.pth`（同上，L30） |

> 后两者的下载脚本已经在包里：`<PKG>/scripts/validation_handoff_20260911/univad_local_run/fetch_assets.py`
> （自带 Range 断点续传 + 代理配置）。直接运行即可，无需另找 URL。

### 1.3 空占位文件（不是权重，不需要补）

`methods/patchcore/patchcore-inspection-main/models/**/*.pkl`（180 个）在本机全部是 **0 字节**
占位文件，本包已按 `*.pkl` 规则排除；它们不含任何参数，缺失不影响结构。

---

## 2. 环境缓存权重（11 个，≈ 7.8 GiB，放在 `%USERPROFILE%\.cache` 下）

这些不在包内、也不在仓库内，由 `torch.hub` / `open_clip` / `timm` / `transformers` /
`huggingface_hub` 在首次调用时自动下载。**离线机器必须手工预置到下列路径**。

| 目标路径 | 字节数 | SHA-256 | 来源 URL / 仓库 |
|---|---:|:---:|---|
| `<USER>/.cache/clip/ViT-L-14-336px.pt` | 934,088,680 | `3035c92b350959924f9f00213499208652fc7ea050643e8b385c2dac08641f02` | OpenAI CLIP（`clip` 包，供 AnomalyCLIP/AnomalyDINO 用）：`https://openaipublic.azureedge.net/clip/models/3035c92b350959924f9f00213499208652fc7ea050643e8b385c2dac08641f02/ViT-L-14-336px.pt` —— 该 URL 路径内嵌的 64 位摘要 **就是本文件的 SHA-256**，下载后自校验 |
| `<USER>/.cache/clip/vit_b_16_plus_240-laion400m_e32-699c4b84.pt` | 833,559,975 | `699c4b843885d82733517f36f0911d7e1b360bcc1314dda81d8c56c76fe9524d` | open_clip v0.2 权重（WinCLIP 用；URL 逐字取自包内 `methods/winclip/WinClip-master/WinCLIP/CLIPAD/pretrained.py` L118）：`https://github.com/mlfoundations/open_clip/releases/download/v0.2-weights/vit_b_16_plus_240-laion400m_e32-699c4b84.pt` |
| `<USER>/.cache/torch/hub/checkpoints/dinov2_vitg14_pretrain.pth` | 4,546,108,579 | `baf8467e50af277596bbbafa06887c177ee899ab46033649c383577d7e9309d3` | `torch.hub facebookresearch/dinov2`（DINOv2 ViT-g/14）；镜像 `https://dl.fbaipublicfiles.com/dinov2/dinov2_vitg14/dinov2_vitg14_pretrain.pth`（`fetch_assets.py` L32） |
| `<USER>/.cache/torch/hub/checkpoints/dinov2_vitb14_pretrain.pth` | 346,378,731 | `0b8b82f85de91b424aded121c7e1dcc2b7bc6d0adeea651bf73a13307fad8c73` | `https://dl.fbaipublicfiles.com/dinov2/dinov2_vitb14/dinov2_vitb14_pretrain.pth` |
| `<USER>/.cache/torch/hub/checkpoints/dinov2_vits14_pretrain.pth` | 88,283,115 | `b938bf1bc15cd2ec0feacfe3a1bb553fe8ea9ca46a7e1d8d00217f29aef60cd9` | `https://dl.fbaipublicfiles.com/dinov2/dinov2_vits14/dinov2_vits14_pretrain.pth` |
| `<USER>/.cache/torch/hub/checkpoints/wide_resnet50_2-95faca4d.pth` | 138,223,492 | `95faca4d11227dddf8633dbb5ff6c8a9003c1aa5b8945c73834b8007b10950b8` | torchvision 官方（PatchCore 骨干）：`https://download.pytorch.org/models/wide_resnet50_2-95faca4d.pth`。实测 `download.pytorch.org` 走代理返回 **403**，需 `HF_ENDPOINT=https://hf-mirror.com` 或手工放置 |
| `<USER>/.cache/torch/hub/checkpoints/dino_deitsmall8_300ep_pretrain.pth` | 86,728,949 | `10fee18a0e7714de9005f9d56975ca8993d5fb87dab867868e528132d2be176c` | `https://dl.fbaipublicfiles.com/dino/dino_deitsmall8_300ep_pretrain/dino_deitsmall8_300ep_pretrain.pth`（`fetch_assets.py` L26） |
| `<USER>/.cache/huggingface/hub/models--bert-base-uncased/snapshots/86b5e0934494bd15c9632b12f734a8a67f723594/model.safetensors` | 440,449,768 | `68d45e234eb4a928074dfd868cead0219ab85354cc53d20e772753c6bb9169d3` | HF `bert-base-uncased`（UniVAD 的 RAM 文本编码器；googlesearch 镜像：`HF_ENDPOINT=https://hf-mirror.com`） |
| `<USER>/.cache/huggingface/hub/models--timm--convnext_tiny.fb_in1k/snapshots/b43a6303c9fcf176d2d707478a128c2c91e93528/model.safetensors` | 114,374,272 | `08b9dc9c3a3a29421de7996761e176501896d1ae7fc3085cf56a643772329276` | HF `timm/convnext_tiny.fb_in1k`（E1/E2 额外编码器） |
| `<USER>/.cache/huggingface/hub/models--timm--convnext_tiny.in12k_ft_in1k/snapshots/aa096f03029c7f0ec052013f64c819b34f8ad790/model.safetensors` | 114,374,272 | `a1aefa409b513cf209b085424eb3efffe4e4a9f511491bc2c12ea35209e6bb95` | HF `timm/convnext_tiny.in12k_ft_in1k` |
| `<USER>/.cache/huggingface/hub/models--timm--swin_tiny_patch4_window7_224.ms_in1k/snapshots/4cc3a7275b50b53a7bec45f32c236ebe64227cff/model.safetensors` | 114,286,722 | `fb01861f793143135fa0d6cd97b1631e4b33eaa3ee162bbea9e62de1c76ebac1` | HF `timm/swin_tiny_patch4_window7_224.ms_in1k`（E3 编码器） |

**未列入、也不需要**：`<USER>/.cache/huggingface/.../<64位摘要>.incomplete`（335 MB）
是 2026-09-20 中断的下载残片，不是任何脚本的输入。

---

## 3. 离线复现建议

```powershell
# 1) 先放公开权重（有 URL 的那几个），全部用 sha256 校验：
$weights = @{
  "$env:USERPROFILE\.cache\clip\ViT-L-14-336px.pt" = "3035c92b350959924f9f00213499208652fc7ea050643e8b385c2dac08641f02"
  "$env:USERPROFILE\.cache\torch\hub\checkpoints\wide_resnet50_2-95faca4d.pth" = "95faca4d11227dddf8633dbb5ff6c8a9003c1aa5b8945c73834b8007b10950b8"
}
foreach ($p in $weights.Keys) {
  if (Test-Path $p) { (Get-FileHash $p -Algorithm SHA256).Hash.ToLower() -eq $weights[$p] }
}
# 2) 再放项目内权重：AnomalyCLIP 检查点随上游源码归档提供（解压即得）；
#    AdaptCLIP / ReMP-AD 为本项目训练产物，须取自本机副本或按 `train*.sh` 重训
# 3) 最后设离线开关，禁止联网回退：
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
```

`HF_ENDPOINT=https://hf-mirror.com` 只在**联网**取权重时用；一旦缓存齐了就改回
`HF_HUB_OFFLINE=1`（见 `<PKG>/docs/HANDOVER_20260919.md` 与
`<PKG>/docs/REPRODUCIBILITY_PACKAGE.md`）。

---

## 4. 上表是怎么读出来的（可复核）

```powershell
# 单个文件
python -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" <file>
# 或
(Get-FileHash <file> -Algorithm SHA256).Hash.ToLower()
```

本次实读覆盖的 46 个文件、逐条 `sha256  bytes  path`，见下方机器可读块
（路径 <PKG>/<USER> 已按 §1/§2 的约定缩写，解析时先展开）：

```text
# --- 项目内（<PKG> = 本包根） ---
415c5dcb52668b8c33fb9c1a351c686d632b919df5b384d63fa9ce7a2338ced4  22631975  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale_visa/epoch_15.pth
94ce202da3e6486a864b904fdfed5057de75846c5834e446fd1d2fe7f97acb44  22631975  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale/epoch_15.pth
de5df7fc2ec18acb5709e65b1889d586974d365c39d1aa4df728336633e4ee70  22631493  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale_visa/epoch_1.pth
c98c722977ac0fc42c1067a8038656c10466728f6e9d448aad9e3f6b3d5368b6  22631493  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale_visa/epoch_2.pth
d3e7a65d6b9ff057b5fa53bfc59bfa57a25619b5a5d9cd40ed37579e312ab4aa  22631493  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale_visa/epoch_3.pth
f56b0ed7bd9da05f77780a3c4318e038c258b99a02ad1455652cad146b3dded5  22631493  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale_visa/epoch_4.pth
f2c44c082a19abde2993e80044466c1e45a620cc24aad39e85bd65ed60d3572d  22631493  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale_visa/epoch_5.pth
402d63bca2150631fb09d8d1c7529712a4ee8eea29bd7746412eae99b4ec6dc5  22631493  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale_visa/epoch_6.pth
081526236212ebc011ec53babaf8f0da7e25fbe92300aa7cc68eb41ca29b054f  22631493  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale_visa/epoch_7.pth
3f2587be72657ab30fc26bc5957e130ba7359ff53c32beb7984be517a818427c  22631493  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale_visa/epoch_8.pth
4850f209b34912c33718b86c13d2a01c340907d182236a8ef8903f35c80daec0  22631493  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale_visa/epoch_9.pth
397255934bd313beeab2b610fa901f113e12342974687147cad78f502e5ae7e5  22631975  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale_visa/epoch_10.pth
843fb9df1c46da89f6976a42d10d5fe34675ad48eccb365e3f43785f925c2ae9  22631975  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale_visa/epoch_11.pth
17f69ad9ae4bcc5823fdd9ad56b51ec57cc641270280a1776c1014ea1969f282  22631975  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale_visa/epoch_12.pth
5bf5fd9c269e3f68e81134f4361c3239ba14d5f2cd4e3564f93f5b59f616cd19  22631975  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale_visa/epoch_13.pth
969dbaaa1a986f17d79dfb81d2ce90443d0e9dd9f19db7fd9a9190f97cc8e3d4  22631975  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale_visa/epoch_14.pth
a89d1ffe49d86995e936c8e91515efa878d4e1777c73888622091e89a8df9e5b  22631493  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale/epoch_1.pth
f6bfcd2ed1725b3d58dd06d5d38f7ef6d3b9c49d817bb4714a16f3153c3d7450  22631493  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale/epoch_2.pth
5af4c383158732845ac2ef195e5036e8528f187ed80173c8d993830a0abed64c  22631493  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale/epoch_3.pth
7ab9a9909711c89cac5f02f0c46c7baac82b09bfaca59a83271a50b195cad89f  22631493  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale/epoch_4.pth
317837a0ef5b46d2476c234d3fa77e8cfab7bbfa85711f5fe7eb7f50ea7151a0  22631493  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale/epoch_5.pth
04379155c0df8d4e1194335427091e626df512a9747e47c1bbb7ee3a55708164  22631493  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale/epoch_6.pth
41c5a77a355c27266d6a9c7b6da4b3ee2c193596873d889822e68a797a2688b2  22631493  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale/epoch_7.pth
c92bfa088eccb2efb71b27c9703c0f21158903581efd7292f42938ad96940c82  22631493  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale/epoch_8.pth
43f0eca2d506b88370a06c94a6cd557360c7bcb179a4f3f24981230349a9581a  22631493  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale/epoch_9.pth
7205c05df3319984b349686cbfd8cc01d3ac241a82f33943e9217cbb85604b0b  22631975  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale/epoch_10.pth
40017b0588b3e41aea4cf3902b388bbee494201b4406583f0a9c96f90818a986  22631975  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale/epoch_11.pth
ef4bdfad5689797d48296eeceb57343aabba5ae5a2c7e57d4b9e225d2d254252  22631975  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale/epoch_12.pth
4381596b44bbaa33e7b04b4a19a46582980f1ee8742414d71147c8be95ef90d7  22631975  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale/epoch_13.pth
fd2a3865c4cf1363b80f301da7dc181a54787e3c218cc1f3464650a5f749cb26  22631975  methods/AnomalyCLIP-main/checkpoints/9_12_4_multiscale/epoch_14.pth
777821da141eb57d159acef46868440faf773a2dd0acf5c276ec3f258c27edee   7520074  methods/adaptclip/adaptclip_checkpoints/12_4_128_train_on_visa_3adapters_batch8/epoch_15.pth
9a5b16f97a5b79b27b0f06dedd65c82839900921d9de272972970a3ed9ec99a0  12598041  methods/remp_ad/result/mvtec/epoch_15.pth
c03832d44691e99b62ae28c4dfa2f134853a3614b3756c94f525109cce5a5051  4546030112  methods/SubspaceAD/checkpoints/dinov2-with-registers-giant/model.safetensors
3b3ca2563c77c69f651d7bd133e97139c186df06231157a64c507099c52bc799  693997677  methods/univad_official/pretrained_ckpts/groundingdino_swint_ogc.pth
a7ac14a085326d9fa6199c8c698c4f0e7280afdbb974d2c4660ec60877b45e35  2570940653  methods/univad_official/pretrained_ckpts/sam_hq_vit_h.pth
# --- 环境缓存（<USER> = %USERPROFILE%） ---
3035c92b350959924f9f00213499208652fc7ea050643e8b385c2dac08641f02  934088680  .cache/clip/ViT-L-14-336px.pt
699c4b843885d82733517f36f0911d7e1b360bcc1314dda81d8c56c76fe9524d  833559975  .cache/clip/vit_b_16_plus_240-laion400m_e32-699c4b84.pt
baf8467e50af277596bbbafa06887c177ee899ab46033649c383577d7e9309d3  4546108579  .cache/torch/hub/checkpoints/dinov2_vitg14_pretrain.pth
0b8b82f85de91b424aded121c7e1dcc2b7bc6d0adeea651bf73a13307fad8c73  346378731  .cache/torch/hub/checkpoints/dinov2_vitb14_pretrain.pth
b938bf1bc15cd2ec0feacfe3a1bb553fe8ea9ca46a7e1d8d00217f29aef60cd9  88283115  .cache/torch/hub/checkpoints/dinov2_vits14_pretrain.pth
95faca4d11227dddf8633dbb5ff6c8a9003c1aa5b8945c73834b8007b10950b8  138223492  .cache/torch/hub/checkpoints/wide_resnet50_2-95faca4d.pth
10fee18a0e7714de9005f9d56975ca8993d5fb87dab867868e528132d2be176c  86728949  .cache/torch/hub/checkpoints/dino_deitsmall8_300ep_pretrain.pth
68d45e234eb4a928074dfd868cead0219ab85354cc53d20e772753c6bb9169d3  440449768  .cache/huggingface/hub/models--bert-base-uncased/snapshots/86b5e0934494bd15c9632b12f734a8a67f723594/model.safetensors
08b9dc9c3a3a29421de7996761e176501896d1ae7fc3085cf56a643772329276  114374272  .cache/huggingface/hub/models--timm--convnext_tiny.fb_in1k/snapshots/b43a6303c9fcf176d2d707478a128c2c91e93528/model.safetensors
a1aefa409b513cf209b085424eb3efffe4e4a9f511491bc2c12ea35209e6bb95  114374272  .cache/huggingface/hub/models--timm--convnext_tiny.in12k_ft_in1k/snapshots/aa096f03029c7f0ec052013f64c819b34f8ad790/model.safetensors
fb01861f793143135fa0d6cd97b1631e4b33eaa3ee162bbea9e62de1c76ebac1  114286722  .cache/huggingface/hub/models--timm--swin_tiny_patch4_window7_224.ms_in1k/snapshots/4cc3a7275b50b53a7bec45f32c236ebe64227cff/model.safetensors
```

### 未取得 SHA-256 的项

**无。** 46 项全部在本机实读成功，没有 `[[SHA256]]` 占位。
唯一无法给出**独立下载 URL**的是 §1.2 中的 2 个**本项目训练**权重
（AdaptCLIP ×1、ReMP-AD ×1）：它们在公网上不存在，只能从本机副本取得或按对应
`train*.sh` 配置重训。§1.1 的 AnomalyCLIP 30 个检查点**不属于此列**：它们随上游
AnomalyCLIP 源码归档一并提供（commit `3911738c…`，ZIP SHA-256 `533ED87B…`），
**不是本项目训练产物**。
