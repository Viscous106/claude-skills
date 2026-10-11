# What wins on Kaggle in 2025–2026 — research digest

Compiled 2026-10-11 from winner write-ups, NVIDIA grandmaster posts, the TabArena
benchmark and ML-engineering-agent papers. Load this when you want the evidence
behind the playbook.

## The pattern behind recent 1st places

- **Volume of diverse experiments, saved as OOF files, blended at the end.**
  The March 2026 Playground churn win: 850 experiments, 150 models selected,
  four-level stack. Chris Deotte's 1st places: hundreds of GBDT/NN/cuML models
  fed into hill climbing; "each new model doesn't need a great CV by itself, it
  needs to be different."
- **Multi-level stacking**: 75 level-1 models from 500 candidates (GBDT, NN, SVR,
  kNN) with four target formulations (direct, ratio, residual-from-linear,
  imputation of a key missing feature); level-2 GBDT and NN on OOF columns plus
  meta-features (per-row mean and std of level-1 preds); level-3 weighted average.
  CV 11.54 → private 11.44 RMSE, 1st place.
- **Leak-free OOF target encoding with multi-scale smoothing** on
  high-cardinality columns is repeatedly the single biggest feature gain.
- **Hard rules the data contains** (deterministic thresholds, clipping) beat
  what trees learn; inject them as features or post-processing.
- **Rank-transform before Ridge stacking** for AUC-type metrics; try alphas.
- **CV↔LB relation is the compass.** Winners of s6e2 titled the write-up
  "Diversity, Selection, and Trusting the CV–LB Relation."
- **GPU speed is a strategy**: cuDF/cuML/XGBoost-GPU make 100s of experiments
  affordable; LLM agents make writing them cheap. Iteration count wins.

## 2026 tabular model landscape (TabArena v0.1.4, June 2026, Elo)

| Rank | Model | Notes |
|---|---|---|
| 1 | AutoGluon 4h ensemble | ceiling reference, slow |
| 2 | TabPFN-3 (default) | single forward pass, GPU, ≤~50k rows sweet spot, statistically tied with AutoGluon on small data |
| 3 | TabPFN-2.6 | |
| 5 | TabICL v2 | fastest predict in the top tier |
| 6 | RealMLP (tuned+ens) | |
| 9 | LightGBM (tuned+ens) | best tree model, CPU |
| 10 | CatBoost (tuned+ens) | strong defaults |
| 13 | XGBoost (tuned+ens) | still a core ensemble member |
| — | TabM | parameter-efficient MLP ensembling; co-led 2025 board |

GBDT ensembles still win or podium in roughly 70% of tabular competitions, but
the foundation models (TabPFN, TabICL) are now mandatory ensemble members on
small/medium data, and often the best single model there. On >500k rows, GBDTs
and big MLPs dominate; TabPFN needs subsampling/bagging.

## Shake-up survival (from grandmaster handbooks)

- Replicate the train/test split in the CV split. Group leakage and time are
  the two classic failures.
- Simulate public/private: split your OOF into random 20/80 chunks many times
  and see how much rank order among your candidate submissions changes.
- Large CV↔LB gaps are a red flag, not a win. Investigate drift (adversarial
  validation), fold leakage, metric mismatch, or public set being tiny.
- Seed-average, use more folds, prefer rank-robust ensembles; pick final subs by
  CV, use the second slot as a hedge.

## What ML-engineering agents learned (MLE-STAR, CoMind, AIDE)

- Retrieve current SOTA models via search instead of defaulting to what the
  model "remembers" (AIDE lost by reaching for outdated ResNet/sklearn defaults).
- Ablate to find which pipeline block matters most, then refine only that block;
  avoid thrashing across stages.
- Leakage checker and data-usage checker (did we use every provided file?) are
  cheap and catch real failures.
- Community artifacts (discussions, kernels published before deadline) raise
  valid-submission and medal rates; highly upvoted ensemble kernels are noisy
  signals — extract the *ideas*, not the blend.
- Tiny validation sets give unstable feedback; raise fold count or repeat seeds.

## Kaggle CLI 2.x (July 2026)

Python ≥3.11, `uv tool install kaggle`. Auth: `kaggle auth login` (OAuth),
`KAGGLE_API_TOKEN` env var, `~/.kaggle/access_token`, or legacy
`~/.kaggle/kaggle.json`. Competition commands: list / files / download /
submit (`--wait`) / submissions / submission / leaderboard / topics.

## Sources

- NVIDIA, "Winning a Kaggle Competition with Generative AI–Assisted Coding" (2026) — https://developer.nvidia.com/blog/winning-a-kaggle-competition-with-generative-ai-assisted-coding/
- NVIDIA, "Grandmaster Pro Tip: Winning First Place with Stacking Using cuML" — https://developer.nvidia.com/blog/grandmaster-pro-tip-winning-first-place-in-a-kaggle-competition-with-stacking-using-cuml/
- NVIDIA, "Kaggle Grandmasters Unveil Winning Strategies" — https://developer.nvidia.com/blog/kaggle-grandmasters-unveil-winning-strategies-for-data-science-superpowers/
- Deotte, "1st Place - GPU Hill Climbing" (PS s5e5) — https://www.kaggle.com/competitions/playground-series-s5e5/writeups/chris-deotte-1st-place-gpu-hill-climbing
- Deotte, "1st Place - RAPIDS cuML Stack - 3 Levels" (PS s5e4) — https://www.kaggle.com/competitions/playground-series-s5e4/writeups/chris-deotte-1st-place-rapids-cuml-stack-3-levels
- PS s6e2 1st, "Diversity, Selection, and Trusting the CV–LB Relation" — https://www.kaggle.com/competitions/playground-series-s6e2/writeups/1st-place-solution-diversity-selection-and-t
- PS s5e12 1st, "Hill climbing + Ridge ensemble" — https://www.kaggle.com/competitions/playground-series-s5e12/writeups/1st-place-solution-hill-climbing-ridge-ensembl
- PS s6e5 8th, "L5 Ensemble" (TabPFN/TabICL/RealMLP/TabM mix) — https://www.kaggle.com/competitions/playground-series-s6e5/writeups/l5-ensemble
- TabArena leaderboard summary — https://www.codesota.com/tasks/tabular-ml
- "Tabular Data in 2026: Do GBDTs Still Beat Deep Learning?" — https://www.mlaia.com/blog-tabular-data-ml-vs-dl.html
- Kaggle Handbook: surviving a shake-up — https://medium.com/global-maksimum-data-information-technologies/kaggle-handbook-tips-tricks-to-survive-a-kaggle-shake-up-23675beed05e
- MLE-STAR (Google Research, NeurIPS 2025) — https://research.google/blog/mle-star-a-state-of-the-art-machine-learning-engineering-agents/
- CoMind: community-driven ML engineering agents — https://arxiv.org/html/2506.20640v2
- Kaggle solutions archive — https://kaggle.farid.one/
- Kaggle CLI docs — https://github.com/Kaggle/kaggle-cli/blob/main/docs/competitions.md
- hillclimbers module (reference implementation) — https://github.com/Matt-OP/hillclimbers
- Larger existing plugin, MIT, 34 skills + 9 agents + hooks, if you want more scaffolding — https://github.com/TranBaDat2607/claude-code-kaggle-grandmaster
