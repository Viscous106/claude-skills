#!/usr/bin/env python3
"""Append-only experiment ledger (experiments.jsonl) with a one-screen summary.

Every experiment gets one line: name, CV score, per-fold scores, what changed
vs its parent, and later the public LB score. The summary shows CV-LB
correlation so you know whether to trust local validation.

Examples:
  ledger.py add --name lgb_v3 --cv 0.9412 --folds 0.940,0.943,0.939,0.942,0.942 --parent lgb_v2 --change "add target-encoded city"
  ledger.py lb --name lgb_v3 --public 0.9388
  ledger.py show
"""
import argparse
import json
import os
import sys
import time


def load(path):
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        return [json.loads(l) for l in fh if l.strip()]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", default="experiments.jsonl")
    sp = p.add_subparsers(dest="cmd", required=True)
    add = sp.add_parser("add")
    add.add_argument("--name", required=True)
    add.add_argument("--cv", type=float, required=True)
    add.add_argument("--folds", default="", help="comma-separated per-fold scores")
    add.add_argument("--parent", default=None)
    add.add_argument("--change", default="", help="the ONE thing changed vs parent")
    add.add_argument("--notes", default="")
    add.add_argument("--accepted", action="store_true", help="mark as new baseline")
    lb = sp.add_parser("lb")
    lb.add_argument("--name", required=True)
    lb.add_argument("--public", type=float, required=True)
    sp.add_parser("show")
    a = p.parse_args()

    rows = load(a.file)
    if a.cmd == "add":
        folds = [float(x) for x in a.folds.split(",") if x.strip()]
        rec = {"ts": time.strftime("%Y-%m-%d %H:%M"), "name": a.name, "cv": a.cv, "folds": folds,
               "cv_std": (float(__import__("statistics").pstdev(folds)) if len(folds) > 1 else None),
               "parent": a.parent, "change": a.change, "notes": a.notes, "accepted": a.accepted, "public": None}
        with open(a.file, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        parent = next((r for r in rows if r["name"] == a.parent), None)
        if parent:
            d = a.cv - parent["cv"]
            print(f"{a.name}: cv {a.cv:.6f} vs parent {parent['name']} {parent['cv']:.6f} (delta {d:+.6f})")
            if rec["cv_std"] is not None and abs(d) < rec["cv_std"] / max(len(folds), 1) ** 0.5:
                print("  delta is within fold noise (std/sqrt(k)); treat as no change unless repeated with other seeds")
        else:
            print(f"{a.name}: cv {a.cv:.6f}")
        return 0
    if a.cmd == "lb":
        hit = False
        with open(a.file, "w") as fh:
            for r in rows:
                if r["name"] == a.name:
                    r["public"] = a.public
                    hit = True
                fh.write(json.dumps(r) + "\n")
        if not hit:
            sys.exit(f"no experiment named {a.name}")
        print(f"recorded public LB {a.public} for {a.name}")
        return 0
    if a.cmd == "show":
        if not rows:
            print("ledger empty")
            return 0
        print(f"{'name':<28}{'cv':>10}{'std':>8}{'public':>10}  {'acc':<4}{'change'}")
        for r in rows:
            std = f"{r['cv_std']:.4f}" if r.get("cv_std") is not None else "-"
            pub = f"{r['public']:.5f}" if r.get("public") is not None else "-"
            print(f"{r['name']:<28}{r['cv']:>10.5f}{std:>8}{pub:>10}  {'*' if r.get('accepted') else '':<4}{r.get('change','')}")
        pairs = [(r["cv"], r["public"]) for r in rows if r.get("public") is not None]
        if len(pairs) >= 3:
            import statistics as st
            cv, pub = zip(*pairs)
            try:
                corr = st.correlation(cv, pub)
                print(f"\nCV-LB correlation over {len(pairs)} submissions: {corr:+.3f} "
                      f"({'trust CV' if corr > 0.7 else 'weak: investigate CV scheme or LB noise'})")
            except st.StatisticsError:
                pass
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
