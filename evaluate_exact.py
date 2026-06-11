from ground_truth import truth
from pandas import DataFrame
import argparse
import src.validation as val

# --------------------------------------------------------- #
# Evaluate saved responses against ground truth.
# --------------------------------------------------------- #


parser = argparse.ArgumentParser()
parser.add_argument(
    "--macro-csv",
    help="Path to save the macro precision/recall/F1 pivot table as CSV.",
)
parser.add_argument(
    "--agg-csv",
    help="Path to save the aggregated per-cell scores as CSV.",
)
parser.add_argument(
    "--runs-csv",
    help="Path to save the per-run scores as CSV.",
)
args = parser.parse_args()


cells = [
    (model, chunker, variant)
    for model in ("gpt-5.5", "claude-opus-4-6", "gpt-5-nano", "claude-haiku-4-5")
    for chunker in ("non_chunker", "section_chunker")
    for variant in (
        "naive",
        "improved_naive",
        "algorithmic",
        "improved_algorithmic",
        "improved_naive_cascading_step_2",
    )
]


# Per-run P/R/F1 — one row per (model, chunker, variant, run, aspect)
runs_df = DataFrame.from_records(val.per_run_grid(cells, truth))
print("=== Per-run scores ===")
print(runs_df.round(3).to_string(index=False))


# Aggregated scores per cell — macro (mean ± std over runs), micro (pooled), majority vote
agg_df = DataFrame.from_records(val.score_grid(cells, truth))
print("\n=== Aggregated scores ===")
print(agg_df.round(3).to_string(index=False))


# Headline view: macro precision / recall / F1 by (model, chunker, aspect) × variant
print("\n=== Macro precision / recall / F1 pivot ===")
print(
    agg_df.pivot_table(
        index=["model", "chunker", "aspect"],
        columns="variant",
        values=["macro_f1"],
    ).round(3)
)


if args.runs_csv:
    runs_df.round(3).to_csv(args.runs_csv, index=False)
    print(f"Wrote per-run scores to {args.runs_csv}")

if args.agg_csv:
    agg_df.round(3).to_csv(args.agg_csv, index=False)
    print(f"Wrote aggregated scores to {args.agg_csv}")

    

def save_macro_pivot(agg_df: DataFrame, path: str) -> None:
    """Write the macro precision/recall/F1 pivot to ``path`` as CSV."""
    pivot = agg_df.pivot_table(
        index=["model", "chunker", "aspect"],
        columns="variant",
        values=["macro_precision", "macro_recall", "macro_f1"],
    ).round(3)
    # Flatten the (metric, variant) column MultiIndex and the row index into a
    # single header row so the CSV is one clean line of field names.
    pivot.columns = [f"{metric}__{variant}" for metric, variant in pivot.columns]
    pivot = pivot.reset_index()
    pivot.to_csv(path, index=False)
    print(f"Wrote macro pivot to {path}")

# --------------------------------------------------------- #

if args.macro_csv:
    save_macro_pivot(agg_df, args.macro_csv)


