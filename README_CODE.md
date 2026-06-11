# coco_paper_2026_final_code

Final pipeline for the paper *"Extracting Object-Centric Process Mining (OCEL)
entities from compliance documentation with LLMs."*

The workflow is three steps:

1. **`main.py`** — query the LLMs and save the extracted OCEL entities as JSON
   under `response_data/`.
2. **`evaluate_exact.py`** — score those responses against the hand-annotated
   ground truth using **exact (string-equality) matching**.
3. **`evaluate_semantic_aggregated.py`** — score the same responses using
   **embedding-based semantic matching** (two names match if their embeddings
   are similar enough).

---

## Setup

The project uses [`uv`](https://docs.astral.sh/uv/) with `pyproject.toml`
(Python ≥ 3.13).

```bash
# from this directory
uv sync
```

### Credentials (`.env`)

All model and embedding credentials are read from a `.env` file in this
directory. Each logical model needs three variables, named with the model's
uppercased prefix (`-`/space → `_`):

```dotenv
# Chat models used by main.py (one block per model in main.py's sweep)
GPT_5.5_MODEL_NAME=...
GPT_5.5_API_KEY=...
GPT_5.5_BASE_URL=...

GPT_5_NANO_MODEL_NAME=...
GPT_5_NANO_API_KEY=...
GPT_5_NANO_BASE_URL=...

CLAUDE_OPUS_4_6_MODEL_NAME=...
CLAUDE_OPUS_4_6_API_KEY=...
CLAUDE_OPUS_4_6_BASE_URL=...

CLAUDE_HAIKU_4_5_MODEL_NAME=...
CLAUDE_HAIKU_4_5_API_KEY=...
CLAUDE_HAIKU_4_5_BASE_URL=...

# Embedding model used by evaluate_semantic_aggregated.py
EMBEDDING_MODEL_NAME=text-embedding-3-small
EMBEDDING_API_KEY=...
EMBEDDING_BASE_URL=...
```

Names containing `GPT` route to `ChatOpenAI`; everything else routes to
`ChatAnthropic` (see `src/ai.py:AiWorker`). The embedding client uses
`OpenAIEmbeddings` (see `src/validation/embedding_based_matching.py`).

> All commands below assume the project's `uv` environment. If you have a
> different `VIRTUAL_ENV` active, add `--active`, e.g.
> `uv run --active python main.py`.

---

## 1. Generate response data — `main.py`

`main.py` runs a full sweep of experiment settings. Each setting is an
`ExperimentSetting(model, prompt_variants, chunker)`; the script
iterates over the cross-product of:

- **Models:** `gpt-5.5`, `claude-opus-4-6`, `gpt-5-nano`, `claude-haiku-4-5`
- **Chunkers:** `non_chunker`, `section_chunker`
- **Prompt variants:** `naive`, `improved_naive`(`_ocel`), `algorithmic`(`_ocel`),
  `improved_algorithmic`(`_ocel`), and the two-step `improved_naive_cascading`
  (a list of `[step_1, step_2]` is run as a cascade — step 1's output is fed
  into step 2).

Each cell is run **5 times** (`runs=5`) against the input
document `section_text.txt`.

```bash
uv run python main.py
```

### Output

```
response_data/<model>/<chunker>/<prompt_variant>/response_<i>.json
```

Each `response_<i>.json` is a Pydantic-validated `OcelEntity` with `objs`,
`evts`, `o2o`, `o2e` lists (objects carry `attributes`). `<i>` runs
1..5.

> **Note:** files are overwritten in place. To re-run only part of the sweep,
> edit/trim the settings tuple in `main.py`. Generating all cells issues many
> LLM calls — expect cost and runtime.

---

## 2. Exact-matching results — `evaluate_exact.py`

Loads every `response_*.json` cell, flattens each into name sets
(`objects`, `object_attributes`, `events`, `o2o`, `o2e`),
and scores them against the ground truth in `ground_truth.py` using exact
string equality. Reports three views per cell/aspect:

- **macro** — mean ± population std of per-run precision/recall/F1
- **micro** — P/R/F1 pooled over all runs' TP/FP/FN
- **vote** — P/R/F1 of items appearing in a majority of runs (k-of-n)

```bash
# print all three tables to the terminal
uv run python evaluate_exact.py

# also save CSVs (any subset of these flags)
uv run python evaluate_exact.py \
  --runs-csv exact_per_run.csv \
  --agg-csv exact_aggregated.csv \
  --macro-csv exact_matching_macro.csv
```

### Flags / output

| Flag | Content |
|---|---|
| `--runs-csv`  | one row per (model, chunker, variant, run, aspect): precision, recall, f1 |
| `--agg-csv`   | one row per (model, chunker, variant, aspect): macro/micro/vote scores |
| `--macro-csv` | wide pivot — macro precision/recall/F1 with (model, chunker, aspect) on rows and prompt variant as columns |

The set of cells scored is defined by the `cells` list near the top of
`evaluate_exact.py`; adjust it if you change the sweep in `main.py`.

---

## 3. Semantic-matching results — `evaluate_semantic_aggregated.py`

Mirrors the exact-match aggregator but matches names by **embedding cosine
similarity** instead of string equality (default threshold **0.85**, greedy
1-to-1 matching). It auto-discovers every leaf cell under `response_data/` that
contains `response_*.json` files — no `cells` list to maintain.

```bash
uv run python evaluate_semantic_aggregated.py
```

### Configuration (edit constants at the top of the file)

- `THRESHOLD` — minimum cosine for two names to count as a match (default `0.85`).
- `OUTPUT_ROOT` — output directory (default
  `results/semantic_aggregated_threshold085_OpenAI_embedding_3_small`).
- `MATCH_FN` — `_greedy_match` from
  `src/validation/embedding_based_matching.py`.
- `SKIP_DIRS` — model dirs to ignore during discovery.

### Output (under `OUTPUT_ROOT`)

| File | Content |
|---|---|
| `aggregate.csv`  | one row per (model, chunker, variant, aspect): macro (mean/sd), micro, vote scores |
| `per_run.csv`    | one row per (model, chunker, variant, run, aspect): precision, recall, f1 |
| `macro_pivot.csv`| headline pivot — macro_f1 with (model, chunker, aspect) on rows and prompt variant as columns |

The script also prints the top 10 cells by mean macro F1 to the terminal as a
sanity check.

> This step calls the embedding API once per unique string (results are cached
> within a run). Make sure the `EMBEDDING_*` variables in `.env` are set.

---

## Repository layout (this folder)

| Path | Purpose |
|---|---|
| `main.py` | experiment sweep / response generation |
| `evaluate_exact.py` | exact-match scoring + CSVs |
| `evaluate_semantic_aggregated.py` | embedding-based scoring + CSVs |
| `ground_truth.py` | hand-annotated `truth` OcelEntity |
| `section_text.txt` | input document section fed to the LLM |
| `src/ai.py` | Pydantic OCEL schemas + `AiWorker` (model routing) |
| `src/experiment.py` | `run_experiment`, `load_experiment`, `ExperimentSetting` |
| `src/data_import.py` | chunkers (`non_chunker`, `section_chunker`, …) |
| `src/prompt.py`, `src/prompt_text.py` | prompt variants + formatting |
| `src/validation/` | exact + semantic scoring (`aggregate*.py`, `embedding_based_matching.py`, `metrics.py`, `validation.py`) |
| `response_data/` | generated LLM responses |
| `results/` | generated evaluation CSVs |
