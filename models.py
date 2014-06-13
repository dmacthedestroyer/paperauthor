from collections import namedtuple
import itertools

Author = namedtuple("Author", ["id", "name", "affiliation"])
Paper = namedtuple("Paper", ["id", "title", "year", "keyword"])
PaperAuthor = namedtuple("PaperAuthor", ["paperid", "authorid", "name", "affiliation", "confirmed"])
Journal = namedtuple("Journal", ["id", "shortname", "fullname"])
Conference = namedtuple("Conference", ["id", "shortname", "fullname"])

Expanded = namedtuple("Expanded", ["author", "paper", "paperauthor", "journal", "conference"])


def group_expanded_tuples(l, key):
    for g in itertools.groupby(sorted(l, key=key), key=key):
        groups = list(g[1])

        yield (g[0], Expanded(author=set(e.author for e in groups if e.author),
                              paper=set(e.paper for e in groups if e.paper),
                              paperauthor=set(e.paperauthor for e in groups if e.paperauthor),
                              journal=set(e.journal for e in groups if e.journal),
                              conference=set(e.conference for e in groups if e.conference)))
