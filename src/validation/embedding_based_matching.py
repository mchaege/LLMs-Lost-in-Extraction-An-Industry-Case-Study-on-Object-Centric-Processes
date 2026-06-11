"""Embedding-based semantic matching of OCEL entities against a ground truth.

The exact-match scorer in `validation.py` says `"acknowledge_doc"` and
`"acknowledge_document"` are different. This module relaxes that: two names
count as the same thing if their text embeddings are similar enough.

How a single comparison works:
    1. Both predicted and expected names are flattened into category sets
       (objects, events, relations, attributes) via `flatten_entity`.
    2. Inside a category, every (predicted, expected) pair gets a similarity
       score. Structured names (events, relations, attributes) are split into
       parts FIRST so a shared substring can't inflate the score; each part is
       embedded individually and the pair score is the MIN across parts.
    3. Pairs above the threshold are matched 1-to-1, greedily by descending
       similarity. Matched pairs = true positives; from there precision,
       recall, and F1 are the usual formulas.

Configuration: reads `EMBEDDING_MODEL_NAME`, `EMBEDDING_API_KEY`, and
`EMBEDDING_BASE_URL` from `.env` (same pattern as `AiWorker`).
"""

import os
import math
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from pydantic import SecretStr

from ..ai import OcelEntity
from .core import FlatEntity
from .validation import flatten_entity


load_dotenv()


def _cosine(v1: list[float], v2: list[float]) -> float:
    """Cosine similarity in [-1, 1]: 1 means same direction, 0 means orthogonal.

    For embeddings of natural-language strings, values >~ 0.8 usually mean the
    two strings refer to closely related concepts.
    """
    dot = sum(x * y for x, y in zip(v1, v2))
    m1 = math.sqrt(sum(x * x for x in v1))
    m2 = math.sqrt(sum(x * x for x in v2))
    if m1 == 0 or m2 == 0:
        return 0.0
    return dot / (m1 * m2)


class EmbeddingMatcher:
    """Wraps the embedding model and caches one vector per unique string.

    The cache matters: evaluating many runs against the same ground truth
    re-uses the same set of strings hundreds of times. Without the cache we
    would re-pay an API call for every comparison.

    Args:
        threshold: minimum cosine for two names to be considered a match.
            0.85 is a sane default for short OCEL-style names *after*
            structural decomposition. Lower it if real synonyms get rejected,
            raise it if topically-related but distinct concepts get matched.
        model_env_prefix: prefix of the env vars the embedding client reads
            credentials from.
    """

    def __init__(self, threshold: float = 0.85, model_env_prefix: str = "EMBEDDING"):
        self.threshold = threshold
        self.client = OpenAIEmbeddings(
            model=os.getenv(f"{model_env_prefix}_MODEL_NAME"),
            api_key=SecretStr(os.getenv(f"{model_env_prefix}_API_KEY")),
            base_url=os.getenv(f"{model_env_prefix}_BASE_URL"),
        )
        # self.client = HuggingFaceEmbeddings(
        #     model_name="sentence-transformers/all-MiniLM-L6-v2",
        #     model_kwargs={"device": "cpu"},          # or "cuda"
        #     encode_kwargs={"normalize_embeddings": False},
        # )
        self._cache: dict[str, list[float]] = {}

    def embed(self, names: list[str]) -> dict[str, list[float]]:
        """Return vectors for `names`, calling the API only for ones not yet
        cached. Batching everything missing into one request keeps the cost
        roughly proportional to the number of *unique* strings ever seen."""
        missing = [n for n in set(names) if n and n not in self._cache]
        if missing:
            vectors = self.client.embed_documents(missing)
            for n, v in zip(missing, vectors):
                self._cache[n] = v
        return {n: self._cache[n] for n in names if n}


# --------------------------------------------------------------------------- #
# Structural decomposition of flattened names.
#
# The names produced by `flatten_entity` carry internal structure that gets
# washed out if we embed the whole string at once. Example:
#
#   "assign_authorization <-> user"  vs  "assign_authorization <-> authorization"
#
# Embedded as full strings these look ~92% similar because the left endpoint
# is identical, masking that the right endpoint is a completely different
# object. We fix this by splitting names along their structural separators,
# embedding the atomic parts, and taking the MIN of per-part cosines as the
# pair score — a single mismatched part is enough to reject the pair.
# --------------------------------------------------------------------------- #


