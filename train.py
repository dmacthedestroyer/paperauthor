from collections import Counter
import itertools
import data
import keywords
import models
import read
import settings


def __build_author_tuple(aet, affiliation_keywords, paper_keywords, paper_title_keywords,
                         conference_fullname_keywords, journal_fullname_keywords):
    assert len(aet.author) == 1

    yield len(aet.paper)
    years = [p.year for p in aet.paper if p.year > 0]
    yield min(years) if any(years) else 0
    yield sum(years) / float(len(years)) if any(years) else 0
    yield max(years) if any(years) else 0
    yield len(aet.conference)
    yield len(aet.journal)
    author_affiliation_keyword_counts = read.general_keyword_counter(a.affiliation for a in aet.author)
    for kw in affiliation_keywords:
        yield author_affiliation_keyword_counts[kw]

    for f in __build_common_tuple(aet, paper_keywords, paper_title_keywords, conference_fullname_keywords, journal_fullname_keywords):
        yield f


def __build_paper_tuple(aet, paper_keywords, paper_title_keywords, conference_fullname_keywords, journal_fullname_keywords):
    assert len(aet.paper) == 1

    for p in aet.paper:
        yield p.year
    yield len(aet.author)
    for f in __build_common_tuple(aet, paper_keywords, paper_title_keywords, conference_fullname_keywords, journal_fullname_keywords):
        yield f


def __build_paperauthor_tuple(aet, affiliation_keywords):
    assert len(aet.paperauthor) == 1

    paperauthor_affiliation_counts = read.general_keyword_counter(pa.affiliation for pa in aet.paperauthor)
    for kw in affiliation_keywords:
        yield paperauthor_affiliation_counts[kw]


def __build_common_tuple(aet, paper_keywords, paper_title_keywords,
                         conference_fullname_keywords, journal_fullname_keywords):
    paper_keyword_counts = Counter(itertools.chain.from_iterable(read.extract_paper_keywords(p.keyword) for p in aet.paper))
    for kw in paper_keywords:
        yield paper_keyword_counts[kw]
    title_keyword_counts = read.general_keyword_counter(p.title for p in aet.paper)
    for kw in paper_title_keywords:
        yield title_keyword_counts[kw]
    conference_fullname_keyword_counts = read.general_keyword_counter(c.fullname for c in aet.conference)
    for kw in conference_fullname_keywords:
        yield conference_fullname_keyword_counts[kw]
    journal_fullname_keyword_counts = read.general_keyword_counter(j.fullname for j in aet.journal)
    for kw in journal_fullname_keywords:
        yield journal_fullname_keyword_counts[kw]


def __build_classification_tuples(expanded_tuples, num_affiliation_keywords=50, num_paper_keywords=100,
                                  num_paper_title_keywords=50, num_conference_fullname_keywords=50,
                                  num_journal_fullname_keywords=50):
    keyword_repository = keywords.KeywordRepository()

    aac = keyword_repository.most_common_affiliations(num_affiliation_keywords)
    pkc = keyword_repository.most_common_paper_keywords(num_paper_keywords)
    ptc = keyword_repository.most_common_paper_titles(num_paper_title_keywords)
    cfc = keyword_repository.most_common_conference_fullnames(num_conference_fullname_keywords)
    jfc = keyword_repository.most_common_journal_fullnames(num_journal_fullname_keywords)

    a = {g[0].id: list(__build_author_tuple(g[1], aac, pkc, ptc, cfc, jfc)) for g in models.group_expanded_tuples(expanded_tuples, lambda e: e.author)}
    p = {g[0].id: list(__build_paper_tuple(g[1], pkc, ptc, cfc, jfc)) for g in models.group_expanded_tuples(expanded_tuples, lambda e: e.paper)}
    pa = {(g[0].paperid, g[0].authorid): list(__build_paperauthor_tuple(g[1], aac)) for g in models.group_expanded_tuples(expanded_tuples, lambda e: e.paperauthor)}

    for k in pa:
        yield list(itertools.chain(a[k[1]], p[k[0]], pa[k]))

if __name__ == "__main__":
    print("read training tuples")
    training_tuples = data.get_train_tuples()
    print("build classification tuples")
    classification_tuples = list(__build_classification_tuples(training_tuples))
    print("print shit out")
    print("total tuples: {0}".format(len(classification_tuples)))
    longest_list = None
    for l in classification_tuples:
        nonzero = [i for i in l if i > 0]
        if longest_list is None or len(longest_list) < len(nonzero):
            longest_list = nonzero
            print("new longest classification tuple: {0} non-zero items".format(len(nonzero)))
            print(l)