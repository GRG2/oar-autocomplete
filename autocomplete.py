import json
from difflib import SequenceMatcher

# In case the better regex library is not available, use the standard library regex
try:
    import regex as re
except:
    import re


"""
https://stackoverflow.com/a/17388505 "Find the similarity metric between two strings"
OPTIONAL: replace ratio() with quick_ratio() or real_quick_ratio() for a speed boost,
at the cost of accuracy (leads to worse auto suggestions).
returns: floating point number between 0 and 1
"""


def similar(a, b):
    if (not b.startswith(a[:len(a)//2+1])) or len(b) < len(a):
        return 0
    
    return SequenceMatcher(None, a, b).ratio()


"""
Finds the number of matching terms (fractional number, meaning partial matches
give a value less than 1).
Matches of less than threshold are ignored from the calculation entirely.
This prevents matches over 100% (values greater than 1).
returns: floating point number between 0 and 1
"""


def match_terms(a, b, threshold):
    matches = 0
    firstword = a.split()[0]
    firstword_match = False
    for word_b in b.split():
        if similar(firstword, word_b) >= threshold:
            firstword_match = True
    if not firstword_match:
        return 0
    words_a = set(a.split())  # Using sets to remove duplicate words
    words_b = set(b.split())
    for word_a in words_a:
        best = 0
        for word_b in words_b:
            similarity = similar(word_a, word_b)
            best = max(best, similarity)
        if best > threshold:
            matches += 1
    return matches / max(len(words_a), len(words_b))


"""
Used in the process pool to analyze segments of the CSV data (see splits[] in server.py).
arguments is a tuple, which is unpacked on the first line. The reason for using a tuple is
that arguments are not able to be passed to a processing pool. This is a workaround.
returns: a 2D list of strings and floating point numbers between 0 and 1
"""


def search_helper(arguments):
    dataset, phrase, max_values, threshold = arguments

    # Similarity matrix keeps track of the best matches for the search phrase
    similarity_matrix = {}

    for index, row in dataset.iterrows():
        # First, clean up both the terms and the phrase
        comparison_terms = row["TERM_REDUCED"]
        comparison_phrase = row["PHRASE"]
        # Then, find the highest similarity between the search phrase and the comparison data
        # (match_terms for analyzing terms like keywords, and similar for matching whole phrases)
        # similarity = max(
        #     match_terms(phrase, comparison_terms, threshold),
        #     match_terms(phrase, comparison_phrase, threshold)
        # )
        similarity = match_terms(phrase, comparison_terms, threshold)
        
        if (
            not comparison_terms in similarity_matrix.keys()
        ) or similarity > similarity_matrix[comparison_terms]["similarity"]:

            similarity_matrix[comparison_terms] = {
                "similarity": similarity,
                "data": dict(row),
                "rank": (similarity ** 2) * row["FREQ"],
            }

    # Sort the similarity matrix from highest to lowest
    similarity_matrix = sorted(
        similarity_matrix.items(), key=lambda item: item[1]["rank"], reverse=True
    )

    # Filter out matches below the threshold, then return only the number of values we want
    return_values = list(
        filter(lambda value: value[1]["similarity"] >= threshold, similarity_matrix)
    )
    return_values = return_values[:max_values]

    return list(return_values)


"""
Boilerplate code which handles splitting the search between processes in the processing pool.
returns: JSON formatted 2D list of strings and floating point numbers between 0 and 1
"""


def search_json(phrase, splits, p, max_values=10, threshold=0.5):
    if len(phrase) == 0:
        return json.dumps([])

    rv = []

    return_values = p.map(
        search_helper, [(split, phrase, max_values, threshold) for split in splits]
    )
    return_values = [item for sublist in return_values for item in sublist]

    return_values = sorted(
        return_values, key=lambda item: item[1]["rank"], reverse=True
    )

    return_values_unique = []
    seen_values = set()

    for rv in return_values:
        if not rv[0] in seen_values:
            return_values_unique.append(rv)
            seen_values.add(rv[0])

    return_values = return_values_unique[:max_values]

    return_values_reordered = []
    for rv in return_values:
        words_a = phrase.split()
        words_b = set(rv[1]["data"]["TERM_REDUCED"].split())
        for word_a in words_a:
            if word_a in words_b:
                words_b.remove(word_a)
        return_values_reordered.append((" ".join(words_a + list(words_b)), rv[1]))
    
    # return_values = sorted(return_values, key=lambda item: item[1]["data"]["FREQ"], reverse=True)

    return json.dumps(return_values_reordered)
    # print(return_values)
    # return json.dumps(return_values)