def _atomic_sim(a: str, b: str, matcher: "EmbeddingMatcher") -> float:
    """Similarity of two leaf strings. Lazily embeds anything not in cache,
    so the fallback paths in the other sim helpers can't KeyError on a string
    that wasn't pre-batched."""
    if a == b:
        return 1.0
    missing = [n for n in (a, b) if n not in matcher._cache]
    if missing:
        matcher.embed(missing)
    return _cosine(matcher._cache[a], matcher._cache[b])


def _event_sim(a: str, b: str, matcher: "EmbeddingMatcher") -> float:
    """Compare two event names of the form `verb_noun_phrase`.

    Splits on the first underscore so that the verb is compared against the
    verb and the noun-phrase against the noun-phrase, then takes the min.
    This is what kills false positives like `create_change_proposal` vs
    `implement_change_proposal` — the verbs differ, so the min cosine drops
    even though the noun phrase is identical.
    """
    pa = a.split("_", 1)
    pb = b.split("_", 1)
    if len(pa) != len(pb):
        return _atomic_sim(a, b, matcher)
    return min(_atomic_sim(pa[i], pb[i], matcher) for i in range(len(pa)))


def _endpoint_sim(a: str, b: str, matcher: "EmbeddingMatcher") -> float:
    """A relation endpoint is either an object (`document`) or an event
    (`create_document`). Use the event splitter only if both sides actually
    have a verb_noun shape."""
    if "_" in a and "_" in b:
        return _event_sim(a, b, matcher)
    return _atomic_sim(a, b, matcher)


def _relation_sim(a: str, b: str, matcher: "EmbeddingMatcher") -> float:
    """Compare two relations of the form `endpoint_a <-> endpoint_b`.

    Endpoints are pre-sorted alphabetically by `flatten_entity`, so position
    is meaningful: we match left-to-left and right-to-right. Pair score is
    the min of the two endpoint similarities, so a wrong endpoint sinks the
    whole match.
    """
    pa = a.split(" <-> ")
    pb = b.split(" <-> ")
    if len(pa) != 2 or len(pb) != 2:
        return _atomic_sim(a, b, matcher)
    return min(
        _endpoint_sim(pa[0], pb[0], matcher),
        _endpoint_sim(pa[1], pb[1], matcher),
    )


def _attribute_sim(a: str, b: str, matcher: "EmbeddingMatcher") -> float:
    """Compare two attributes of the form `owner: attr_name`. The owner can
    be event-shaped (`create_document: actor`), so it gets the endpoint
    treatment; the attribute name itself is treated as a leaf."""
    pa = a.split(": ", 1)
    pb = b.split(": ", 1)
    if len(pa) != 2 or len(pb) != 2:
        return _atomic_sim(a, b, matcher)
    return min(
        _endpoint_sim(pa[0], pb[0], matcher),
        _atomic_sim(pa[1], pb[1], matcher),
    )


# Picks the right per-pair similarity function for each FlatEntity category.
_SIM_BY_CATEGORY = {
    "objects": _atomic_sim,
    "events": _event_sim,
    "relations": _relation_sim,
    "o2o": _relation_sim,
    "o2e": _relation_sim,
    "object_attributes": _attribute_sim,
    "event_attributes": _attribute_sim,
}


def _collect_tokens(name: str, category: str) -> set[str]:
    """Return every atomic substring of `name` that needs an embedding.

    Used to pre-batch all required API calls before scoring begins, which
    is much faster than embedding strings lazily one-at-a-time inside the
    O(|predicted| × |expected|) pair loop.
    """
    if category == "objects":
        return {name}
    if category == "events":
        return set(name.split("_", 1)) if "_" in name else {name}
    if category in ("relations", "o2o", "o2e"):
        tokens: set[str] = set()
        endpoints = name.split(" <-> ") if " <-> " in name else [name]
        for ep in endpoints:
            tokens.update(ep.split("_", 1) if "_" in ep else [ep])
        return tokens
    if category in ("object_attributes", "event_attributes"):
        parts = name.split(": ", 1) if ": " in name else [name]
        tokens = set(parts[0].split("_", 1) if "_" in parts[0] else [parts[0]])
        if len(parts) > 1:
            tokens.add(parts[1])
        return tokens
    return {name}


