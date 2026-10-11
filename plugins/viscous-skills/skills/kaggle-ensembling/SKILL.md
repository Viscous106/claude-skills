---
name: kaggle-ensembling
description: Use when combining multiple Kaggle models — blending out-of-fold predictions, hill climbing, weighted/rank averaging, Ridge or GBDT stacking, multi-level stacks, pseudo-labelling or distillation — or when deciding which models to keep for the final submission.
---

# Ensembling: turn many OOF files into one leaderboard jump

Ensembling is where most 1st places are decided (150-model four-level stack,
March 2026; 75-of-500 three-level stack; hundreds of models hill-climbed). It only
works if every model wrote honest OOF predictions on the **same frozen folds**.

Script: `kaggle-compete/scripts/hill_climb.py`.

## Conventions

- `preds/<name>_oof.npy` shape `[n_train]` (or `[n_train, n_classes]`), aligned
  to `train.csv` row order; `preds/<name>_test.npy` aligned to `test.csv`, the
  average over fold models (and seeds).
- Keep a `preds/README.md` line per model: features, target transform, CV.
- Never blend with weights fit on the test set or on the public LB.

## Step 1: Hill climbing (do this early and often)

```bash
python scripts/hill_climb.py --preds preds --y y.npy --metric auc --rank --out-test blend_test.npy
python scripts/hill_climb.py --preds preds --y y.npy --metric rmse --negative --weights 0.02:1:0.02
```

- Starts from the best single model, greedily adds the (model, weight) that most
  improves OOF, stops when nothing helps. Weak-but-different models get picked;
  near-duplicates get ignored. Reads the output as a diversity report: if your
  last five models never enter the blend, build something different.
- `--rank` for AUC-type metrics; `--negative` can help for RMSE-type metrics but
  increases overfitting risk — confirm with a second fold seed if you have one.
- Honest estimate: the hill-climb OOF score is optimistic by a little (weights
  fit on OOF). With ≤30 models and n ≥ 10k this is usually < fold noise; with
  many models, run the climb inside folds (fit weights on 4 folds' OOF, score
  the 5th) to get a nested score before trusting it.

## Step 2: Stacking (level 2)

Inputs: the OOF matrix `[n_train, n_models]` and the matching test matrix.
Add cheap meta-features: row-wise mean, std, min, max of the level-1 preds, and
optionally the few strongest raw features.

Meta-models that work:
- **Ridge / logistic regression** on rank-transformed OOF (try alphas 0.1–100);
  the most robust choice, often the final answer in Playground competitions.
- **Small GBDT** (`num_leaves=7..15, learning_rate=0.01, strong regularisation`)
  — captures interactions between models; prone to overfit, needs nested CV.
- **Small MLP** on OOF + meta-features — a different inductive bias for level 2.

Fit the meta-model with the same `folds.csv` (so level-2 OOF exists), producing
`preds/l2_ridge_oof.npy` etc. Level 3 is then a simple average or a second hill
climb over the level-2 models. Three levels is the practical max.

Honesty rule: level-2 is trained on OOF predictions that were themselves produced
out-of-fold, so a single CV pass is honest **as long as every level-1 model used
the same folds**. If some models used different folds or full-train fits, their
OOF is leaky and will dominate the stack while losing on the LB.

## Step 3: Diversity engineering (when the blend stalls)

Build models that are *different*, not just better:
- different family (GBDT ↔ TabPFN/TabICL ↔ MLP/TabM ↔ kNN/SVR ↔ linear);
- different targets: raw, log, rank, ratio to a base feature, residual from
  a linear/GBDT model, predicting an imputed key feature;
- different feature views: raw only, engineered only, target-encoded only,
  per-group models, models on subsets of rows (e.g. only rows with the key
  feature missing);
- different loss (MSE vs MAE vs quantile; logloss vs focal);
- more seeds/folds for the strongest families (10-fold, 100-fold is a known trick
  on small Playground data).

## Pseudo-labelling and distillation

- **Pseudo-labelling**: add confident test predictions (or all, for regression)
  as training rows, retrain; keep CV honest by adding pseudo-labels only inside
  the training fold. Helps most when test is large relative to train and drift
  is low. Verify on a held-out fold seed.
- **Distillation**: train a new model on the ensemble's OOF/test predictions as
  soft targets; it becomes a strong, smooth level-1 member and a cheap final
  model for code competitions with runtime limits.

## Final assembly

1. Rebuild the blend/stack from scratch from `preds/` (no notebook state).
2. Post-process per the metric (`kaggle-tabular` § metric-specific).
3. `check_submission.py`, then record the ensemble as its own ledger entry
   with the nested CV and the list of members.
4. Keep a conservative variant (rank average of the top-5 by weight) as the
   second final submission (see `kaggle-validation` § final selection).
