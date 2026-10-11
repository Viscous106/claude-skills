---
name: kaggle-tabular
description: Use when building or improving models for a tabular Kaggle competition (CSV/parquet data, classification or regression) — picking models, feature engineering, target encoding, GBDT parameters, writing the fold-loop training template, or using the GPU. Also has short pointers for image, text and time-series competitions.
---

# Tabular modelling for Kaggle (2026)

Follow the conventions in `kaggle-compete`: frozen `folds.csv`, every model writes
`preds/<name>_oof.npy` and `preds/<name>_test.npy`, one change per experiment.

## Model zoo and when to use each

| Model | Use when | Notes |
|---|---|---|
| LightGBM | always; first baseline; any size | CPU-fast; `device="gpu"` optional |
| XGBoost | always; `device="cuda"` | different splits/regularisation → diversity |
| CatBoost | many categoricals; strong defaults | ordered target stats built in; slow but robust |
| TabPFN-3 / TabPFN-2.6 | n ≤ ~50k rows, ≤ ~500 features; GPU | often best single model on small data; zero tuning; bag/subsample above the limit |
| TabICL v2 | same regime as TabPFN; faster predict | good second foundation model |
| TabM / RealMLP | mid/large data; GPU | MLP-family diversity; need tuning + ensembling |
| MLP (own PyTorch) | after GBDTs; embeddings for high-cardinality | diversity, and its embeddings can feed GBDTs |
| Linear/ridge/logistic on engineered + one-hot | always, cheap | weak alone, useful in blends and as a sanity baseline |
| kNN / SVR (cuML) | small/medium data; scaled features | classic Deotte diversity members |
| AutoGluon (`presets="best_quality"`) | time-boxed ceiling check | tells you how far you are from "easy" SOTA |

Diversity sources beyond model family: different feature subsets, raw vs
engineered, target transforms (log1p, rank, ratio to a base feature, residual
from a linear model), different seeds, different fold seeds (only for level-1
models that will not be stacked against each other).

## Known-good GBDT starting points

LightGBM (binary/regression):
```python
dict(objective=..., learning_rate=0.02, num_leaves=63, min_child_samples=40,
     feature_fraction=0.7, bagging_fraction=0.8, bagging_freq=1, lambda_l2=1.0,
     n_estimators=5000, verbose=-1, n_jobs=-1)   # early_stopping(200)
```
XGBoost: `max_depth=6..8, learning_rate=0.02, subsample=0.8, colsample_bytree=0.7, min_child_weight=5, reg_lambda=1, tree_method="hist", device="cuda", enable_categorical=True`, early stopping 200.
CatBoost: `depth=6..8, learning_rate=0.03, l2_leaf_reg=3, iterations=5000, od_type="Iter", od_wait=200, cat_features=[...], task_type="GPU"` when available.

Tune (Optuna, 30–60 trials) only after features settle, and only models that
survive hill climbing. Lower learning rate + more trees for final seeds.

## Feature engineering checklist (highest-yield first)

1. **OOF target encoding** of high-cardinality columns (and of pairs/triples of
   categoricals): compute inside each training fold with smoothing
   `(sum + prior*m) / (count + m)` for several `m` (e.g. 1, 10, 100); for test
   use the full-train statistic. Never compute it on the full train once.
2. **Count/frequency encoding** over train+test (no target involved, so safe).
3. **Group statistics**: mean/std/min/max/rank of numeric columns within
   categorical groups; row minus group mean.
4. **Original dataset** (Playground Series): add it as extra training rows
   (flag with `is_original`), and/or compute statistics from it as features.
   Check CV with and without.
5. **Interactions**: ratios, differences, products of the top-importance pairs;
   binned numeric × categorical.
6. **Missingness**: indicator per column with NaNs; count of NaNs per row;
   for a key missing feature, predict it with a model and use the prediction
   (and the residual target) as features.
7. **Hard rules in the data**: deterministic thresholds, caps, rounding patterns,
   duplicated rows with different targets — find them in EDA, encode them explicitly,
   and consider post-processing (clip, round, override).
8. **Numeric encodings for NNs**: quantile transform or rank-gauss; one-hot for
   low-cardinality; embeddings for high-cardinality.
9. **Text columns**: TF-IDF → SVD; or sentence-embeddings → PCA; feed to GBDT.
10. **Dates**: cyclic encodings, elapsed time, holidays, lags/rolling stats
    computed only from the past.

