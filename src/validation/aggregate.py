from pathlib import Path
from statistics import mean, pstdev
from collections import Counter

from ..ai import OcelEntity
from .validation import flatten_entity
from .metrics import precision, recall, f1_score


ASPECTS = ("objects", "object_attributes", "events", "o2o", "o2e")


def _prf(predicted: set, expected: set) -> dict:
    return {
        "precision": precision(predicted, expected),
        "recall":    recall(predicted, expected),
        "f1":        f1_score(predicted, expected),
    }


def cell_scores(runs: list[OcelEntity], truth: OcelEntity, k_vote: int | None = None) -> dict:
    """Score one (model, chunker, variant) cell against ground truth.

    Returns, per aspect, three views:
      - macro:  mean and population std of per-run P/R/F1 across the runs
      - micro:  P/R/F1 computed once over pooled tp/fp/fn counts
      - vote_kofn: P/R/F1 of the set of items appearing in >= k of n runs
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
        per_run = [_prf(f[a], expected) for f in flats]

        macro = {
            m: {
                "mean": mean(r[m] for r in per_run),
                "std":  pstdev(r[m] for r in per_run) if n > 1 else 0.0,
            }
            for m in ("precision", "recall", "f1")
        }

        tp = sum(len(f[a] & expected) for f in flats)
        fp = sum(len(f[a] - expected) for f in flats)
        fn = sum(len(expected - f[a]) for f in flats)
        p = tp / max(tp + fp, 1)
        r = tp / max(tp + fn, 1)
        micro = {
            "precision": p,
            "recall":    r,
            "f1":        2 * p * r / max(p + r, 1),
        }

        votes = Counter(item for f in flats for item in f[a])
        voted = {item for item, c in votes.items() if c >= k}
        vote = _prf(voted, expected)

        out[a] = {
            "macro": macro,
            "micro": micro,
            f"vote_{k}of{n}": vote,
        }
    return out


def per_run_scores(runs: list[OcelEntity], truth: OcelEntity) -> list[dict]:
    """One P/R/F1 row per (run, aspect) for a single cell."""
    exp = flatten_entity(truth)
    rows = []
    for i, r in enumerate(runs, start=1):
        f = flatten_entity(r)
        for a in ASPECTS:
            s = _prf(f[a], exp[a])
            rows.append({
                "run": i,
                "aspect": a,
                "precision": s["precision"],
                "recall":    s["recall"],
                "f1":        s["f1"],
            })
    return rows


def load_cell(
    model: str,
    chunker: str,
    variant: str,
    root: Path | str = Path("response_data"),
) -> list[OcelEntity]:
    """Load every response_*.json for one cell, sorted by filename."""
    base = Path(root) / model / chunker / variant
    files = sorted(base.glob("response_*.json"))
    return [OcelEntity.model_validate_json(p.read_text(encoding="utf-8")) for p in files]


def per_run_grid(
    cells: list[tuple[str, str, str]],
    truth: OcelEntity,
    root: Path | str = Path("response_data"),
) -> list[dict]:
    """Per-run P/R/F1 across all cells. One row per (model, chunker, variant, run, aspect)."""
    rows = []
    for model, chunker, variant in cells:
        runs = load_cell(model, chunker, variant, root=root)
        if not runs:
            continue
        for row in per_run_scores(runs, truth):
            rows.append({
                "model": model,
                "chunker": chunker,
                "variant": variant,
                **row,
            })
    return rows


def score_grid(
    cells: list[tuple[str, str, str]],
    truth: OcelEntity,
    root: Path | str = Path("response_data"),
    k_vote: int | None = None,
) -> list[dict]:
    """Run cell_scores for each (model, chunker, variant) and return flat rows
    keyed by (model, chunker, variant, aspect) — ready for DataFrame.from_records.
    Cells with no response files are skipped.
    """
    rows = []
    for model, chunker, variant in cells:
        runs = load_cell(model, chunker, variant, root=root)
        if not runs:
            continue
        scores = cell_scores(runs, truth, k_vote=k_vote)
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
