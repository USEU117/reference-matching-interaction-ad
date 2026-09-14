# 阶段 B 基线运行命令（自动生成，逐条可复现）

# 1) 原生 AnomalyDINO（MPDD + BTAD, K=1/4, seeds 0/1）
& .venv-anomalyclip\Scripts\python.exe scripts\paper_evidence_closeout_20260914\run_baseline_anomalydino.py

# 2) PatchCore（同一网格；BTAD 先镜像成 MVTec 布局）
& .venv-anomalyclip\Scripts\python.exe scripts\paper_evidence_closeout_20260914\run_baseline_patchcore.py --skip-existing

# 3) PatchCore 单单元等价命令（driver 内部按此调用，cwd=methods/patchcore/patchcore-inspection-main，PYTHONPATH=src）
# btad_s0_k1
.\.venv-patchcore\Scripts\python.exe bin/run_patchcore.py --gpu 0 --seed 0 --dump_predictions --log_group btad_s0_k1 --log_project btad_closeout .\outputs\patchcore\closeout patch_core -b wideresnet50 -le layer2 -le layer3 --pretrain_embed_dimension 1024 --target_embed_dimension 256 --anomaly_scorer_num_nn 1 --patchsize 3 --faiss_num_workers 1 sampler -p 0.1 approx_greedy_coreset dataset --resize 144 --imagesize 128 --batch_size 1 --num_workers 0 -d 01 -d 02 -d 03 mvtec .\data\patchcore_closeout\btad_s0_k1
# btad_s0_k4
.\.venv-patchcore\Scripts\python.exe bin/run_patchcore.py --gpu 0 --seed 0 --dump_predictions --log_group btad_s0_k4 --log_project btad_closeout .\outputs\patchcore\closeout patch_core -b wideresnet50 -le layer2 -le layer3 --pretrain_embed_dimension 1024 --target_embed_dimension 256 --anomaly_scorer_num_nn 1 --patchsize 3 --faiss_num_workers 1 sampler -p 0.1 approx_greedy_coreset dataset --resize 144 --imagesize 128 --batch_size 1 --num_workers 0 -d 01 -d 02 -d 03 mvtec .\data\patchcore_closeout\btad_s0_k4
# btad_s1_k1
.\.venv-patchcore\Scripts\python.exe bin/run_patchcore.py --gpu 0 --seed 1 --dump_predictions --log_group btad_s1_k1 --log_project btad_closeout .\outputs\patchcore\closeout patch_core -b wideresnet50 -le layer2 -le layer3 --pretrain_embed_dimension 1024 --target_embed_dimension 256 --anomaly_scorer_num_nn 1 --patchsize 3 --faiss_num_workers 1 sampler -p 0.1 approx_greedy_coreset dataset --resize 144 --imagesize 128 --batch_size 1 --num_workers 0 -d 01 -d 02 -d 03 mvtec .\data\patchcore_closeout\btad_s1_k1
# btad_s1_k4
.\.venv-patchcore\Scripts\python.exe bin/run_patchcore.py --gpu 0 --seed 1 --dump_predictions --log_group btad_s1_k4 --log_project btad_closeout .\outputs\patchcore\closeout patch_core -b wideresnet50 -le layer2 -le layer3 --pretrain_embed_dimension 1024 --target_embed_dimension 256 --anomaly_scorer_num_nn 1 --patchsize 3 --faiss_num_workers 1 sampler -p 0.1 approx_greedy_coreset dataset --resize 144 --imagesize 128 --batch_size 1 --num_workers 0 -d 01 -d 02 -d 03 mvtec .\data\patchcore_closeout\btad_s1_k4
# mpdd_s0_k1
.\.venv-patchcore\Scripts\python.exe bin/run_patchcore.py --gpu 0 --seed 0 --dump_predictions --log_group mpdd_s0_k1 --log_project mpdd_closeout .\outputs\patchcore\closeout patch_core -b wideresnet50 -le layer2 -le layer3 --pretrain_embed_dimension 1024 --target_embed_dimension 256 --anomaly_scorer_num_nn 1 --patchsize 3 --faiss_num_workers 1 sampler -p 0.1 approx_greedy_coreset dataset --resize 144 --imagesize 128 --batch_size 1 --num_workers 0 -d bracket_black -d bracket_brown -d bracket_white -d connector -d metal_plate -d tubes mvtec .\data\patchcore_closeout\mpdd_s0_k1
# mpdd_s0_k4
.\.venv-patchcore\Scripts\python.exe bin/run_patchcore.py --gpu 0 --seed 0 --dump_predictions --log_group mpdd_s0_k4 --log_project mpdd_closeout .\outputs\patchcore\closeout patch_core -b wideresnet50 -le layer2 -le layer3 --pretrain_embed_dimension 1024 --target_embed_dimension 256 --anomaly_scorer_num_nn 1 --patchsize 3 --faiss_num_workers 1 sampler -p 0.1 approx_greedy_coreset dataset --resize 144 --imagesize 128 --batch_size 1 --num_workers 0 -d bracket_black -d bracket_brown -d bracket_white -d connector -d metal_plate -d tubes mvtec .\data\patchcore_closeout\mpdd_s0_k4
# mpdd_s1_k1
.\.venv-patchcore\Scripts\python.exe bin/run_patchcore.py --gpu 0 --seed 1 --dump_predictions --log_group mpdd_s1_k1 --log_project mpdd_closeout .\outputs\patchcore\closeout patch_core -b wideresnet50 -le layer2 -le layer3 --pretrain_embed_dimension 1024 --target_embed_dimension 256 --anomaly_scorer_num_nn 1 --patchsize 3 --faiss_num_workers 1 sampler -p 0.1 approx_greedy_coreset dataset --resize 144 --imagesize 128 --batch_size 1 --num_workers 0 -d bracket_black -d bracket_brown -d bracket_white -d connector -d metal_plate -d tubes mvtec .\data\patchcore_closeout\mpdd_s1_k1
# mpdd_s1_k4
.\.venv-patchcore\Scripts\python.exe bin/run_patchcore.py --gpu 0 --seed 1 --dump_predictions --log_group mpdd_s1_k4 --log_project mpdd_closeout .\outputs\patchcore\closeout patch_core -b wideresnet50 -le layer2 -le layer3 --pretrain_embed_dimension 1024 --target_embed_dimension 256 --anomaly_scorer_num_nn 1 --patchsize 3 --faiss_num_workers 1 sampler -p 0.1 approx_greedy_coreset dataset --resize 144 --imagesize 128 --batch_size 1 --num_workers 0 -d bracket_black -d bracket_brown -d bracket_white -d connector -d metal_plate -d tubes mvtec .\data\patchcore_closeout\mpdd_s1_k4
