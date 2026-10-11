#!/usr/bin/env python3
"""Hill-climbing blend of out-of-fold predictions (Deotte-style).

Expects a directory of prediction files named `<model>_oof.npy` and
`<model>_test.npy` (shape: [n_rows] or [n_rows, n_classes]) plus the target
as a .npy or a CSV column. Greedily adds the model+weight that most improves
the OOF metric, starting from the best single model; stops when nothing
improves by more than --tol. Diversity wins: weak but different models often
get picked over strong but redundant ones.

Examples:
  hill_climb.py --preds preds/ --y y.npy --metric auc
  hill_climb.py --preds preds/ --y train.csv --y-col target --metric rmse --negative
  hill_climb.py --preds preds/ --y y.npy --metric logloss --out-test blend_test.npy
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

MAXIMIZE = {"auc", "accuracy", "f1", "r2", "map", "ndcg"}


def score(metric, y, p):
    from sklearn import metrics as M
    if metric == "auc":
        return M.roc_auc_score(y, p)
    if metric == "rmse":
        return float(np.sqrt(M.mean_squared_error(y, p)))
    if metric == "mae":
        return M.mean_absolute_error(y, p)
    if metric == "rmsle":
        return float(np.sqrt(M.mean_squared_log_error(y, np.clip(p, 0, None))))
    if metric == "logloss":
        return M.log_loss(y, np.clip(p, 1e-7, 1 - 1e-7))
    if metric == "accuracy":
        return M.accuracy_score(y, p.argmax(1) if p.ndim == 2 else (p > 0.5).astype(int))
    if metric == "f1":
        return M.f1_score(y, (p > 0.5).astype(int))
    if metric == "r2":
        return M.r2_score(y, p)
    if metric == "mape":
        return M.mean_absolute_percentage_error(y, p)
    sys.exit(f"unknown metric {metric}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--preds", required=True, help="directory with <model>_oof.npy / <model>_test.npy")
    p.add_argument("--y", required=True, help="target .npy, or CSV (use --y-col)")
    p.add_argument("--y-col", default=None)
    p.add_argument("--metric", default="auc")
    p.add_argument("--weights", default="0.05:1.0:0.05", help="start:stop:step for candidate weights")
    p.add_argument("--negative", action="store_true", help="also try negative weights (can help, can overfit)")
    p.add_argument("--max-models", type=int, default=50)
    p.add_argument("--tol", type=float, default=1e-6)
    p.add_argument("--rank", action="store_true", help="rank-transform predictions first (AUC-type metrics)")
    p.add_argument("--out-test", default=None, help="write blended test predictions here (.npy)")
    p.add_argument("--out-json", default="blend_weights.json")
    a = p.parse_args()

    if a.y.endswith(".npy"):
        y = np.load(a.y)
    else:
        import pandas as pd
        if not a.y_col:
            sys.exit("--y-col required when --y is a CSV")
        y = pd.read_csv(a.y)[a.y_col].values

    names, oofs, tests = [], [], []
    for f in sorted(glob.glob(os.path.join(a.preds, "*_oof.npy"))):
        name = os.path.basename(f)[: -len("_oof.npy")]
        oof = np.load(f)
        if len(oof) != len(y):
            print(f"skip {name}: oof length {len(oof)} != {len(y)}")
            continue
        tf = os.path.join(a.preds, f"{name}_test.npy")
        names.append(name)
        oofs.append(oof)
        tests.append(np.load(tf) if os.path.exists(tf) else None)
    if not names:
        sys.exit("no *_oof.npy files found")

    if a.rank:
        from scipy.stats import rankdata
        oofs = [rankdata(o) / len(o) for o in oofs]
        tests = [None if t is None else rankdata(t) / len(t) for t in tests]

    maximize = a.metric in MAXIMIZE
    better = (lambda n, o: n > o + a.tol) if maximize else (lambda n, o: n < o - a.tol)
    singles = [score(a.metric, y, o) for o in oofs]
    for n, s in sorted(zip(names, singles), key=lambda t: -t[1] if maximize else t[1]):
        print(f"  {s:.6f}  {n}")

    best_i = int(np.argmax(singles) if maximize else np.argmin(singles))
    current = oofs[best_i].copy()
    weights = {names[best_i]: 1.0}
    cur_score = singles[best_i]
    print(f"\nstart: {names[best_i]} = {cur_score:.6f}")

    w0, w1, ws = (float(x) for x in a.weights.split(":"))
    grid = np.arange(w0, w1 + 1e-9, ws)
    if a.negative:
        grid = np.r_[-grid[::-1], grid]

    for step in range(a.max_models):
        best = None
        for j, o in enumerate(oofs):
            for w in grid:
                cand = (1 - w) * current + w * o
                s = score(a.metric, y, cand)
                if best is None or better(s, best[0]):
                    best = (s, j, w)
        if best is None or not better(best[0], cur_score):
            break
        s, j, w = best
        current = (1 - w) * current + w * oofs[j]
        for k in weights:
            weights[k] *= (1 - w)
        weights[names[j]] = weights.get(names[j], 0.0) + w
        cur_score = s
        print(f"step {step + 1}: +{names[j]} w={w:+.2f} -> {cur_score:.6f}")

    weights = {k: round(v, 6) for k, v in weights.items() if abs(v) > 1e-9}
    print(f"\nfinal OOF {a.metric} = {cur_score:.6f} with {len(weights)} models")
    for k, v in sorted(weights.items(), key=lambda t: -abs(t[1])):
        print(f"  {v:+.4f}  {k}")
    with open(a.out_json, "w") as fh:
        json.dump({"metric": a.metric, "oof_score": cur_score, "rank": a.rank, "weights": weights}, fh, indent=2)
    print(f"wrote {a.out_json}")

    if a.out_test:
        missing = [k for k in weights if tests[names.index(k)] is None]
        if missing:
            sys.exit(f"cannot blend test: missing test preds for {missing}")
        blend = sum(weights[k] * tests[names.index(k)] for k in weights)
        np.save(a.out_test, blend)
        print(f"wrote {a.out_test} shape={blend.shape}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
