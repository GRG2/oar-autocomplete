import parmenides
from os import cpu_count

INCLUDE_HEADER = True
INCLUDE_TITLE = False
DEFAULT_LANGUAGE = "en_core_web_sm"
NUM_WORKERS = cpu_count()
BATCH_SIZE = NUM_WORKERS
DETECT_LANGUAGE = False
TIME = True

from collections import defaultdict
from parmenides.conf import settings
from parmenides.write import Writer

import csv
try:
    import regex as re
except:
    import re

chars_to_remove = ['.', ',', ';', '!', '?', '[', ']', '{', '}']
chars_to_replace_with_space = ['_', '/', r'\s+', ':']


MAX_TERMS = 5

class my_writer(Writer):

    def __init__(self, output):

        fieldnames = [
            'TERM',
            'TERM_REDUCED',
            'PHRASE',
            'DOCUMENT',
        ] + settings.CSV_EXTRA_COLUMNS

        self.outfile = open(output, 'w', encoding=settings.ENCODING,
                newline='')
        self.writer = csv.DictWriter(self.outfile, delimiter=',',
                quotechar='"', quoting=csv.QUOTE_MINIMAL,
                fieldnames=fieldnames)

        if settings.INCLUDE_HEADER:
            self.writer.writeheader()

    def remove_unwanted(self, s):
        for c in chars_to_remove:
            s = re.sub(re.escape(c), '', s, ignore_unused=True)
        for c in chars_to_replace_with_space:
            s = re.sub(c, ' ', s, ignore_unused=True)
        return s

    def write(self, document, trees):

        collected_terms = {}
        
        for tree in trees:
            term = tree.term
            if term.representation in collected_terms:
                collected_terms[term.representation].phrases |= \
                    term.phrases
            else:
                term.sentence = str(tree)
                collected_terms[term.representation] = term

        for representation, term in collected_terms.items():
            if len(str(list(term.phrases)[0]).split()) > MAX_TERMS:
                continue
            row = {
                'TERM': representation,
                'TERM_REDUCED': " ".join(list(set(re.split(r':\d:', str(representation))))),
                'PHRASE': self.remove_unwanted(str(list(term.phrases)[0])),
                'DOCUMENT': document.identifier,
            }
            for column_name in settings.CSV_EXTRA_COLUMNS:
                row[column_name] = document.metadata.get(column_name)
            self.writer.writerow(row)


WRITER = my_writer