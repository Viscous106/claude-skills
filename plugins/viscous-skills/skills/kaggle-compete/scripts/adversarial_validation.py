#!/usr/bin/env python3
"""Adversarial validation: can a model tell train rows from test rows?

AUC ~0.5  -> train and test look alike; a random CV split mirrors the test set.
AUC >0.7  -> distribution shift. Inspect the top features: drop them, bin them,
             or build a validation set that resembles test (e.g. weight rows by
             P(test) or validate on the train rows most test-like).

Example:
  adversarial_validation.py --train train.csv --test test.csv --target y --id-col id
"""
import argparse
import sys

import numpy as np
import pandas as pd


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--train", required=True)
    p.add_argument("--test", required=True)
    p.add_argument("--target", required=True, help="target column (dropped from train)")
    p.add_argument("--id-col", default=None, help="id column to drop (keep it in if you suspect an id leak)")
    p.add_argument("--drop", default="", help="comma-separated extra columns to drop")
    p.add_argument("--n-folds", type=int, default=5)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--top", type=int, default=15)
    p.add_argument("--out", default=None, help="optional CSV of P(test) per train row for test-like validation weighting")
    a = p.parse_args()

    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.inspection import permutation_importance
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import StratifiedKFold

    read = lambda f: pd.read_parquet(f) if f.endswith(".parquet") else pd.read_csv(f)
    tr, te = read(a.train), read(a.test)
    drop = [c for c in [a.target, a.id_col] + a.drop.split(",") if c]
    tr = tr.drop(columns=[c for c in drop if c in tr.columns])
    te = te.drop(columns=[c for c in drop if c in te.columns])
    cols = [c for c in tr.columns if c in te.columns]
    X = pd.concat([tr[cols], te[cols]], ignore_index=True)
    y = np.r_[np.zeros(len(tr)), np.ones(len(te))]

    cat_cols = [c for c in cols if not pd.api.types.is_numeric_dtype(X[c]) or isinstance(X[c].dtype, pd.CategoricalDtype)]
    for c in cat_cols:
        X[c] = X[c].astype("category").cat.codes
    X = X.astype(float)
    cat_mask = np.array([c in cat_cols for c in cols])

    oof = np.zeros(len(X))
    skf = StratifiedKFold(a.n_folds, shuffle=True, random_state=a.seed)
    last = None
    for tr_idx, va_idx in skf.split(X, y):
        clf = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, categorical_features=cat_mask,
                                             random_state=a.seed)
        clf.fit(X.iloc[tr_idx], y[tr_idx])
        oof[va_idx] = clf.predict_proba(X.iloc[va_idx])[:, 1]
        last = (clf, va_idx)
    auc = roc_auc_score(y, oof)
    print(f"adversarial AUC = {auc:.4f}  (0.5 = indistinguishable, >0.7 = real shift)")

    clf, va_idx = last
    sub = np.random.RandomState(a.seed).choice(va_idx, size=min(5000, len(va_idx)), replace=False)
    imp = permutation_importance(clf, X.iloc[sub], y[sub], n_repeats=3, random_state=a.seed, scoring="roc_auc")
    order = np.argsort(-imp.importances_mean)[: a.top]
    print("\ntop shifted features (permutation importance on AUC):")
    for i in order:
        print(f"  {cols[i]:<40s} {imp.importances_mean[i]:+.4f}")

    if a.out:
        pd.DataFrame({"p_test": oof[: len(tr)]}).to_csv(a.out, index=False)
        print(f"\nwrote P(test) for train rows to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
