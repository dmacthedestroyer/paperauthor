import csv
from collections import Counter
import pprint
import re
import itertools
from unidecode import unidecode

common_stopwords = set(['ON', 'AND', 'CONFERENCE', 'INTERNATIONAL', 'WORKSHOP', 'SYSTEMS', 'IN', 'OF', 'FOR', 'THE',
                       'JOURNAL', 'RESEARCH', 'REVIEW', 'UNIVERSITY', 'DEPARTMENT', 'INSTITUTE', 'SCIENCE', 'DE',
                       'NATIONAL', 'LABORATORY', 'SCHOOL'])
paper_keyword_line_strip_regex = re.compile("KEY[S\"\s-]*(WORD|TERM)S{0,1}[:;.-]{0,1}")
paper_keyword_split_regex = re.compile("[;|,]|\s-\s")
general_keyword_split_regex = re.compile("[\W]")


def read_csv(file_name, max_rows=None):
    rows_read = 0
    with open(file_name, "r", encoding="utf8") as file:
        for r in csv.DictReader(file):
            if max_rows is not None and rows_read >= max_rows:
                break
            yield r
            rows_read += 1


def scrub_string(string):
    return unidecode(string).upper().strip()


def split_string(string, regex):
    return (x.strip() for x in regex.split(string) if x is not None and len(x) > 2 and x not in common_stopwords)


def extract_general_keywords(string):
    return split_string(scrub_string(string), general_keyword_split_regex)


def extract_paper_keywords(string):
    # to upper, replace accents, other general scrubbing stuff
    keywords = scrub_string(string)
    # lots of entries begin with some variant of "Keywords: ", so strip that out.  And a lot of others end in a period
    keywords = re.sub(paper_keyword_line_strip_regex, "", keywords).rstrip(".")
    # split on common separators (";", "|", ",", " - "), then get rid of any extra whitespace
    return split_string(keywords, paper_keyword_split_regex)
