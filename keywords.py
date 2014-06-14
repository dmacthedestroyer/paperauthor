from collections import Counter
import itertools
import re
from unidecode import unidecode
import data

# exclude the following stopwords from being considered keywords
__common_stopwords = {'ON', 'AND', 'IN', 'OF', 'FOR', 'THE', 'FROM', 'WITH', 'BASED', 'USING'}
# a simple regex to strip any leading "KEYWORDS:"-style nonsense from paper keyword attributes
__paper_keyword_line_strip_regex = re.compile("KEY[S\"\s-]*(WORD|TERM)S?[:;.-]?")
# paper keywords are separated by ";", "|", ",", and " - ", so we'll split on that
__paper_keyword_split_regex = re.compile("[;|,]|\s-\s")
# names, titles, and other stuff like that, we'll just split on whitespace
__general_keyword_split_regex = re.compile("[\W]")


def general_keyword_counter(strings):
    """
    Cleans, splits, flattens and returns a Counter for the specified collection of unprocessed strings for general
    keyword extraction
    :param strings: a collection of strings which will individually get split, then flattened into a single list
    :return: a Counter object for the processed strings
    """
    return Counter(itertools.chain.from_iterable(extract_general_keywords(s) for s in strings))


def extract_general_keywords(string):
    """
    Cleans and splits a single string object into a list of keywords
    :param string:
    :return:
    """
    if string is None:
        return []

    return __split_string(__scrub_string(string), __general_keyword_split_regex)


def __scrub_string(string):
    """
    Unaccent, upper-case and remove extra whitespace for a given string
    :param string:
    :return:
    """
    return unidecode(string).upper().strip() if string is not None else ""


def __split_string(string, regex):
    """
    Splits a string and removes common stop words
    :param string:
    :param regex:
    :return: a generator function fetching each word from the provided string
    """
    if string is None:
        return []

    return (x.strip() for x in regex.split(string) if x is not None and len(x) > 2 and x not in __common_stopwords)


def extract_paper_keywords(string):
    """
    Scrubs and splits a given string within the context of a paper keyword
    :param string:
    :return:
    """
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
        self.affiliation_keywords = self.__build_keywords(data.get_author_affiliations())
        print("\tbuilding conference full name keywords")
        self.conference_fullname_keywords = self.__build_keywords(data.get_conference_fullnames())
        print("\tbuilding journal full name keywords")
        self.journal_fullname_keywords = self.__build_keywords(data.get_journal_fullnames())
        print("\tbuilding paper title and keywords")
        __paper_title_counter = Counter()
        __paper_keyword_counter = Counter()
        for t, kw in data.get_paper_titles_and_keywords():
            if t:
                for tkw in extract_general_keywords(t):
                    __paper_title_counter[tkw] += 1
            if kw:
                for kwkw in extract_paper_keywords(kw):
                    __paper_keyword_counter[kwkw] += 1
        self.paper_title_keywords = [t[0] for t in __paper_title_counter.most_common(100)]
        self.paper_keywords = [t[0] for t in __paper_keyword_counter.most_common(100)]

    @staticmethod
    def __build_keywords(keyword_iter, n=100):
        extracted_keywords = (extract_general_keywords(a) for a in keyword_iter)
        flattened = itertools.chain.from_iterable(extracted_keywords)
        return [t[0] for t in Counter(flattened).most_common(n)]