---
name: kaggle-validation
description: Use when designing cross-validation folds for a Kaggle competition, checking train/test drift, debugging a CV vs leaderboard mismatch, worrying about leaderboard shake-up, or choosing which final submissions to select.
---

# Validation: make CV predict the private leaderboard

A model that does well on local CV must do well on the private LB. That is the
only purpose of this skill. Everything else in the competition is built on it.

Scripts (in `kaggle-compete/scripts/`): `make_folds.py`, `adversarial_validation.py`,
`ledger.py`.

## 1. Choose the split that mirrors test

Ask: *how was test separated from train?* Then copy it.

| Situation | Strategy | `make_folds.py --strategy` |
|---|---|---|
| random rows, classification | stratified k-fold | `stratified` |
| random rows, regression | k-fold, or stratify on target bins if skewed | `kfold` / `stratified-regression --bins 10` |
| entities repeat (patient, user, device, image source) and test has **new** entities | group k-fold on the entity | `group --group-col <col>` |
| same, with imbalanced target | stratified group k-fold | `stratified-group` |
| test is later in time | forward/expanding splits; validate only on later blocks | `timeseries --time-col <col>` |
| test is a different distribution (drift) | see §2; validate on test-like rows or weight by P(test) | |
| multiple rows per sample (e.g. several views) | group on the sample id | `group` |

Defaults: 5 folds; 10 folds when n < 20k or the metric is noisy; repeat with 2–3
seeds for decisions below ~0.1% metric difference. Freeze `folds.csv`; commit it.

Group leakage check: for the chosen group column, assert no group appears in
more than one fold. For time: assert max(time in train fold) < min(time in val fold).

## 2. Adversarial validation (train vs test drift)

```bash
python scripts/adversarial_validation.py --train data/train.csv --test data/test.csv --target y --id-col id
```

- AUC ≤ 0.6: random folds are fine.
- AUC > 0.7: real drift. Options, in order: drop or coarsen the shifting
  features if they are not predictive of the target; build a validation set from
  the most test-like train rows (`--out ptest.csv`, take top 20% by P(test));
  weight training rows by P(test)/(1-P(test)); for time drift, use forward splits.
- Also run it with the id column **kept**: an id that separates train from test
  (or correlates with target) is a leak worth exploiting or a trap to avoid.

## 3. Track CV ↔ LB from the first submission

Log every submission: `ledger.py lb --name <exp> --public <score>`; `ledger.py show`
prints the correlation.

- Correlation > 0.7 across ≥4 materially different submissions: trust CV, stop
  looking at the LB except as a sanity check.
- Weak or negative: do not keep modelling. Debug (§5).
- Public set is small (<~2k rows or <20% of test): expect LB noise; CV wins.

Useful calibration: compute how the metric varies across your folds. If fold
std is 0.003, a public LB difference of 0.002 between two submissions is noise.

## 4. Shake-up insurance

- Simulate public/private: split OOF rows randomly 20/80 many times; rank your
  candidate submissions on each 20% chunk and on the 80%; if the "public" winner
  often differs from the "private" winner, the metric is noisy and you should
  prefer robust ensembles over sharp ones.
- Seed-average every final model (3–5 seeds), use all folds' test predictions
  (average of fold models), prefer rank averaging for AUC metrics.
- Keep the final pipeline deterministic and re-runnable from scratch.

## 5. CV better than LB (or vice versa): debug checklist

1. **Leak in CV**: target encoding or scaling fit on full train; group members
   across folds; duplicated rows across folds; features built from the target.
2. **Fold ≠ test construction**: time, groups, or sampling differ.
3. **Metric mismatch**: you optimise logloss but the competition is AUC/F1/
   quadratic kappa; threshold or rank post-processing missing; wrong averaging
   for multiclass.
4. **Drift**: adversarial AUC high; public set may also differ from private.
5. **Submission bug**: id misalignment, wrong column order, fold-model
   averaging missing on test, test preprocessing differs from train.
6. **Overfit to public LB**: picked blends by LB; stop and re-select by CV.

## 6. Final submission selection

- Slot 1: best honest CV (ensemble built with nested CV).
- Slot 2: a hedge — fewer models, lower variance, or rank-averaged; or the
  best single-family model if the ensemble has suspiciously many tiny weights.
- Never select by public LB alone; use LB only to break ties among CV-equivalent
  candidates.
- Verify both files with `check_submission.py` and re-run the pipeline once from
  clean state before the deadline.