def _greedy_match(
    predicted: set[str],
    expected: set[str],
    matcher: EmbeddingMatcher,
    category: str,
) -> tuple[list[tuple[float, str, str]], set[str], set[str]]:
    """Match predicted names to expected names, 1-to-1, greedily.

    Steps:
        1. Collect every atomic substring on both sides and embed them all in
           one batched API call.
        2. Score every (predicted, expected) pair using the category's sim
           function. Drop anything below `matcher.threshold`.
        3. Sort surviving pairs by descending similarity; walk the list and
           lock in each pair whose two sides are both still unmatched.

    Greedy assignment prevents one ground-truth name from "absorbing"
    multiple predictions (e.g. three slightly different paraphrases all
    matching the same truth entry would otherwise count as three TPs).

    Returns:
        (matches, matched_predicted, matched_expected) where `matches` is the
        list of locked-in (score, predicted, expected) triples in descending
        score order, and the two sets are the predicted/expected sides that
        appear in `matches`.
    """
    if not predicted or not expected:
        return [], set(), set()

    tokens: set[str] = set()
    for n in predicted | expected:
        tokens.update(_collect_tokens(n, category))
    matcher.embed(list(tokens))

    sim_fn = _SIM_BY_CATEGORY.get(category, _atomic_sim)

    pairs = []
    for p in predicted:
        for e in expected:
            sim = sim_fn(p, e, matcher)
            if sim >= matcher.threshold:
                pairs.append((sim, p, e))

    pairs.sort(reverse=True)
    matches: list[tuple[float, str, str]] = []
    used_p: set[str] = set()
    used_e: set[str] = set()
    for sim, p, e in pairs:
        if p in used_p or e in used_e:
            continue
        used_p.add(p)
        used_e.add(e)
        matches.append((sim, p, e))

    return matches, used_p, used_e


def _scores(
    predicted: set[str],
    expected: set[str],
    matcher: EmbeddingMatcher,
    category: str,
) -> dict:
    """Score one category of one run.

    Returns precision / recall / F1 plus the full match list and the
    unmatched names on both sides — the extra fields let a human inspect
    *why* the score came out the way it did.

    Output keys:
        precision, recall, f1     — the usual scalars
        matches                   — [{predicted, expected, similarity}, ...]
        false_positives           — predicted names with no acceptable match
        false_negatives           — expected names with no acceptable match
    """
    matches, used_p, used_e = _greedy_match(predicted, expected, matcher, category)
    tp = len(matches)
    fp = len(predicted) - tp
    fn = len(expected) - tp
    prec = tp / max(tp + fp, 1)
    rec = tp / max(tp + fn, 1)
    f1 = 2 * (prec * rec) / max(prec + rec, 1)
    return {
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "matches": [
            {"predicted": p, "expected": e, "similarity": round(sim, 4)}
            for sim, p, e in matches
        ],
        "false_positives": sorted(predicted - used_p),
        "false_negatives": sorted(expected - used_e),
    }


def score_entity_semantic(
    entity: OcelEntity,
    reference: OcelEntity,
    matcher: EmbeddingMatcher,
) -> dict[str, dict[str, float]]:
    """Semantic counterpart to `validation.score_entity`.

    Returns a dict keyed by category (`objects`, `events`, `relations`,
    `object_attributes`) with precision/recall/F1 for each. The
    `event_attributes` category is excluded — see the project notes.
    """
    predicted: FlatEntity = flatten_entity(entity)
    expected: FlatEntity = flatten_entity(reference)
    return {
        key: _scores(predicted[key], expected[key], matcher, key)
        for key in predicted.keys()
        if key != "event_attributes"
    }


def score_batch_semantic(
    entities: list[OcelEntity],
    reference: OcelEntity,
    matcher: EmbeddingMatcher,
) -> dict[str, dict[str, float]]:
    """Score a batch of runs against the same ground truth.

    A batch is the N response files for one `(model, chunker, prompt_variant)`
    configuration. We compute per-entity scores and a macro-average where
    every run and every category contribute equally.

    Returned dict layout:
        {
            "Entity 0": {category: {precision, recall, f1}, ...},
            "Entity 1": {...},
            ...,
            "Average": {precision, recall, f1},
        }
    """
    scores: dict[str, dict[str, float]] = {}
    n = len(entities)
    avg_precision = 0.0
    avg_recall = 0.0
    avg_f1 = 0.0

    for i, e in enumerate(entities):
        score = score_entity_semantic(e, reference, matcher)
        scores[f"Entity {i}"] = score
        n_categories = len(score)
        avg_precision += sum(score[k]["precision"] for k in score) / max(n * n_categories, 1)
        avg_recall += sum(score[k]["recall"] for k in score) / max(n * n_categories, 1)
        avg_f1 += sum(score[k]["f1"] for k in score) / max(n * n_categories, 1)

    scores["Average"] = {"precision": avg_precision, "recall": avg_recall, "f1": avg_f1}
    return scores
