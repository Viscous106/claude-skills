---
name: kaggle-cli
description: Use when the user needs to install or authenticate the Kaggle CLI, list or inspect competitions, download competition or dataset files, submit predictions, check submissions or the leaderboard, or push a notebook/kernel for a code competition.
---

# Kaggle CLI (v2.x, 2026)

## Install

Requires Python 3.11+.

```bash
uv tool install kaggle        # or: pipx install kaggle
kaggle --version
```

## Authenticate (pick one)

| Method | How |
|---|---|
| OAuth (recommended) | `kaggle auth login` — opens a browser flow; the user must run this themselves (`! kaggle auth login` in the prompt). |
| Env var | `export KAGGLE_API_TOKEN=...` |
| Token file | put the token in `~/.kaggle/access_token` |
| Legacy | Account → Settings → "Create New Token" → `~/.kaggle/kaggle.json`, then `chmod 600 ~/.kaggle/kaggle.json` |

Rules: never print, cat, or commit tokens or `kaggle.json`; never paste them into
notes or the ledger. Verify auth with `kaggle competitions list --group entered`.

The competition must be **joined** (rules accepted on the website) before
`download` or `submit` work; the error is a 403 otherwise.

## Competitions

```bash
kaggle competitions list -s <search>                  # find the slug
kaggle competitions list --group entered              # what the user has joined
kaggle competitions files -c <slug>
kaggle competitions download -c <slug> -p data --unzip
kaggle competitions download -c <slug> -f train.csv -p data
kaggle competitions submit -c <slug> -f submission.csv -m "lgb_v3 cv=0.9412" --wait
kaggle competitions submissions -c <slug>             # history with public scores
kaggle competitions leaderboard -c <slug> -s           # show top of LB
kaggle competitions leaderboard -c <slug> -d -p lb/    # download full LB csv
kaggle competitions topics list <slug>                 # discussion titles
kaggle competitions topics show <topic-ref>            # full thread
```

Add `-v` for CSV output when parsing programmatically.

## Submission protocol

1. `check_submission.py --sub <file> --sample data/sample_submission.csv [--proba]`
   (in `kaggle-compete/scripts/`). Fix anything it reports.
2. Show the user: file, row count, CV score, message, and remaining daily
   submissions (count today's in `kaggle competitions submissions`). Wait for a yes.
3. Submit with a message that names the experiment and its CV so the ledger
   can be reconciled: `-m "<name> cv=<score>"`.
4. Record the public score: `ledger.py lb --name <name> --public <score>`.

Submission limits are usually 5/day (Playground) and reset at 00:00 UTC. Do not
burn slots on near-duplicate blends; use them to calibrate CV↔LB with
materially different submissions.

## Datasets and models

```bash
kaggle datasets list -s <search>
kaggle datasets download -d <owner>/<dataset> -p data --unzip
kaggle datasets files -d <owner>/<dataset>
kaggle models list -s <search>
```

Or in Python: `import kagglehub; path = kagglehub.dataset_download("owner/dataset")`.

## Code competitions (notebook submissions)

The notebook runs offline (no internet), under a wall-clock limit (commonly 9–12h
CPU/GPU; check the rules), and must write `submission.csv` to `/kaggle/working`.

```bash
mkdir kernel && cd kernel
kaggle kernels init -p .               # writes kernel-metadata.json
# edit: id "<user>/<slug>-infer", code_file, language python, kernel_type script,
#       enable_gpu true/false, enable_internet false,
#       competition_sources ["<slug>"], dataset_sources ["<user>/<weights-dataset>"]
kaggle kernels push -p .
kaggle kernels status <user>/<slug>-infer
kaggle kernels output <user>/<slug>-infer -p out/
kaggle competitions submit -c <slug> -k <user>/<slug>-infer -v <version> -m "..."
```

Ship trained weights as a private dataset (`kaggle datasets create -p weights/`
after `kaggle datasets init -p weights/`), and pip wheels the same way if the
competition image lacks a library. Always include a fallback: if inference
errors or times out, write the sample submission so the run still scores.

## Kaggle notebooks as free compute

~30 GPU hours/week (P100/T4x2), 12h session limit, 20 GB `/kaggle/working`.
Use them for the GPU-heavy members of the ensemble; download OOF/test `.npy`
files back with `kaggle kernels output` and merge into local `preds/`.
