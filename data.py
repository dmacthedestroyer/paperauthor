import psycopg2
from models import Author, Paper, PaperAuthor, Conference, Journal, TrainingTuple, Train
import settings


def __get_cursor():
    return psycopg2.connect(settings.POSTGRESQL_CONNECTION_STRING).cursor()


def __execute_sql(sql, params=None):
    cursor = __get_cursor()
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


def get_training_tuples(ids, tuple_type):
    table_alias_by_type = {Author: "a", Paper: "p"}
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
where {0}.id = any(values {1})
order by {0}.id
""".format(table_alias_by_type[tuple_type], ",".join("({0})".format(i) for i in ids))
    tt = TrainingTuple._make(set() for x in range(5))
    # cursor = __get_cursor()
    # mogrified = cursor.mogrify(sql, (ids,))

    for r in __execute_sql(sql, (ids,)):
        if (tuple_type == Author and any(tt.authors) and r[0] not in (a.id for a in tt.authors)) or \
                (tuple_type == Paper and any(tt.papers) and r[7] not in (p.id for p in tt.papers)):
            yield tt
            tt = TrainingTuple._make(set() for x in range(5))

        if r[0]:
            tt.authors.add(Author._make(r[0:3]))
        if r[3] and r[4]:
            tt.paperauthors.add(PaperAuthor._make(r[3:7]))
        if r[7]:
            tt.papers.add(Paper._make(r[7:11]))
        if r[11]:
            tt.conferences.add(Conference._make(r[11:14]))
        if r[14]:
            tt.journals.add(Journal._make(r[14:17]))

    if any(tt.authors):
        yield tt


def read_training_ids():
    sql = """
select authorid, paperid, true
from trainconfirmed
union all
select authorid, paperid, false
from traindeleted
"""
    return (Train._make(r) for r in __execute_sql(sql))

if __name__ == "__main__":
    for at in get_training_tuples([1122750, 1998870, 2269160, 339923, 1378795, 634048, 1039808, 1085027, 92353, 973910],Author):
        print(at)
