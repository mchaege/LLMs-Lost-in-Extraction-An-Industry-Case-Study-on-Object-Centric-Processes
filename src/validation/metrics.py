import math


# -------------------------------------------------------------------------------- #

# obsolete due to new approach
def dot_product(v1, v2):
    return sum(x * y for x, y in zip(v1, v2))

# obsolete due to new approach
def magnitude(v):
    return math.sqrt(dot_product(v, v))

# obsolete due to new approach
def cosine_similarity(vec_1: list[float], vec_2: list[float]) -> float:
    if magnitude(vec_1) == 0 or magnitude(vec_2) == 0:
        return 0.0
    return dot_product(vec_1, vec_2) / (magnitude(vec_1) * magnitude(vec_2))

# obsolete due to new approach
def euclidian_distance(vec_1: list[float], vec_2: list[float]) -> float:
    assert(len(vec_1) == len(vec_2))
    distance = 0
    for i in range(len(vec_1)):
        distance += (vec_1[i] - vec_2[i]) ** 2
    
    return distance ** 0.5

def true_positive(predicted: set, expected: set) -> float:
    return len(expected & predicted)

def false_positive(predicted: set, expected: set) -> float:
    return len(predicted - expected)

def false_negative(predicted: set, expected: set) -> float:
    return len(expected - predicted)

def precision(predicted: set, expected: set) -> float:
    tp = true_positive(predicted=predicted, expected=expected)
    fp = false_positive(predicted=predicted, expected=expected)
    return tp / max(tp + fp, 1)

def recall(predicted: set, expected: set) -> float:
    tp = true_positive(predicted=predicted, expected=expected)
    fn = false_negative(predicted=predicted, expected=expected)
    return tp / max(tp + fn, 1)

def f1_score(predicted: set, expected: set) -> float:
    prs = precision(predicted=predicted, expected=expected)
    rec = recall(predicted=predicted, expected=expected)
    return 2 * (prs * rec) / max(prs + rec, 1)
