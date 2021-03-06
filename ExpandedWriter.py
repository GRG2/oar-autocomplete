from parmenides.conf import settings
from parmenides.write import Writer

import csv
try:
    import regex as re
except:
    import re

chars_to_remove = ['.', ',', ';', '!', '?', '[', ']', '{', '}']
chars_to_replace_with_space = ['_', '/', r'\s+', ':']

MIN_FREQ = 1
MAX_TERMS = 5

class ExpandedWriter(Writer):

    def __init__(self, output):

        fieldnames = [
            'TERM',
            'TERM_REDUCED',
            'PHRASE',
            'DOCUMENT',
            'SECTION',
            'FREQ'
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
        freq = {}
        
        for tree in trees:
            term = tree.term
            term.section = tree.section
            if term.representation in collected_terms:
                collected_terms[term.representation].phrases |= \
                    term.phrases
            else:
                term.sentence = str(tree)
                collected_terms[term.representation] = term
            if term.representation in freq:
                freq[term.representation] += 1
            else:
                freq[term.representation] = 1
        
        for representation, term in collected_terms.items():
            if freq[representation] < MIN_FREQ:
                continue
            words = str(list(term.phrases)[0]).split()
            if len(words) > MAX_TERMS:
                continue
            skip = False
            for word in words:
                if word.isnumeric() or not word.isalnum:
                    skip = True
                    break
            if skip:
                continue
            
            row = {
                'TERM': str(representation).lower().strip(),
                'TERM_REDUCED': " ".join(list(set(re.split(r':\d:', str(representation))))).lower().strip(),
                'PHRASE': self.remove_unwanted(str(list(term.phrases)[0])).lower().strip(),
                'DOCUMENT': document.identifier,
                'SECTION': term.section,
                'FREQ': freq[representation]
            }
            for column_name in settings.CSV_EXTRA_COLUMNS:
                row[column_name] = document.metadata.get(column_name)
            self.writer.writerow(row)