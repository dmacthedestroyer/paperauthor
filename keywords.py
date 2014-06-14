from collections import Counter
import itertools
import re
from unidecode import unidecode
import data

__common_stopwords = {'ON', 'AND', 'IN', 'OF', 'FOR', 'THE', 'FROM', 'WITH', 'BASED', 'USING'}
__paper_keyword_line_strip_regex = re.compile("KEY[S\"\s-]*(WORD|TERM)S?[:;.-]?")
__paper_keyword_split_regex = re.compile("[;|,]|\s-\s")
__general_keyword_split_regex = re.compile("[\W]")


def general_keyword_counter(strings):
    return Counter(itertools.chain.from_iterable(extract_general_keywords(s) for s in strings))


def extract_general_keywords(string):
    if string is None:
        return []

    return __split_string(__scrub_string(string), __general_keyword_split_regex)


def __scrub_string(string):
    return unidecode(string).upper().strip() if string is not None else ""


def __split_string(string, regex):
    if string is None:
        return []

    return (x.strip() for x in regex.split(string) if x is not None and len(x) > 2 and x not in __common_stopwords)


def extract_paper_keywords(string):
    if string is None:
        return []

    # to upper, replace accents, other general scrubbing stuff
    keywords = __scrub_string(string)
    # lots of entries begin with some variant of "Keywords: ", so strip that out.  And a lot of others end in a period
    keywords = re.sub(__paper_keyword_line_strip_regex, "", keywords).rstrip(".")
    # split on common separators (";", "|", ",", " - "), then get rid of any extra whitespace
    return __split_string(keywords, __paper_keyword_split_regex)


class KeywordRepository(object):
    def __init__(self):
        print("construct most common keywords:")
        print("\tbuilding author affiliation keywords")
        self.__affiliation_counter = self.__build_keywords(data.get_author_affiliations())
        print("\tbuilding conference full name keywords")
        self.__conference_fullname_counter = self.__build_keywords(data.get_conference_fullnames())
        print("\tbuilding journal full name keywords")
        self.__journal_fullname_counter = self.__build_keywords(data.get_journal_fullnames())
        print("\tbuilding paper title and keywords")
        self.__paper_title_counter = Counter()
        self.__paper_keyword_counter = Counter()
        for t, kw in data.get_paper_titles_and_keywords():
            if t:
                for tkw in extract_general_keywords(t):
                    self.__paper_title_counter[tkw] += 1
            if kw:
                for kwkw in extract_paper_keywords(kw):
                    self.__paper_keyword_counter[kwkw] += 1

    def most_common_affiliations(self, n=50):
        return self.__strip_most_common_keywords(self.__affiliation_counter.most_common(n))

    def most_common_paper_keywords(self, n=100):
        return self.__strip_most_common_keywords(self.__paper_keyword_counter.most_common(n))

    def most_common_paper_titles(self, n=50):
        return self.__strip_most_common_keywords(self.__paper_title_counter.most_common(n))

    def most_common_conference_fullnames(self, n=50):
        return self.__strip_most_common_keywords(self.__conference_fullname_counter.most_common(n))

    def most_common_journal_fullnames(self, n=50):
        return self.__strip_most_common_keywords(self.__journal_fullname_counter.most_common(n))

    @staticmethod
    def __strip_most_common_keywords(common_tuple):
        return [t[0] for t in common_tuple]

    @staticmethod
    def __build_keywords(keyword_iter):
        extracted_keywords = (extract_general_keywords(a) for a in keyword_iter)
        flattened = itertools.chain.from_iterable(extracted_keywords)
        return Counter(flattened)