#!/usr/bin/env python3
"""Validate a submission file against the competition's sample_submission.

Catches the mistakes that waste a daily submission: wrong columns, wrong row
count, ids missing or duplicated, NaN/inf, probabilities outside [0, 1],
labels outside the training label set.

Example:
  check_submission.py --sub submission.csv --sample sample_submission.csv
  check_submission.py --sub submission.csv --sample sample_submission.csv --proba
  check_submission.py --sub submission.csv --sample sample_submission.csv --labels train.csv --target y
"""
import argparse
import sys

import numpy as np
import pandas as pd


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--sub", required=True)
    p.add_argument("--sample", required=True)
    p.add_argument("--proba", action="store_true", help="prediction columns must be in [0,1]")
    p.add_argument("--labels", default=None, help="train CSV; predictions must be in its label set")
    p.add_argument("--target", default=None, help="target column in --labels")
    a = p.parse_args()

    sub, sample = pd.read_csv(a.sub), pd.read_csv(a.sample)
    problems = []
    if list(sub.columns) != list(sample.columns):
        problems.append(f"columns {list(sub.columns)} != sample {list(sample.columns)}")
    if len(sub) != len(sample):
        problems.append(f"row count {len(sub)} != sample {len(sample)}")
    idc = sample.columns[0]
    if idc in sub.columns:
        if sub[idc].duplicated().any():
            problems.append(f"{sub[idc].duplicated().sum()} duplicated ids")
        missing = set(sample[idc]) - set(sub[idc])
        extra = set(sub[idc]) - set(sample[idc])
        if missing:
            problems.append(f"{len(missing)} sample ids missing from submission (e.g. {list(missing)[:3]})")
        if extra:
            problems.append(f"{len(extra)} ids not in sample (e.g. {list(extra)[:3]})")
        if not problems and not sub[idc].equals(sample[idc]):
            print("note: id order differs from sample (usually fine, Kaggle joins on id)")
    pred_cols = [c for c in sub.columns if c != idc]
    for c in pred_cols:
        col = sub[c]
        if col.isna().any():
            problems.append(f"{c}: {col.isna().sum()} NaN")
        if pd.api.types.is_numeric_dtype(col):
            if np.isinf(col.astype(float)).any():
                problems.append(f"{c}: inf values")
            if a.proba and ((col < 0) | (col > 1)).any():
                problems.append(f"{c}: values outside [0,1] (min {col.min()}, max {col.max()})")
            if col.nunique() == 1:
                problems.append(f"{c}: constant prediction ({col.iloc[0]})")
        if a.labels and a.target:
            labels = set(pd.read_csv(a.labels)[a.target].unique())
            bad = set(col.unique()) - labels
            if bad:
                problems.append(f"{c}: labels not in train: {list(bad)[:5]}")
        print(f"{c}: {col.describe().to_dict() if pd.api.types.is_numeric_dtype(col) else col.value_counts().head(5).to_dict()}")

    if problems:
        print("\nPROBLEMS:")
        for x in problems:
            print(f"  - {x}")
        return 1
    print(f"\nOK: {len(sub)} rows, columns {list(sub.columns)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
