"""Semantic counterpart to `aggregate.py`.

Same idea (macro / micro / k-of-n vote scoring per cell) but pair counts come
from embedding-based matching instead of exact set intersection.

Macro:   mean and population std of per-run P/R/F1 across the runs of a cell.
Micro:   pool tp/fp/fn counts across runs, then compute P/R/F1 once.
Vote:    union of names appearing in >= k of n runs, matched against truth.

The matching strategy is injected: pass
`embedding_based_matching._greedy_match` (greedy) as `match_fn`.

Skips `event_attributes` to stay consistent with `score_entity_semantic`.
"""

from pathlib import Path
from statistics import mean, pstdev
from collections import Counter
from typing import Callable

from ..ai import OcelEntity
from .validation import flatten_entity
from .embedding_based_matching import EmbeddingMatcher, _greedy_match


ASPECTS = ("objects", "object_attributes", "events", "o2o", "o2e")


# A match function takes (predicted, expected, matcher, category) and returns
# (matches, matched_predicted, matched_expected), where `matches` is a list of
# (similarity, predicted_name, expected_name) triples.
MatchFn = Callable[
    [set[str], set[str], EmbeddingMatcher, str],
    tuple[list[tuple[float, str, str]], set[str], set[str]],
]


def _prf(tp: int, fp: int, fn: int) -> dict:
    p = tp / max(tp + fp, 1)
    r = tp / max(tp + fn, 1)
    return {
        "precision": p,
        "recall": r,
        "f1": 2 * p * r / max(p + r, 1),
    }


def _count(
    predicted: set[str],
    expected: set[str],
    matcher: EmbeddingMatcher,
    category: str,
    match_fn: MatchFn,
) -> tuple[int, int, int]:
    """Return (tp, fp, fn) for one (predicted, expected) pair using
    semantic matching."""
    matches, _, _ = match_fn(predicted, expected, matcher, category)
    tp = len(matches)
    fp = len(predicted) - tp
    fn = len(expected) - tp
    return tp, fp, fn


def cell_scores_semantic(
    runs: list[OcelEntity],
    truth: OcelEntity,
    matcher: EmbeddingMatcher,
    match_fn: MatchFn = _greedy_match,
    k_vote: int | None = None,
) -> dict:
    """Score one (model, chunker, variant) cell against ground truth.

    Returns, per aspect:
      - macro:    mean and population std of per-run P/R/F1
      - micro:    P/R/F1 over pooled tp/fp/fn counts across runs
      - vote_kofn: P/R/F1 of names appearing in >= k of n runs
    """
    flats = [flatten_entity(r) for r in runs]
    exp = flatten_entity(truth)
    n = len(runs)
    if n == 0:
        return {}
    k = k_vote if k_vote is not None else (n // 2 + 1)

    out = {}
    for a in ASPECTS:
        expected = exp[a]

        # Per-run P/R/F1, then macro stats.
        per_run = []
        pooled_tp = pooled_fp = pooled_fn = 0
        for f in flats:
            tp, fp, fn = _count(f[a], expected, matcher, a, match_fn)
            per_run.append(_prf(tp, fp, fn))
            pooled_tp += tp
            pooled_fp += fp
            pooled_fn += fn

        macro = {
            m: {
                "mean": mean(r[m] for r in per_run),
                "std": pstdev(r[m] for r in per_run) if n > 1 else 0.0,
            }
            for m in ("precision", "recall", "f1")
        }

        micro = _prf(pooled_tp, pooled_fp, pooled_fn)

        votes = Counter(item for f in flats for item in f[a])
        voted = {item for item, c in votes.items() if c >= k}
        v_tp, v_fp, v_fn = _count(voted, expected, matcher, a, match_fn)
        vote = _prf(v_tp, v_fp, v_fn)

        out[a] = {
            "macro": macro,
            "micro": micro,
            f"vote_{k}of{n}": vote,
        }
    return out


def per_run_scores_semantic(
    runs: list[OcelEntity],
    truth: OcelEntity,
    matcher: EmbeddingMatcher,
    match_fn: MatchFn = _greedy_match,
) -> list[dict]:
    """One P/R/F1 row per (run, aspect) for a single cell."""
    exp = flatten_entity(truth)
    rows = []
    for i, r in enumerate(runs, start=1):
        f = flatten_entity(r)
        for a in ASPECTS:
            tp, fp, fn = _count(f[a], exp[a], matcher, a, match_fn)
            s = _prf(tp, fp, fn)
            rows.append({
                "run": i,
                "aspect": a,
                "precision": s["precision"],
                "recall": s["recall"],
                "f1": s["f1"],
            })
    return rows


def load_cell(
    model: str,
    chunker: str,
    variant: str,
    root: Path | str = Path("response_data"),
) -> list[OcelEntity]:
    base = Path(root) / model / chunker / variant
    files = sorted(base.glob("response_*.json"))
    return [OcelEntity.model_validate_json(p.read_text(encoding="utf-8")) for p in files]


def per_run_grid_semantic(
    cells: list[tuple[str, str, str]],
    truth: OcelEntity,
    matcher: EmbeddingMatcher,
    match_fn: MatchFn = _greedy_match,
    root: Path | str = Path("response_data"),
) -> list[dict]:
    """Per-run P/R/F1 across all cells. One row per (model, chunker, variant, run, aspect)."""
    rows = []
    for model, chunker, variant in cells:
        runs = load_cell(model, chunker, variant, root=root)
        if not runs:
            continue
        for row in per_run_scores_semantic(runs, truth, matcher, match_fn):
            rows.append({
                "model": model,
                "chunker": chunker,
                "variant": variant,
                **row,
            })
    return rows


def score_grid_semantic(
    cells: list[tuple[str, str, str]],
    truth: OcelEntity,
    matcher: EmbeddingMatcher,
    match_fn: MatchFn = _greedy_match,
    root: Path | str = Path("response_data"),
    k_vote: int | None = None,
) -> list[dict]:
    """One flat row per (model, chunker, variant, aspect) carrying
    macro / micro / vote scores. Ready for DataFrame.from_records."""
    rows = []
    for model, chunker, variant in cells:
        runs = load_cell(model, chunker, variant, root=root)
        if not runs:
            continue
        scores = cell_scores_semantic(runs, truth, matcher, match_fn, k_vote=k_vote)
        n = len(runs)
        k = k_vote if k_vote is not None else (n // 2 + 1)
        vote_key = f"vote_{k}of{n}"
        for aspect in ASPECTS:
            s = scores[aspect]
            rows.append({
                "model": model,
                "chunker": chunker,
                "variant": variant,
                "aspect": aspect,
                "runs": n,
                "macro_precision":    s["macro"]["precision"]["mean"],
                "macro_precision_sd": s["macro"]["precision"]["std"],
                "macro_recall":       s["macro"]["recall"]["mean"],
                "macro_recall_sd":    s["macro"]["recall"]["std"],
                "macro_f1":           s["macro"]["f1"]["mean"],
                "macro_f1_sd":        s["macro"]["f1"]["std"],
                "micro_precision":    s["micro"]["precision"],
                "micro_recall":       s["micro"]["recall"],
                "micro_f1":           s["micro"]["f1"],
                "vote_precision":     s[vote_key]["precision"],
                "vote_recall":        s[vote_key]["recall"],
                "vote_f1":            s[vote_key]["f1"],
                "vote_threshold":     f"{k}/{n}",
            })
    return rows
