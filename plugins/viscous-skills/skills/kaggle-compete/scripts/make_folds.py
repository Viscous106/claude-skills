#!/usr/bin/env python3
"""Create and freeze cross-validation folds for a competition.

Writes a CSV with the id column (or row index) and a `fold` column. Freeze it
once at the start of the competition and have every experiment read it, so
that out-of-fold predictions from different experiments are comparable and
stackable.

Examples:
  make_folds.py --train train.csv --target y --strategy stratified --out folds.csv
  make_folds.py --train train.csv --target y --strategy group --group-col patient_id
  make_folds.py --train train.csv --target y --strategy timeseries --time-col date
  make_folds.py --train train.csv --target y --strategy stratified-regression --bins 10
"""
import argparse
import sys

import numpy as np
import pandas as pd


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--train", required=True, help="training CSV/parquet")
    p.add_argument("--target", required=True, help="target column")
    p.add_argument("--id-col", default=None, help="id column to carry into the folds file (default: row index)")
    p.add_argument("--strategy", default="stratified",
                   choices=["stratified", "kfold", "group", "stratified-group", "timeseries", "stratified-regression"])
    p.add_argument("--group-col", default=None)
    p.add_argument("--time-col", default=None)
    p.add_argument("--bins", type=int, default=10, help="bins for stratified-regression")
    p.add_argument("--n-folds", type=int, default=5)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="folds.csv")
    a = p.parse_args()

    from sklearn.model_selection import GroupKFold, KFold, StratifiedGroupKFold, StratifiedKFold, TimeSeriesSplit

    df = pd.read_parquet(a.train) if a.train.endswith(".parquet") else pd.read_csv(a.train)
    y = df[a.target]
    fold = np.full(len(df), -1, dtype=int)

    if a.strategy == "stratified":
        splitter = StratifiedKFold(a.n_folds, shuffle=True, random_state=a.seed)
        splits = splitter.split(df, y)
    elif a.strategy == "kfold":
        splits = KFold(a.n_folds, shuffle=True, random_state=a.seed).split(df)
    elif a.strategy == "group":
        if not a.group_col:
            sys.exit("--group-col required for group strategy")
        splits = GroupKFold(a.n_folds).split(df, y, groups=df[a.group_col])
    elif a.strategy == "stratified-group":
        if not a.group_col:
            sys.exit("--group-col required for stratified-group strategy")
        splits = StratifiedGroupKFold(a.n_folds, shuffle=True, random_state=a.seed).split(df, y, groups=df[a.group_col])
    elif a.strategy == "stratified-regression":
        ybin = pd.qcut(y.rank(method="first"), q=a.bins, labels=False)
        splits = StratifiedKFold(a.n_folds, shuffle=True, random_state=a.seed).split(df, ybin)
    elif a.strategy == "timeseries":
        if not a.time_col:
            sys.exit("--time-col required for timeseries strategy")
        order = np.argsort(df[a.time_col].values, kind="stable")
        splits = ((order[tr], order[va]) for tr, va in TimeSeriesSplit(a.n_folds).split(order))
    else:  # pragma: no cover
        sys.exit(f"unknown strategy {a.strategy}")

    for k, (_, va_idx) in enumerate(splits):
        fold[va_idx] = k

    out = pd.DataFrame({"fold": fold})
    if a.id_col:
        out.insert(0, a.id_col, df[a.id_col].values)
    else:
        out.insert(0, "row", np.arange(len(df)))
    out.to_csv(a.out, index=False)

    assigned = (fold >= 0).sum()
    print(f"wrote {a.out}: {len(df)} rows, {a.n_folds} folds, strategy={a.strategy}, seed={a.seed}")
    if a.strategy == "timeseries":
        print(f"timeseries: {assigned} rows are validation rows; rows with fold=-1 are train-only (earliest block)")
    print(pd.Series(fold).value_counts().sort_index().to_string())
    if a.strategy in ("stratified", "stratified-group") and y.nunique() < 50:
        print("target rate per fold:")
        print(pd.crosstab(pd.Series(fold, name="fold"), y, normalize="index").round(4).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
