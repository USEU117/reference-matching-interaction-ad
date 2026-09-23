from pathlib import Path
import json
R=Path(__file__).resolve().parents[2];S=Path(__file__).resolve().parent
r=(S/'results.md').read_text(encoding='utf-8')
r=r.replace('because VisA is in-domain for the C branch: its frozen AnomalyCLIP checkpoint was trained on that dataset.','because VisA retains the conservative in-domain role specified in Section 4.1.1. The visual-only C path does not use the learned prompt outputs.')
(S/'results.md').write_text(r,encoding='utf-8')
m=(S/'manuscript.md').read_text(encoding='utf-8')
m=m.replace('Raw datasets and feature caches remain separate.','Raw datasets and feature caches remain separate. The reproduction entry point is `docs/REPRODUCE_TO_TABLES.md`; checkpoint paths and hashes are recorded in `docs/MODEL_WEIGHTS.md`.')
(S/'manuscript.md').write_text(m,encoding='utf-8')
t=json.loads((S/'tables.json').read_text(encoding='utf-8'))
t['design']['widths']=[2.5,4.4,3.4,6.7]
t['models']['headers'][0]='Item'
for sp in t.values():
 if 'note' in sp:sp['note']=sp['note'].replace('corrected geometry used in Section 4.2.4','corrected geometry used in Section 4.2.1')
(S/'tables.json').write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
w=(R/'dist/replication_package_20260920/weights/README.md').read_text(encoding='utf-8')
w=w.replace('（目录名 `9_12_4` = 图像 9 × 文本 12 × 4 层多尺度）','（具体 depth、n_ctx 与 text_n_ctx 以加载参数为准）')
w=w.replace('本文件是权重的**唯一清单**','本文件保留历史权重清单')
w=w.replace('（本机 = `C:\\Users\\lynle`）','')
header='''# 模型权重清单与来源边界（2026-09-23）

以下为 2026-09-20 的 46 项本机权重库存，保留其原有哈希、目标路径和获取线索；并非所有库存都进入当前论文。当前 Table 11/12 的外部家族为 AnomalyDINO、PatchCore、SubspaceAD、WinCLIP+、AnomalyCLIP；AdaptCLIP/ReMP 等库存不得据此写成本文已评估基线。

本轮重新核验了 AnomalyCLIP 的 30 个检查点：与保留源码 ZIP 全部一致，证据见 [来源复核](ANOMALYCLIP_CHECKPOINT_PROVENANCE_20260923.md) 和同名 JSON。其余 16 项沿用 09-20 记录，不冒称本轮重读。原归档下载地址没有完整记录，按记录的提交和 SHA-256 识别文件，不猜测未证实的下载地址。

权重许可须与模型发布方分别核对。仓库根 MIT 不自动覆盖外部预训练权重；本包不再分发权重。代码来源及固定 revision 见复现包 `methods/README.md`；其中没有明确列出的权重授权状态记为待确认，不补写臆测许可证。

## 历史逐文件库存（日期和数值保持原记录）

'''
(R/'docs/MODEL_WEIGHTS.md').write_text(header+w,encoding='utf-8')
(R/'docs/SUBMISSION_METADATA.md').write_text('''# 投稿元数据（2026-09-23）

权威稿：`paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx`。用户本轮只确认姓名，其余不确定，均不代填。

| 项目 | 当前内容 | 状态 |
|---|---|---|
| 作者 | 李越宁 / Yuening Li；英文稿署名 Yuening Li | 用户已确认；未添加其他作者 |
| 单位、城市、邮编、国家 | `[[AFFILIATIONS]]` | 待作者 |
| 通讯作者、邮箱 | `[[CORRESPONDING_AUTHOR]]` | 待作者 |
| ORCID | 未填 | 待作者，按投稿系统要求 |
| 资助与基金号 | `[[FUNDING]]` | 待作者；不擅自声明无资助 |
| 利益冲突 | `[[COMPETING_INTERESTS_TO_BE_CONFIRMED]]` | 待作者；原无利益冲突默认句撤回 |
| 伦理 | Not applicable; the study analyses industrial image data only, with no human or animal subjects. | 保留研究范围说明 |
| 仓库 | https://github.com/USEU117/reference-matching-interaction-ad | 摘要与可得性节一致 |
| 永久归档 DOI | 未建立 | 未虚构 |
| 目标期刊 | 未确定 | 当前延续已审阅版式；投稿时再套期刊模板 |
| 数据与权重许可 | 数据分别由提供方分发，权重许可单独核对 | 根 MIT 不代替第三方许可 |

正文为审阅稿；单位、通讯、资助和 COI 四项占位尚未清除，因此不能称为可直接投稿的定稿。
''',encoding='utf-8')
for rel in ['docs/REFERENCE_FIG_CONVERGENCE_PLAN.md','docs/REPRODUCIBILITY_PACKAGE.md']:
 p=R/rel;old=p.read_text(encoding='utf-8')
 note=('> 2026-09-23 更新：当前两页 S4 已入新稿。正文限定为已存 bootstrap 的数值稳定性，前缀相互依赖，N = 1000 是参照值；N >= 500 的区间宽度最大偏离为 6.8%，±5% 仅为参考带，全部序列从网格 N = 700 起保持在带内。下文旧建议中的“充分稳定/证明”不再作为当前稿表述。\n\n' if 'CONVERGENCE' in rel else '> 2026-09-23 当前复现入口见 `REPRODUCE_TO_TABLES.md`。现役源为 `scripts/paper_complete_review_20260920/`，旧 `manuscript_build_20260914/` 为历史链。版式母本必须保留，不能把所有 docx 一概排除；当前母本已受版本控制。下文体积及可执行性是历史快照。\n\n')
 p.write_text(note+old,encoding='utf-8')
print('Updated current manuscript and documentation')
