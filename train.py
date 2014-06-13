from collections import Counter
import itertools
import data
import keywords
from models import Author, Paper
import read


def __build_author_tuple(tt, affiliation_keywords, paper_keywords, paper_title_keywords,
                         conference_fullname_keywords, journal_fullname_keywords):
    author_affiliation_keyword_counts = read.general_keyword_counter(a.affiliation for a in tt.authors)
    assert len(tt.authors) == 1
    yield len(tt.papers)
    years = [p.year for p in tt.papers if p.year > 0]
    yield min(years)
    yield sum(years) / float(len(years))
    yield max(years)
    yield len(tt.conferences)
    yield len(tt.journals)
    for kw in affiliation_keywords:
        yield author_affiliation_keyword_counts[kw]
    for f in __build_common_tuple(tt, paper_keywords, paper_title_keywords, conference_fullname_keywords, journal_fullname_keywords):
        yield f


def __build_paper_tuple(tt, paper_keywords, paper_title_keywords, conference_fullname_keywords, journal_fullname_keywords):
    assert len(tt.papers) == 1
    for p in tt.papers:
        yield p.year
    yield len(tt.authors)
    for f in __build_common_tuple(tt, paper_keywords, paper_title_keywords, conference_fullname_keywords, journal_fullname_keywords):
        yield f


def __build_common_tuple(tt, paper_keywords, paper_title_keywords,
                         conference_fullname_keywords, journal_fullname_keywords):
    paper_keyword_counts = Counter(itertools.chain.from_iterable(read.extract_paper_keywords(p.keyword) for p in tt.papers))
    for kw in paper_keywords:
        yield paper_keyword_counts[kw]
    title_keyword_counts = read.general_keyword_counter(p.title for p in tt.papers)
    for kw in paper_title_keywords:
        yield title_keyword_counts[kw]
    conference_fullname_keyword_counts = read.general_keyword_counter(c.fullname for c in tt.conferences)
    for kw in conference_fullname_keywords:
        yield conference_fullname_keyword_counts[kw]
    journal_fullname_keyword_counts = read.general_keyword_counter(j.fullname for j in tt.journals)
    for kw in journal_fullname_keywords:
        yield journal_fullname_keyword_counts[kw]


if __name__ == "__main__":
    keyword_repository = keywords.get_or_create_keyword_repository(force_create=False)

    aac = keyword_repository.most_common_affiliations(50)
    pkc = keyword_repository.most_common_paper_keywords(100)
    ptc = keyword_repository.most_common_paper_titles(50)
    cfc = keyword_repository.most_common_conference_fullnames(50)
    jfc = keyword_repository.most_common_journal_fullnames(50)

    print("build training data")
    training_data = {(t[0:2]): t[2] for t in data.read_training_ids()}
    print("build author tuples")
    author_tuples = list(data.get_training_tuples([k[0] for k in training_data.keys()], Author))
    print("build paper tuples")
    paper_tuples = list(data.get_training_tuples([k[1] for k in training_data.keys()], Paper))
