from collections import namedtuple

Author = namedtuple("Author", ["id", "name", "affiliation"])
Paper = namedtuple("Paper", ["id", "title", "year", "keyword"])
PaperAuthor = namedtuple("PaperAuthor", ["paperid", "authorid", "name", "affiliation"])
Journal = namedtuple("Journal", ["id", "shortname", "fullname"])
Conference = namedtuple("Conference", ["id", "shortname", "fullname"])

AuthorTraining = namedtuple("AuthorTraining", ["author", "papers", "paperauthors", "journals", "conferences"])