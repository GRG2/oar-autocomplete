import multiprocessing as mp
import json
from difflib import SequenceMatcher

try:
    import regex as re
except:
    import re



# https://stackoverflow.com/a/17388505 "Find the similarity metric between two strings"
# I figured this would be worth a shot instead of using cosine similarity
# Plus it uses a builtin Python library, which is good for cutting down on dependencies
# OPTIONAL: replace ratio() with quick_ratio() or real_quick_ratio() for a speed boost,
#   at the cost of accuracy (leads to worse auto suggestions)
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def match_terms(a, b, threshold):
    if len(a) == 0 or len(b) == 0:
        return 0
    matches = 0
    words_a = set(a.split())
    words_b = set(b.split())
    for word_a in words_a:
        for word_b in words_b:
            similarity = similar(word_a, word_b)
            matches += similarity
    return matches / max(len(words_a), len(words_b))


def search_helper(arguments):
    dataset, phrase, max_values, threshold = arguments
    similarity_matrix = {}
    for index, row in dataset.iterrows():
        comparison_terms = row["TERM_REDUCED"].lower().strip()
        comparison_terms = re.sub(r":\d:", " ", comparison_terms)
        comparison_phrase = row["PHRASE"].lower().strip()
        similarity = max(
            match_terms(phrase.lower(), comparison_terms, threshold),
            similar(phrase, comparison_phrase),
        )
        if comparison_phrase in similarity_matrix.keys():
            similarity_matrix[comparison_phrase] = max(
                similarity_matrix[comparison_phrase], similarity
            )
        else:
            similarity_matrix[comparison_phrase] = similarity

    sorted_similarity_matrix = sorted(
        similarity_matrix.items(), key=lambda item: item[1], reverse=True
    )

    return_values = sorted_similarity_matrix[:max_values]

    return_values = filter(lambda value: value[1] >= threshold, return_values)
    return(list(return_values))


def search_json(phrase, splits, p, max_values=10, threshold=0.5):
    rv = []

    return_values = p.map(search_helper, [(split, phrase, max_values, threshold) for split in splits])
    return_values = [item for sublist in return_values for item in sublist]

    return_values = sorted(return_values, key=lambda item: item[1], reverse=True)

    return_values_unique = []
    seen_values = set()

    for rv in return_values:
        if not rv[0] in seen_values:
            return_values_unique.append(rv)
            seen_values.add(rv[0])

    return_values = return_values_unique[:max_values]
    return json.dumps(return_values)
