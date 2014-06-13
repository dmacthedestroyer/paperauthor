from collections import Counter
import itertools
import data
import keywords
import read


def __build_author_tuple(at, affiliation_keywords, paper_keywords, paper_title_keywords,
                         conference_fullname_keywords, journal_fullname_keywords):
    # number of occurrences of common affiliation keywords
    author_affiliation_keyword_counts = Counter(read.extract_general_keywords(at.author.affiliation))
    for kw in affiliation_keywords:
        yield author_affiliation_keyword_counts[kw]

    # number of papers by author
    yield len(at.papers)

    #number of occurrences of common paper keywords for this author
    paper_keyword_counts = Counter(itertools.chain.from_iterable(read.extract_paper_keywords(p.keyword) for p in at.papers))
    for kw in paper_keywords:
        yield paper_keyword_counts[kw]

    #number of occurrences of common title keywords for this author
    paper_title_keyword_counts = read.general_keyword_counter(p.title for p in at.papers)
    for kw in paper_title_keywords:
        yield paper_title_keyword_counts[kw]

    #number of conferences by author
    yield len(set(c.id for c in at.conferences))

    #number of occurrences of common conference fullname keywords
    conference_fullname_keyword_counts = read.general_keyword_counter(c.fullname for c in at.conferences)
    for kw in conference_fullname_keywords:
        yield conference_fullname_keyword_counts[kw]

    #number of journals
    yield len(set(j.id for j in at.journals))

    #number of occurrences of common journal fullname keywords
    journal_fullname_keyword_counts = read.general_keyword_counter(j.fullname for j in at.journals)
    for kw in journal_fullname_keywords:
        yield journal_fullname_keyword_counts[kw]


def __build_paper_tuple(pt, paper_keywords, paper_title_keywords,
                        conference_fullname_keywords, journal_fullname_keywords):
    yield pt.year

    paper_keyword_counts = Counter(read.extract_paper_keywords(pt.paper.keyword))
    for kw in paper_keywords:
        yield paper_keyword_counts[kw]

    title_keyword_counts = Counter(read.extract_general_keywords(pt.paper.title))
    for kw in paper_title_keywords:
        yield title_keyword_counts[kw]

    conference_fullname_keyword_counts = read.general_keyword_counter(c.fullname for c in at.conferences)
    for kw in conference_fullname_keywords:
        yield conference_fullname_keyword_counts[kw]

    journal_fullname_keyword_counts = read.general_keyword_counter(j.fullname for j in at.journals)
    for kw in journal_fullname_keywords:
        yield journal_fullname_keyword_counts[kw]

    yield len(pt.paperauthors)


if __name__ == "__main__":
    keyword_repository = keywords.get_or_create_keyword_repository(force_create=False)

    aac = keyword_repository.most_common_affiliations(50)
    pkc = keyword_repository.most_common_paper_keywords(100)
    ptc = keyword_repository.most_common_paper_titles(50)
    cfc = keyword_repository.most_common_conference_fullnames(50)
    jfc = keyword_repository.most_common_journal_fullnames(50)
    author_tuples = dict()

    longest_list = []
    for batch in itertools.zip_longest(*[iter(range(1, 2300000))] * 500): #[[2563, 8695, 19946, 26537, 32227]]:
        for t in (__build_author_tuple(at, aac, pkc, ptc, cfc, jfc) for at in
                  data.get_author_training_tuples(list(batch))):
            nonzeroes = [i for i in t if i > 0]
            if len(nonzeroes) > len(longest_list):
                longest_list = nonzeroes
        print("current longest tuple: {0} items".format(len(longest_list)))
        print(longest_list)
    pass