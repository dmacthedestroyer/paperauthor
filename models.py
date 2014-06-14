from collections import namedtuple
import itertools

# represents the author table
Author = namedtuple("Author", ["id", "name", "affiliation"])

# represents the paper table
Paper = namedtuple("Paper", ["id", "title", "year", "keyword"])

# represents the paperauthor table
PaperAuthor = namedtuple("PaperAuthor", ["authorid", "paperid", "name", "affiliation"])

# represents the journal table
Journal = namedtuple("Journal", ["id", "shortname", "fullname"])

# represents the conference table
Conference = namedtuple("Conference", ["id", "shortname", "fullname"])

# the corresponding author, paper, paperauthor, journal, and conference namedtuples for a given author/paper pair
Expanded = namedtuple("Expanded", ["author", "paper", "paperauthor", "journal", "conference"])


def group_expanded_tuples(list_of_extended_namedtuples, key):
    """
    Groups the given list of namedtuples by the provided key, resulting in a list of Expanded namedtuples with sets for
    the attributes instead of single namedtuples
    :param list_of_extended_namedtuples:
    :param key:
    :return:
    """
    for g in itertools.groupby(sorted(list_of_extended_namedtuples, key=key), key=key):
        groups = list(g[1])

        yield (g[0], Expanded(author=set(e.author for e in groups if e.author),
                              paper=set(e.paper for e in groups if e.paper),
                              paperauthor=set(e.paperauthor for e in groups if e.paperauthor),
                              journal=set(e.journal for e in groups if e.journal),
                              conference=set(e.conference for e in groups if e.conference)))
