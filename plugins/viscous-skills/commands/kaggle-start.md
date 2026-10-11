---
description: Bootstrap a Kaggle competition workspace — recon, data download, frozen folds, drift check, baseline, first submission. Usage: /kaggle-start <competition-slug>
---

Load the `kaggle-compete` skill and run its Day-1 checklist for competition `$ARGUMENTS`.

Steps, in order, reporting after each:
1. Recon: `kaggle competitions list -s $ARGUMENTS`, then read the overview, data, evaluation and rules pages (metric, deadline, submission limit, code competition or not, external data policy). Skim the top discussion topics via `kaggle competitions topics list $ARGUMENTS`. Write `NOTES.md` with these facts and an initial idea backlog.
2. Download data into `data/` with `--unzip`. Print shapes, dtypes, target distribution, missingness, and train/test id structure.
3. Use the `kaggle-validation` skill to choose a fold strategy; create `folds.csv` with `make_folds.py`; run `adversarial_validation.py` and report the AUC.
4. Train one LightGBM baseline with the `kaggle-tabular` fold-loop template, writing `preds/lgb_v1_{oof,test}.npy`, `subs/lgb_v1.csv`, and a ledger entry marked `--accepted`.
5. Validate `subs/lgb_v1.csv` with `check_submission.py`. Show the user the CV score and the exact submit command, and ask for a yes before submitting. After the submission scores, record the public score with `ledger.py lb`.
6. Finish with a ranked backlog of the next five experiments (one change each) and what each is expected to gain.

If the Kaggle CLI is not installed or not authenticated, stop at step 1 and give the user the install/auth commands from the `kaggle-cli` skill to run themselves.
