from collections import Counter
import itertools
import os
import pickle
from sqlalchemy import or_
from models import Author, Conference, Journal, Paper
import read
import settings


class KeywordRepository(object):
    def __init__(self):
        print("building author affiliation keywords")
        self.affiliation_counter = self.__build_keywords(Author.affiliation)
        print("building conference full name keywords")
        self.conference_fullname_counter = self.__build_keywords(Conference.fullname)
        print("building journal full name keywords")
        self.journal_fullname_counter = self.__build_keywords(Journal.fullname)
        print("building paper title and keywords")
        self.paper_title_counter = Counter()
        self.paper_keyword_counter = Counter()
        with settings.session_scope() as session:
            for t, kw in session.query(Paper.title, Paper.keyword).filter(or_(Paper.title != "", Paper.keyword != "")):
                if t is not None:
                    for tkw in read.extract_general_keywords(t):
                        self.paper_title_counter[tkw] += 1
                if kw is not None:
                    for kwkw in read.extract_paper_keywords(kw):
                        self.paper_keyword_counter[kwkw] += 1


    def __build_keywords(self, db_column, keyword_extraction_func=read.extract_general_keywords):
        with settings.session_scope() as session:
            keyword_list = (kt[0] for kt in session.query(db_column).filter(db_column != ""))
            extracted_keywords = (keyword_extraction_func(a) for a in keyword_list)
            flattened = itertools.chain.from_iterable(extracted_keywords)
            return Counter(flattened)


def get_or_create_keyword_repository(data_model_path=settings.MODEL_PATH + "\keyword_counts.pickle", force_create=False):
    if force_create:
        try:
            os.remove(data_model_path)
            print("original data model file deleted")
        except OSError:
            pass

    try:
        with open(data_model_path, 'rb') as file:
            print("found data model at {0}".format(data_model_path))
            return pickle.load(file)
    except IOError:
        print("no file found at {0}, creating new data model from database".format(data_model_path))
        data_model = KeywordRepository()
        print("saving data model at location: {0}".format(data_model_path))
        with open(data_model_path, 'wb') as file:
            pickle.dump(data_model, file)
        return data_model


if __name__ == "__main__":
    model = get_or_create_keyword_repository()