Feature selection: add features in blocks; keep a block only if CV improves beyond
fold noise; remove features with near-zero gain importance at the end.

## Fold-loop training template

```python
import numpy as np, pandas as pd, lightgbm as lgb
from sklearn.metrics import roc_auc_score

NAME = "lgb_v1"; TARGET = "y"; ID = "id"
train = pd.read_csv("data/train.csv"); test = pd.read_csv("data/test.csv")
folds = pd.read_csv("folds.csv")
train = train.merge(folds, on=ID, how="left"); assert train.fold.notna().all()
feats = [c for c in train.columns if c not in (ID, TARGET, "fold")]
cat = [c for c in feats if train[c].dtype == object]
for c in cat:  # consistent categories across train/test
    cats = pd.Categorical(pd.concat([train[c], test[c]])).categories
    train[c] = pd.Categorical(train[c], categories=cats); test[c] = pd.Categorical(test[c], categories=cats)

oof = np.zeros(len(train)); pred = np.zeros(len(test)); scores = []
for k in sorted(train.fold.unique()):
    tr, va = train[train.fold != k], train[train.fold == k]
    # fold-local feature engineering (target encoding etc.) goes HERE, fit on tr only
    m = lgb.LGBMClassifier(**PARAMS)
    m.fit(tr[feats], tr[TARGET], eval_set=[(va[feats], va[TARGET])],
          callbacks=[lgb.early_stopping(200, verbose=False)])
    oof[va.index] = m.predict_proba(va[feats])[:, 1]
    pred += m.predict_proba(test[feats])[:, 1] / train.fold.nunique()
    scores.append(roc_auc_score(va[TARGET], oof[va.index]))
cv = roc_auc_score(train[TARGET], oof)
print(NAME, f"cv={cv:.6f}", "folds=" + ",".join(f"{s:.5f}" for s in scores))
np.save(f"preds/{NAME}_oof.npy", oof); np.save(f"preds/{NAME}_test.npy", pred)
pd.DataFrame({ID: test[ID], TARGET: pred}).to_csv(f"subs/{NAME}.csv", index=False)
```

Then `ledger.py add --name lgb_v1 --cv <cv> --folds <list> --change "..."`.

Seed averaging: loop seeds inside the fold loop and average; name the file
`lgb_v1_s5` so it is clear it is a 5-seed average.

## Metric-specific post-processing

- **AUC**: rank-average blends; calibration irrelevant.
- **Logloss / Brier**: calibrate (temperature or isotonic on OOF); clip to [1e-5, 1-1e-5].
- **F1 / MCC / kappa / accuracy-with-threshold**: optimise the threshold on OOF
  (and per-class thresholds for multiclass); report expected variance.
- **RMSE with bounded/discrete targets**: clip to the training range; test rounding.
- **RMSLE / MAPE**: train on `log1p(y)` / weight by 1/y; back-transform.
- **Ranking/MAP@k**: optimise per-query cutoffs on OOF.

## GPU

cuDF/cuML (`pip install cudf-cu12 cuml-cu12`) give drop-in pandas/sklearn with
10–100× speed for kNN, SVR, logistic, target encoding, and `cuml.ensemble`.
XGBoost `device="cuda"`, LightGBM `device="gpu"`, CatBoost `task_type="GPU"`.
Use Kaggle notebooks (30 GPU-h/week) if there is no local GPU (see `kaggle-cli`).

## Other data types (short pointers)

- **Images**: `timm` backbones (convnext / efficientnet / eva / vit), AMP, EMA,
  strong aug, TTA; 5-fold with model soup/seed average; pseudo-label test when
  allowed; same OOF conventions.
- **Text**: `deberta-v3-large` fine-tune with layer-wise LR decay; or LLM
  (Qwen 7B–14B) QLoRA fine-tune for classification/regression heads; TF-IDF +
  linear as the cheap diverse member; code-competition offline constraints
  dominate — quantise and time-budget inference.
- **Time series**: forward CV only; lags/rolling features computed strictly from
  the past; GBDT on lag features beats most deep models; ensemble with a
  seasonal naive and a global NN (N-BEATS/TFT) for diversity.
- **LLM/agent competitions (ARC-style, reasoning)**: these are research
  competitions; read the forum and papers first, the playbook above does not apply.
