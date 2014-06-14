import os
import pickle
import psycopg2
from models import Author, Paper, PaperAuthor, Conference, Journal, Expanded
import settings


def __execute_sql(sql):
    cursor = psycopg2.connect(settings.POSTGRESQL_CONNECTION_STRING).cursor()
    cursor.execute(sql)
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


def __get_expanded_tuples(inner_table):
    sql = """
with ids as ({0})
select a.id, a.name, a.affiliation,
  pa.authorid, pa.paperid, pa.name, pa.affiliation,
  p.id, p.title, p.year, p.keyword,
  c.id, c.shortname, c.fullname,
  j.id, j.shortname, j.fullname
from ids
  inner join paperauthor pa on ids.authorid = pa.authorid and ids.paperid = pa.paperid
  inner join author a on pa.authorid = a.id
  inner join paper p on pa.paperid = p.id
  left join conference c on p.conferenceid = c.id
  left join journal j on p.journalid = j.id
""".format(inner_table)
    build_from_row = lambda r: Expanded(author=Author._make(r[0:3]) if r[0] else None,
                                        paperauthor=PaperAuthor._make(r[3:7]) if r[3] and r[4] else None,
                                        paper=Paper._make(r[7:11]) if r[7] else None,
                                        conference=Conference._make(r[11:14]) if r[11] else None,
                                        journal=Journal._make(r[14:17]) if r[14] else None)

    return [build_from_row(r) for r in __execute_sql(sql)]


def get_train_tuples():
    """
    Returns a list of Expanded namedtuples for each row in the trainconfirmed, traindeleted tables
    :return:
    """
    inner_table = """
select authorid, paperid from trainconfirmed
union all
select authorid, paperid from traindeleted
"""
    return __get_expanded_tuples(inner_table)


def get_training_class_labels():
    """
    Returns a dict with whether the given (authorid, paperid) pair is confirmed or deleted in the training set
    :return:
    """
    sql = """
select authorid, paperid, true confirmed from trainconfirmed
union all
select authorid, paperid, false confirmed from traindeleted
"""
    return {(r[0], r[1]): r[2] for r in __execute_sql(sql)}


def get_valid_tuples():
    """
    Returns a list of Expanded namedtuples for each (authorid, paperid) pair in the validpaper table
    :return:
    """
    return __get_expanded_tuples("select authorid, paperid from validpaper")


def unpickle_or_build(filename, factory, force_create=False):
    """
    Attempts to unpickle an object at the given file location, or otherwise will create and pickle an object at the
    given file location.  This is useful for persistently caching objects that take some time to initially create
    :param filename: the file location for unpickling
    :param factory: a function to call if the file location doesn't exist.  The resultant object will be pickled and
    then returned
    :param force_create: delete any existing file at filename and call the factory parameter to pickle a new object
    :return: the unpickled object, if a file exists at filename, otherwise the result of calling factory
    """
    if force_create:
        try:
            os.remove(settings.MODEL_DIR + filename)
        except OSError:
            pass

    try:
        with open(settings.MODEL_DIR + filename, 'rb') as file:
            return pickle.load(file)
    except IOError:
        obj = factory()
        with open(settings.MODEL_DIR + filename, 'wb') as file:
            pickle.dump(obj, file)
        return obj
