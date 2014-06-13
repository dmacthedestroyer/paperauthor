import psycopg2
from models import Author, Paper, PaperAuthor, Conference, Journal, AuthorTraining
import settings


def __execute_sql(sql, params=None):
    cursor = psycopg2.connect(settings.POSTGRESQL_CONNECTION_STRING).cursor()
    cursor.execute(sql, params)
    return cursor


def __read_all_fullnames(tablename):
    return __execute_sql("select fullname from {0} where fullname is not null".format(tablename))


def get_journal_fullnames():
    return (r[0] for r in __read_all_fullnames("journal"))


def get_conference_fullnames():
    return (r[0] for r in __read_all_fullnames("conference"))


def get_author_affiliations():
    return (r[0] for r in __execute_sql("select affiliation from author where affiliation is not null"))


def get_paper_titles_and_keywords():
    return __execute_sql("select title, keyword from paper where length(title) > 0 or length(keyword) > 0")

def get_author_training_tuples(author_ids):
    sql = """
select a.id, a.name, a.affiliation,
  pa.paperid, pa.authorid, pa.name, pa.affiliation,
  p.id, p.title, p.year, p.keyword,
  c.id, c.shortname, c.fullname,
  j.id, j.shortname, j.fullname
from author a
  left join paperauthor pa on a.id = pa.authorid
  left join paper p on pa.paperid = p.id
  left join conference c on p.conferenceid = c.id
  left join journal j on p.journalid = j.id
where a.id = any(%s)
order by a.id
"""
    current_author, paperauthors, papers, conferences, journals = None, set(), set(), set(), set()
    rows = list(__execute_sql(sql, (author_ids,)))
    for r in rows:
        if current_author is not None and current_author.id != r[0]:
            yield AuthorTraining(author=current_author,
                                 papers=papers,
                                 paperauthors=paperauthors,
                                 conferences=conferences,
                                 journals=journals)
            current_author, paperauthors, papers, conferences, journals = None, set(), set(), set(), set()


        current_author = Author._make(r[0:3])
        paperauthor = PaperAuthor._make(r[3:7])
        if paperauthor.paperid and paperauthor.authorid:
            paperauthors.add(paperauthor)
        paper = Paper._make(r[7:11])
        if paper.id:
            papers.add(paper)
        conference = Conference._make(r[11:14])
        if conference.id:
            conferences.add(conference)
        journal = Journal._make(r[14:17])
        if journal.id:
            journals.add(journal)

    if current_author is not None:
        yield AuthorTraining(author=current_author,
                             papers=papers,
                             paperauthors=paperauthors,
                             conferences=conferences,
                             journals=journals)