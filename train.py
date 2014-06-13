from collections import Counter
import itertools
from sqlalchemy.orm import subqueryload, subqueryload_all
import keywords
from models import Author, PaperAuthor, Paper
import read
import settings


def __build_author_tuple(author, affiliation_counter, paper_keyword_counter, paper_title_counter,
                         conference_fullname_counter, journal_fullname_counter):
    # number of occurrences of common affiliation keywords
    author_affiliation_keyword_counts = Counter(read.extract_general_keywords(author.affiliation))
    for kw in affiliation_counter:
        yield author_affiliation_keyword_counts[kw]

    #number of papers by author
    yield len(author.authorpapers)

    papers = [ap.paper for ap in author.authorpapers if ap.paper is not None]

    #number of occurrences of common paper keywords for this author
    paper_keyword_counts = Counter(itertools.chain.from_iterable(read.extract_paper_keywords(p.keyword) for p in papers))
    for kw in paper_keyword_counter:
        yield paper_keyword_counts[kw]

    #number of occurrences of common title keywords for this author
    paper_title_keyword_counts = read.general_keyword_counter(p.title for p in papers)
    for kw in paper_title_counter:
        yield paper_title_keyword_counts[kw]

    conferences = [p.conference for p in papers if p.conference is not None]
    #number of conferences by author
    yield len(set(c.id for c in conferences))

    #number of occurrences of common conference fullname keywords
    conference_fullname_keyword_counts = read.general_keyword_counter(c.fullname for c in conferences)
    for kw in conference_fullname_counter:
        yield conference_fullname_keyword_counts[kw]

    #number of journals
    journals = [p.journal for p in papers if p.journal is not None]
    yield len(set(j.id for j in journals))

    #number of occurrences of common journal fullname keywords
    journal_fullname_keyword_counts = read.general_keyword_counter(j.fullname for j in journals)
    for kw in journal_fullname_counter:
        yield journal_fullname_keyword_counts[kw]


def __build_paper_tuple(paper, paper_keyword_counter, paper_title_counter,
                        conference_fullname_counter, journal_fullname_counter):
    yield paper.year

    paper_keywords = Counter(read.extract_paper_keywords(paper.keyword))
    for kw in paper_keyword_counter:
        yield paper_keywords[kw]

    title_keywords = Counter(read.extract_general_keywords(paper.title))
    for kw in paper_title_counter:
        yield title_keywords[kw]

    conference_fullname_keywords = Counter()
    if paper.conference is not None:
        conference_fullname_keywords = Counter(read.extract_general_keywords(paper.conference.fullname))
    for kw in conference_fullname_counter:
        yield conference_fullname_keywords[kw]

    jounal_fullname_keywords = Counter()
    if paper.journal is not None:
        jounal_fullname_keywords = Counter(read.extract_general_keywords(paper.journal.fullname))
    for kw in journal_fullname_counter:
        yield jounal_fullname_keywords[kw]

    yield len(paper.paperauthors)

if __name__ == "__main__":
    keyword_repository = keywords.get_or_create_keyword_repository()

    aac = keyword_repository.affiliation_counter.most_common(50)
    pkc = keyword_repository.paper_keyword_counter.most_common(100)
    ptc = keyword_repository.paper_title_counter.most_common(50)
    cfc = keyword_repository.conference_fullname_counter.most_common(50)
    jfc = keyword_repository.journal_fullname_counter.most_common(50)
    author_tuples = dict()
    with settings.session_scope() as session:
        for a in session.query(Author).options(subqueryload_all(Author.authorpapers, PaperAuthor.paper))[:100]:
            author_tuples[a.id] = list(__build_author_tuple(a, aac, pkc, ptc, cfc, jfc))
        for p in session.query(Paper).options(subqueryload_all(Paper.paperauthors))[:100]:
            print(list(__build_paper_tuple(p, pkc, ptc, cfc, jfc)))
    pass