---
name: kaggle-compete
description: Use when the user is working on any Kaggle competition — starting one, climbing the leaderboard, choosing a CV scheme, running experiments, ensembling, or picking final submissions. Master playbook; loads the kaggle-cli, kaggle-validation, kaggle-tabular and kaggle-ensembling skills as needed.
---

# Kaggle competition playbook

The goal is a high **private** leaderboard rank, not a high public one. Everything
below exists to make local cross-validation (CV) trustworthy and then to grind
CV upward with many diverse, logged, reproducible experiments. This is how the
2025–2026 winners work (see `reference.md` for the research digest and sources).

Sibling skills: `kaggle-cli` (API, downloads, submissions), `kaggle-validation`
(fold design, adversarial validation, CV↔LB, final pick), `kaggle-tabular`
(2026 model zoo, feature engineering, training template), `kaggle-ensembling`
(OOF conventions, hill climbing, stacking). Load the one you need when you get
to that phase.

Helper scripts live in `scripts/` next to this file (run with
`uv run --with numpy --with pandas --with scikit-learn --with scipy python <script>`
if the libs are missing):

| Script | Purpose |
|---|---|
| `make_folds.py` | create and freeze folds (stratified / group / time / stratified-regression) |
| `adversarial_validation.py` | train-vs-test drift AUC and the features that cause it |
| `hill_climb.py` | greedy OOF blend of `<model>_oof.npy` files, writes weights + test blend |
| `check_submission.py` | validate a submission against `sample_submission.csv` |
| `ledger.py` | append-only experiment log with CV↔LB correlation |

## Non-negotiable rules

1. **Folds are frozen before the first model.** `folds.csv` is created once, every
   experiment reads it. Changing folds mid-competition invalidates every saved
   OOF file and the ensemble built on them.
2. **Every experiment writes three things**: `preds/<name>_oof.npy`,
   `preds/<name>_test.npy`, and one line in `experiments.jsonl` via `ledger.py`.
   No OOF file, no experiment. This is what makes stacking possible at the end.
3. **One change per experiment**, named after its parent (`lgb_v3` from `lgb_v2`,
   change = "add OOF target encoding on city"). Compare with fold noise in mind:
   a delta smaller than `std(folds)/sqrt(k)` is not a result until repeated with
   another seed.
4. **CV is the truth; the public LB is a sanity check.** Log every public score
   into the ledger. If CV↔LB correlation is weak, stop improving models and fix
   validation first (`kaggle-validation`).
5. **Submissions are a budget.** Run `check_submission.py` before every submit.
   Never submit without the user's go-ahead on the file and message.
6. **Read the forum and public notebooks like papers.** The top notebooks tell
   you the baseline CV everyone has; the discussion threads tell you about
   leaks, drift, metric quirks and the original dataset (Playground series).
7. **Search prior art.** Similar past competitions and their write-ups are
   indexed at https://kaggle.farid.one/ ; winning ideas transfer.
8. **Never touch test labels or leak the future**: no fitting on test, no
   target encoding without out-of-fold, no features computed over train+test
   that use the target, no post-deadline resources in code competitions.

## Phases

### 0. Recon (first hour)
- `kaggle competitions list -s <name>` then read overview, data, evaluation,
  rules (submission limit, code competition? runtime limit? external data?),
  timeline. Note the metric exactly and whether it is rank-based (AUC) or
  value-based (RMSE, logloss) — it changes how you ensemble and post-process.
- Read the top 10 notebooks (sorted by score) and the top 20 discussion threads.
  Extract: baseline CV scores, known leaks, CV scheme people use, drift notes.
- Check for the Playground "original dataset" and whether using it helps.
- Write `NOTES.md`: metric, deadline, submission limit, data shape, known tricks,
  idea backlog ranked by expected gain × cheapness.

### 1. EDA and data checks (short, targeted)
- Shapes, dtypes, target distribution, missingness pattern per column, cardinality,
  duplicates between train and test, id structure (ids are sometimes leaks or
  shifted — check id vs target and id vs train/test).
- `adversarial_validation.py`: AUC near 0.5 means random folds mirror test.
  Above ~0.7 means drift; see `kaggle-validation` before building anything.

### 2. Validation
- Pick the strategy that reproduces how test was split from train (random →
  stratified k-fold; entities repeat → group k-fold; time → forward splits).
  Default 5 folds, 10 if the data is small or the metric is noisy.
- `make_folds.py ... --out folds.csv`. Commit the file.

### 3. Baseline (same day)
- One GBDT with sensible defaults on raw features, writing OOF/test preds.
  Submit it once to establish the CV↔LB relationship. Record both.

### 4. Iterate (most of the competition)
Priority order of where gains come from, by evidence from winners:
1. Validation correctness and leak-free target encoding of high-cardinality columns.
2. Feature engineering (interactions, counts, group stats, original-data stats,
   hard-threshold rules the data contains, missing indicators).
3. Model diversity: GBDT trio + TabPFN/TabICL (small data) + an MLP/TabM/RealMLP
   + linear/kNN/SVR on scaled features. Different feature sets, targets
   (raw / ratio / residual) and seeds also count as diversity.
4. Ensembling (hill climbing, then stacking) — usually the single largest final jump.
5. Hyperparameter tuning — last, and only on models that will survive the blend.

Run experiments in parallel where possible; use the GPU (`cuML`, `XGBoost`
`device="cuda"`, PyTorch) so iteration speed is not the bottleneck.

### 5. Ensemble (last third of the competition)
- `hill_climb.py --preds preds --y y.npy --metric <metric>` as soon as you
  have 5+ OOF files; rerun whenever new models land.
- Then stacking per `kaggle-ensembling`: level-2 GBDT + NN on OOF columns, level-3
  simple average. Keep it honest (nested CV for meta-models).

### 6. Final selection (last 2 days)
- Pick by honest CV. Use both final slots: best-CV ensemble + a more conservative
  variant (fewer models or rank-averaged). Never pick by public LB alone.
- Re-run the final pipeline from scratch once to confirm it reproduces.

## Day-1 checklist for a new competition
```
kaggle competitions download <slug> -p data && (cd data && unzip -o -q '*.zip' && rm -f *.zip)
python scripts/make_folds.py --train data/train.csv --target <y> --id-col <id> --out folds.csv
python scripts/adversarial_validation.py --train data/train.csv --test data/test.csv --target <y> --id-col <id>
# baseline → preds/lgb_v1_{oof,test}.npy, ledger add --accepted
python scripts/check_submission.py --sub sub.csv --sample data/sample_submission.csv
kaggle competitions submit <slug> -f sub.csv -m "lgb_v1 cv=0.xxxx"
python scripts/ledger.py lb --name lgb_v1 --public <score>
```

CLI v2.x takes the slug positionally and has no `--unzip`; see `kaggle-cli`.
Some competitions also forbid fitting anything on test (in-class rules, for
example), which rules out adversarial validation and train+test encodings —
read the rules before running the checklist.

## Working style with the user
- Say what you will try and why before running long jobs; report CV deltas with
  fold std, not just means.
- Keep `NOTES.md` and the ledger current; they are the hand-off for the next session.
- When CV improves but LB does not, say so plainly and go to `kaggle-validation`.
