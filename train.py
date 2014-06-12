from collections import Counter
import itertools
from sqlalchemy.orm import subqueryload, subqueryload_all
import keywords
from models import Author, PaperAuthor
import read
import settings

keyword_repository = keywords.get_or_create_keyword_repository()


def build_author_tuple(author, num_affiliation_keywords=50, num_paper_keywords=100, num_paper_title_keywords=100):
    # number of occurrences of common affiliation keywords
    author_affiliation_keyword_counts = Counter(read.extract_general_keywords(author.affiliation))
    for kw in keyword_repository.most_common_affiliation_keyword_counts(num_affiliation_keywords):
        yield author_affiliation_keyword_counts[kw]

    #number of papers by author
    yield len(author.authorpapers)

    papers = [ap.paper for ap in author.authorpapers] or []

    #number of occurrences of common paper keywords for this author
    foo = [read.extract_paper_keywords(p.keyword) for p in papers]
    bar = itertools.chain.from_iterable(foo)
    paper_keyword_counts = Counter(bar)
    for kw in keyword_repository.most_common_paper_keyword_counts(num_paper_keywords):
        yield paper_keyword_counts[kw]

    #number of cocurrences of common title keywords for this author
    paper_title_keyword_counts = Counter(itertools.chain.from_iterable(read.extract_general_keywords(p.title) for p in papers))
    for kw in keyword_repository.most_common_paper_title_counts(num_paper_title_keywords):
        yield paper_title_keyword_counts[kw]


if __name__ == "__main__":
    with settings.session_scope() as session:
        for a in session.query(Author).options(subqueryload_all(Author.authorpapers, PaperAuthor.paper)).order_by(Author.id)[:100]:
            print(list(build_author_tuple(a)))