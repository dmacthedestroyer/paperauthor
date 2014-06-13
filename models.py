from collections import namedtuple

Author = namedtuple("Author", ["id", "name", "affiliation"])
Paper = namedtuple("Paper", ["id", "title", "year", "keyword"])
PaperAuthor = namedtuple("PaperAuthor", ["paperid", "authorid", "name", "affiliation"])
Journal = namedtuple("Journal", ["id", "shortname", "fullname"])
Conference = namedtuple("Conference", ["id", "shortname", "fullname"])
Train = namedtuple("Train", ["authorid", "paperid", "confirmed"])

class TrainingTuple(namedtuple("Training", ["authors", "papers", "paperauthors", "journals", "conferences"])):
    __slots__ = ()

    def __str__(self):
        return "{0} authors\t{1} papers\t{2} paperauthors\t{3} journals\t{4} conferences".format(len(self.authors),
                                                                                                 len(self.papers),
                                                                                                 len(self.paperauthors),
                                                                                                 len(self.journals),
                                                                                                 len(self.conferences))