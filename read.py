from collections import Counter
import os
import pickle
import re
import itertools
from unidecode import unidecode

common_stopwords = {'ON', 'AND', 'IN', 'OF', 'FOR', 'THE', 'FROM', 'WITH', 'BASED', 'USING'}
paper_keyword_line_strip_regex = re.compile("KEY[S\"\s-]*(WORD|TERM)S?[:;.-]?")
paper_keyword_split_regex = re.compile("[;|,]|\s-\s")
general_keyword_split_regex = re.compile("[\W]")


def scrub_string(string):
    if string is None:
        return ""

    return unidecode(string).upper().strip()


def split_string(string, regex):
    if string is None:
        return []

    return (x.strip() for x in regex.split(string) if x is not None and len(x) > 2 and x not in common_stopwords)


def general_keyword_counter(strings):
    return Counter(itertools.chain.from_iterable(extract_general_keywords(s) for s in strings))

def extract_general_keywords(string):
    if string is None:
        return []

    return split_string(scrub_string(string), general_keyword_split_regex)


def extract_paper_keywords(string):
    if string is None:
        return []

    # to upper, replace accents, other general scrubbing stuff
    keywords = scrub_string(string)
    # lots of entries begin with some variant of "Keywords: ", so strip that out.  And a lot of others end in a period
    keywords = re.sub(paper_keyword_line_strip_regex, "", keywords).rstrip(".")
    # split on common separators (";", "|", ",", " - "), then get rid of any extra whitespace
    return split_string(keywords, paper_keyword_split_regex)


def unpickle_or_build(filename, factory, force_create=False):
    if force_create:
        try:
            os.remove(filename)
        except OSError:
            pass

    try:
        with open(filename, 'rb') as file:
            return pickle.load(file)
    except IOError:
        obj = factory()
        with open(filename, 'wb') as file:
            pickle.dump(obj, file)
        return obj
