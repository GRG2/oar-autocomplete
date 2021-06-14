import multiprocessing as mp
import pandas
import json
from difflib import SequenceMatcher
import os
try:
    import regex as re
except:
    import re

results = pandas.read_csv('parmenides_results.csv')
print("Results:", len(results))
splits = []
num_splits = max(os.cpu_count(), mp.cpu_count())
len_results = len(results)

for i in range(num_splits):
    start = int(i*len_results/num_splits)
    end = int((i+1)*len_results/num_splits)
    splits.append(results[start:end])

THRESHOLD = 0.3

# https://stackoverflow.com/a/17388505 "Find the similarity metric between two strings"
# I figured this would be worth a shot instead of using cosine similarity
# Plus it uses a builtin Python library, which is good for cutting down on dependencies
# OPTIONAL: replace ratio() with quick_ratio() or real_quick_ratio() for a speed boost,
#   at the cost of accuracy (leads to worse auto suggestions)
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def match_terms(a, b, threshold):
    if (len(a) == 0 or len(b) == 0):
        return 0
    matches = 0
    words_a = set(a.split())
    words_b = set(b.split())
    for word_a in words_a:
        for word_b in words_b:
            similarity = similar(word_a, word_b)
            matches += similarity
    return matches / max(len(words_a), len(words_b))

def search_helper(phrase, max_values, threshold, dataset, q):
    similarity_matrix = {}
    for index, row in dataset.iterrows():
        comparison_terms = row["TERM_REDUCED"].lower().strip()
        comparison_terms = re.sub(r':\d:', ' ', comparison_terms)
        comparison_phrase = row["PHRASE"].lower().strip()
        similarity = max(match_terms(phrase.lower(), comparison_terms, threshold), similar(phrase, comparison_phrase))
        if (comparison_phrase in similarity_matrix.keys()):
            similarity_matrix[comparison_phrase] = max(similarity_matrix[comparison_phrase], similarity)
        else:
            similarity_matrix[comparison_phrase] = similarity
    
    sorted_similarity_matrix = sorted(similarity_matrix.items(), key=lambda item: item[1], reverse=True)
        
    return_values = sorted_similarity_matrix[:max_values]

    return_values = filter(lambda value : value[1] >= threshold, return_values)
    q.put(list(return_values))

# def search_helper(phrase, max_values, threshold, dataset, q):
#     similarity_matrix = {}
#     for index, row in dataset.iterrows():
#         comparison_phrase = row["PHRASE"].lower().strip()
#         similarity = similar(phrase.lower(), comparison_phrase)
        
#         similarity_matrix[comparison_phrase] = similarity
    
#     sorted_similarity_matrix = sorted(similarity_matrix.items(), key=lambda item: item[1], reverse=True)
        
#     return_values = sorted_similarity_matrix[:max_values]

#     return_values = filter(lambda value : value[1] >= threshold, return_values)
#     q.put(list(return_values))

def search(phrase, max_values=10, threshold=THRESHOLD):
    rv = ""
    for line in search_helper(phrase, max_values, threshold):
        if (rv != ""):
            rv += "\n"
        if (len(line[0]) >= 67):
            rv += line[0][:63]
            rv += "..."
        else:
            rv += line[0]
    return rv

def search_json(phrase, max_values=10, threshold=THRESHOLD):
    rv = []
    processes = []
    q = mp.Queue()
    for dataset in splits:
        processes.append(mp.Process(target=search_helper, args=(phrase, max_values, threshold, dataset, q)))
    for p in processes:
        p.start()
    
    return_values = []

    for p in processes:
        p.join()
        return_values += q.get()
    
    return_values = sorted(return_values, key=lambda item: item[1], reverse=True)

    return_values_unique = []
    seen_values = set()

    for rv in return_values:
        if (not rv[0] in seen_values):
            return_values_unique.append(rv)
            seen_values.add(rv[0])

    return_values = return_values_unique[:max_values]
    return json.dumps(return_values)