"""Driver: produce semantic macro / micro / per-run CSVs across every
(model, chunker, prompt_variant) cell under `response_data/`.

Mirrors the exact-match aggregator in `src/validation/aggregate.py` but uses
embedding-based pair scoring.

Outputs in `results/semantic_aggregated/`:
    - aggregate.csv  one row per (model, chunker, variant, aspect):
                     macro_precision/_sd, macro_recall/_sd, macro_f1/_sd,
                     micro_precision/_recall/_f1, vote_precision/_recall/_f1,
                     vote_threshold
    - per_run.csv    one row per (model, chunker, variant, run, aspect):
                     precision, recall, f1
    - macro_pivot.csv  wide view: macro_f1 with (model, chunker, aspect) as
                     rows and prompt variant as columns — the headline table.

Run from the top directory:
    uv run python evaluate_semantic_aggregated.py
"""

import csv
from pathlib import Path

from ground_truth import truth
from src.validation.embedding_based_matching import EmbeddingMatcher, _greedy_match
from src.validation.aggregate_semantic import (
    score_grid_semantic,
    per_run_grid_semantic,
)


RESPONSE_ROOT = Path("response_data")
OUTPUT_ROOT = Path("results") / "semantic_aggregated_threshold085_OpenAI_embedding_3_small"
THRESHOLD = 0.85
SKIP_DIRS = {"Results_prompt_text_old"}

# `_greedy_match` from embedding_based_matching.
MATCH_FN = _greedy_match

def discover_cells(root: Path) -> list[tuple[str, str, str]]:
    """Walk `response_data/` and return every leaf (model, chunker, variant)
    that contains at least one response_*.json file."""
    cells: list[tuple[str, str, str]] = []
    for model_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        if model_dir.name in SKIP_DIRS:
            continue
        for chunker_dir in sorted(p for p in model_dir.iterdir() if p.is_dir()):
            for variant_dir in sorted(p for p in chunker_dir.iterdir() if p.is_dir()):
                if any(variant_dir.glob("response_*.json")):
                    cells.append((model_dir.name, chunker_dir.name, variant_dir.name))
    return cells


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        print(f"  no rows for {path.name}, skipping")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow({
                k: (round(v, 4) if isinstance(v, float) else v)
                for k, v in row.items()
            })
    print(f"Wrote {path}")


def main():
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    matcher = EmbeddingMatcher(threshold=THRESHOLD)

    cells = discover_cells(RESPONSE_ROOT)
    print(f"Discovered {len(cells)} cells under {RESPONSE_ROOT}")

    print("Computing aggregate (macro / micro / vote) grid...")
    agg_rows = score_grid_semantic(
        cells, truth, matcher, match_fn=MATCH_FN, root=RESPONSE_ROOT,
    )
    _write_csv(OUTPUT_ROOT / "aggregate.csv", agg_rows)

    print("Computing per-run grid...")
    per_run_rows = per_run_grid_semantic(
        cells, truth, matcher, match_fn=MATCH_FN, root=RESPONSE_ROOT,
    )
    _write_csv(OUTPUT_ROOT / "per_run.csv", per_run_rows)

    # Headline pivot: macro_f1 with (model, chunker, aspect) on rows and the
    # prompt variant on columns. Built by hand (no pandas dependency needed
    # here) so it stays a stable, sorted CSV.
    if agg_rows:
        from collections import OrderedDict
        variants = sorted({r["variant"] for r in agg_rows})
        pivot: dict[tuple, dict] = OrderedDict()
        for r in agg_rows:
            row_key = (r["model"], r["chunker"], r["aspect"])
            pivot.setdefault(row_key, {})[r["variant"]] = r["macro_f1"]
        pivot_path = OUTPUT_ROOT / "macro_pivot.csv"
        with pivot_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["model", "chunker", "aspect", *variants])
            for (model, chunker, aspect) in sorted(pivot.keys()):
                row = [model, chunker, aspect]
                for v in variants:
                    cell = pivot[(model, chunker, aspect)].get(v)
                    row.append("" if cell is None else round(cell, 4))
                writer.writerow(row)
        print(f"Wrote {pivot_path}")

    # Headline preview at the terminal: top 10 cells by mean macro F1 across
    # aspects, just to confirm the run looks sane.
    if agg_rows:
        from collections import defaultdict
        agg_by_cell: dict[tuple, list[float]] = defaultdict(list)
        for r in agg_rows:
            agg_by_cell[(r["model"], r["chunker"], r["variant"])].append(r["macro_f1"])
        ranked = sorted(
            (
                (sum(v) / len(v), k)
                for k, v in agg_by_cell.items()
            ),
            reverse=True,
        )
        print("\nTop cells by mean macro_f1 across aspects:")
        for f1, (model, chunker, variant) in ranked[:10]:
            print(f"  {f1:.3f}  {model}/{chunker}/{variant}")


if __name__ == "__main__":
    main()
