from ..ai import OcelEntity
from .metrics import precision, recall, f1_score

from typing import TypedDict

FlatEntity = TypedDict("FlatEntity", {
    "objects": set[str],
    "object_attributes": set[str],
    "events": set[str],
    "event_attributes": set[str],
    "o2o": set[str],
    "o2e": set[str],
})

def flatten_entity(entity: OcelEntity) -> FlatEntity:
    flat_entity = FlatEntity(
        objects={obj.name for obj in entity.objs}, 
        object_attributes={": ".join([obj.name, attr.name]) for obj in entity.objs for attr in obj.attributes}, 
        events={evt.name for evt in entity.evts}, 
        event_attributes={": ".join([evt.name, attr.name]) for evt in entity.evts for attr in evt.attributes}, 
        # relations={" <-> ".join(sorted([rel.a, rel.b])) for rel in [*entity.o2e, *entity.o2o]}
        o2o={" <-> ".join(sorted([rel.a, rel.b])) for rel in entity.o2o},
        o2e={" <-> ".join(sorted([rel.a, rel.b])) for rel in entity.o2e}
    )
    return flat_entity



def score_entity(entity: OcelEntity, reference: OcelEntity) -> dict[str, float]:
    results = []
    predicted = flatten_entity(entity)
    expected = flatten_entity(reference)
    results = {
        key: {
            "precision": precision(predicted[key], expected[key]),
            "recall": recall(predicted[key], expected[key]),
            "f1": f1_score(predicted[key], expected[key]),
        }
        for key in predicted.keys()
    }
    return results

def score_batch(entities: list[OcelEntity], reference: OcelEntity) -> dict[str, float]:
    """calculates precision, recall and f1 score of a given batch of OcelEntities. Uses macro f1 approach."""
    scores = {}
    avg_precision = 0
    avg_recall = 0
    avg_f1 = 0
    n = len(entities)

    for i, e in enumerate(entities):
        score = score_entity(e, reference)
        scores.setdefault(f"Entity {i}", score)

        avg_precision += sum([score[key]["precision"] for key in score.keys()]) / max(n * 5, 1)
        avg_recall += sum([score[key]["recall"] for key in score.keys()]) / max(n * 5, 1)
        avg_f1 += sum([score[key]["f1"] for key in score.keys()]) / max(n * 5, 1)

    scores.setdefault("Average", {"precision": avg_precision, "recall": avg_recall, "f1": avg_f1})
    return scores


def flatten_batch_score(data: dict) -> list[tuple]:
    flat_data = [
        (
            entity.split(" ")[-1],
            aspect,
            scores["precision"],
            scores["recall"],
            scores["f1"]
        )
        for entity, entries in data.items()
        for aspect, scores in entries.items()
        if entity != "Average"
    ]
    return flat_data
