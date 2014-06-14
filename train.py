from collections import Counter
import itertools
from random import randint
from sklearn.ensemble import RandomForestClassifier
import data
from keywords import KeywordRepository
import keywords
import models


def __build_author_tuple(aet, affiliation_keywords, paper_keywords, paper_title_keywords,
                         conference_fullname_keywords, journal_fullname_keywords):
    assert len(aet.author) == 1

    # number of papers by this author
    yield len(aet.paper)
    years = [p.year for p in aet.paper if p.year > 0]
    # the earliest year of publication
    yield min(years) if any(years) else 0
    # average year of publication
    yield sum(years) / float(len(years)) if any(years) else 0
    #latest year of publication
    yield max(years) if any(years) else 0
    # number of conferences for this author
    yield len(aet.conference)
    # number of journals for this author
    yield len(aet.journal)

    # generate keywords for this author's affiliation, and return the occurrence of the most common keywords
    author_affiliation_keyword_counts = keywords.general_keyword_counter(a.affiliation for a in aet.author)
    for kw in affiliation_keywords:
        yield author_affiliation_keyword_counts[kw]

    for f in __build_common_tuple(aet, paper_keywords, paper_title_keywords, conference_fullname_keywords, journal_fullname_keywords):
        yield f


def __build_paper_tuple(aet, paper_keywords, paper_title_keywords, conference_fullname_keywords, journal_fullname_keywords):
    assert len(aet.paper) == 1

    # year of publication
    for p in aet.paper:
        yield p.year

    # number of coauthors
    yield len(aet.author)

    for f in __build_common_tuple(aet, paper_keywords, paper_title_keywords, conference_fullname_keywords, journal_fullname_keywords):
        yield f


def __build_paperauthor_tuple(aet, affiliation_keywords):
    assert len(aet.paperauthor) == 1

    # frequency of occurrence of common affiliation keywords as reported on papers published by this author
    paperauthor_affiliation_counts = keywords.general_keyword_counter(pa.affiliation for pa in aet.paperauthor)
    for kw in affiliation_keywords:
        yield paperauthor_affiliation_counts[kw]


def __build_common_tuple(aet, paper_keywords, paper_title_keywords,
                         conference_fullname_keywords, journal_fullname_keywords):
    # occurrence of common keywords for papers
    paper_keyword_counts = Counter(itertools.chain.from_iterable(keywords.extract_paper_keywords(p.keyword) for p in aet.paper))
    for kw in paper_keywords:
        yield paper_keyword_counts[kw]
    # occurrence of common keywords for paper titles
    title_keyword_counts = keywords.general_keyword_counter(p.title for p in aet.paper)
    for kw in paper_title_keywords:
        yield title_keyword_counts[kw]
    # occurrence of common keywords for conference full names
    conference_fullname_keyword_counts = keywords.general_keyword_counter(c.fullname for c in aet.conference)
    for kw in conference_fullname_keywords:
        yield conference_fullname_keyword_counts[kw]
    # occurrence of common keywords for journal full names
    journal_fullname_keyword_counts = keywords.general_keyword_counter(j.fullname for j in aet.journal)
    for kw in journal_fullname_keywords:
        yield journal_fullname_keyword_counts[kw]


def build_classification_tuples(expanded_tuples):
    keyword_repository = data.unpickle_or_build("keywords.pickle", KeywordRepository)

    aac = keyword_repository.most_common_affiliations()
    pkc = keyword_repository.most_common_paper_keywords()
    ptc = keyword_repository.most_common_paper_titles()
    cfc = keyword_repository.most_common_conference_fullnames()
    jfc = keyword_repository.most_common_journal_fullnames()

    print("build classification tuples:")
    a = {g[0].id: list(__build_author_tuple(g[1], aac, pkc, ptc, cfc, jfc)) for g in models.group_expanded_tuples(expanded_tuples, lambda e: e.author)}
    print("\tauthor-specific tuples built")
    p = {g[0].id: list(__build_paper_tuple(g[1], pkc, ptc, cfc, jfc)) for g in models.group_expanded_tuples(expanded_tuples, lambda e: e.paper)}
    print("\tpaper-specific tuples built")
    pa = {(g[0].authorid, g[0].paperid): list(__build_paperauthor_tuple(g[1], aac)) for g in models.group_expanded_tuples(expanded_tuples, lambda e: e.paperauthor)}
    print("\tpaperauthor-specific tuples built")

    #after building up all the individual tuples, combine them for each author/paper pair
    return {k: list(itertools.chain(a[k[0]], p[k[1]], pa[k])) for k in pa}


def build_paper_author_classifier():
    """
    Builds a random forest classifier, trained with the training data supplied in the postgres database.
    The training is done with ~70% of the data, and a corresponding accuracy score is measured against the other ~30%.
    :return: the random forest classifier, along with the accuracy score
    """
    training_tuples = data.unpickle_or_build("training_tuples.pickle",
                                             lambda: build_classification_tuples(data.get_train_tuples()))
    print("get training class labels")
    training_class_labels = data.unpickle_or_build("training_class_labels.pickle",
                                                   lambda: data.get_training_class_labels())
    print("train the classifier")
    training, validation = list(), list()
    for i in training_class_labels:
        training.append(i) if randint(0, 10) < 7 else validation.append(i)

    classifier_input_tuples = [training_tuples[k] for k in training]
    classifier_input_class_labels = [training_class_labels[k] for k in training]

    classifier = RandomForestClassifier(n_estimators=50, verbose=2)
    classifier.fit(classifier_input_tuples, classifier_input_class_labels)

    print("calculate accuracy of classifier")
    return classifier, classifier.score([training_tuples[k] for k in validation],
                                        [training_class_labels[k] for k in validation])


if __name__ == "__main__":
    classifier, score = build_paper_author_classifier()
    print("mean accuracy with training data: {0}".format(score))