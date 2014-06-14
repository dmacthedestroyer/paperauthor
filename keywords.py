from collections import Counter
import itertools
import os
import pickle
import data
import read
import settings


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
                for tkw in read.extract_general_keywords(t):
                    self.__paper_title_counter[tkw] += 1
            if kw:
                for kwkw in read.extract_paper_keywords(kw):
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
        extracted_keywords = (read.extract_general_keywords(a) for a in keyword_iter)
        flattened = itertools.chain.from_iterable(extracted_keywords)
        return Counter(flattened)


def get_or_create_keyword_repository(data_model_path=settings.MODEL_PATH + "\keyword_counts.pickle", force_create=False):
    return read.unpickle_or_build(data_model_path, KeywordRepository, force_create=force_create)


if __name__ == "__main__":
    model = get_or_create_keyword_repository(force_create=False)