from collections import Counter
import itertools
from random import randint
from sklearn.ensemble import RandomForestClassifier
import data
from keywords import KeywordRepository
import keywords
import models


def __build_author_tuple(aet, keyword_repository):
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
    for kw in keyword_repository.affiliation_keywords:
        yield author_affiliation_keyword_counts[kw]

    for f in __build_common_tuple(aet, keyword_repository):
        yield f


def __build_paper_tuple(aet, keyword_repository):
    assert len(aet.paper) == 1

    # year of publication
    for p in aet.paper:
        yield p.year

    # number of coauthors
    yield len(aet.author)

    for f in __build_common_tuple(aet, keyword_repository):
        yield f


def __build_paperauthor_tuple(aet, keyword_repository):
    assert len(aet.paperauthor) == 1

    # frequency of occurrence of common affiliation keywords as reported on papers published by this author
    paperauthor_affiliation_counts = keywords.general_keyword_counter(pa.affiliation for pa in aet.paperauthor)
    for kw in keyword_repository.affiliation_keywords:
        yield paperauthor_affiliation_counts[kw]


def __build_common_tuple(aet, keyword_repository):
    # occurrence of common keywords for papers
    paper_keyword_counts = Counter(itertools.chain.from_iterable(keywords.extract_paper_keywords(p.keyword) for p in aet.paper))
    for kw in keyword_repository.paper_keywords:
        yield paper_keyword_counts[kw]
    # occurrence of common keywords for paper titles
    title_keyword_counts = keywords.general_keyword_counter(p.title for p in aet.paper)
    for kw in keyword_repository.paper_title_keywords:
        yield title_keyword_counts[kw]
    # occurrence of common keywords for conference full names
    conference_fullname_keyword_counts = keywords.general_keyword_counter(c.fullname for c in aet.conference)
    for kw in keyword_repository.conference_fullname_keywords:
        yield conference_fullname_keyword_counts[kw]
    # occurrence of common keywords for journal full names
    journal_fullname_keyword_counts = keywords.general_keyword_counter(j.fullname for j in aet.journal)
    for kw in keyword_repository.journal_fullname_keywords:
        yield journal_fullname_keyword_counts[kw]


def build_classification_tuples(expanded_tuples):
    keyword_repository = data.unpickle_or_build("keywords.pickle", KeywordRepository)

    print("\tbuilding author-specific tuples")
    a = {g[0].id: list(__build_author_tuple(g[1], keyword_repository)) for g in models.group_expanded_tuples(expanded_tuples, lambda e: e.author)}
    print("\tbuilding paper-specific tuples")
    p = {g[0].id: list(__build_paper_tuple(g[1], keyword_repository)) for g in models.group_expanded_tuples(expanded_tuples, lambda e: e.paper)}
    pa = {(g[0].authorid, g[0].paperid): list(__build_paperauthor_tuple(g[1], keyword_repository)) for g in models.group_expanded_tuples(expanded_tuples, lambda e: e.paperauthor)}
    print("\tbuilding paperauthor-specific tuples")

    #after building up all the individual tuples, combine them for each author/paper pair
    return {k: list(itertools.chain(a[k[0]], p[k[1]], pa[k])) for k in pa}


def build_paper_author_classifier():
    """
    Builds a random forest classifier, trained with the training data supplied in the postgres database.
    The training is done with ~70% of the data, and a corresponding accuracy score is measured against the other ~30%.
    :return: the random forest classifier, along with the accuracy score
    """
    print("*** Building Random Forest Classifier for Paper/Author dataset ***")
    training_tuples = data.unpickle_or_build("training_tuples.pickle",
                                             lambda: build_classification_tuples(data.get_train_tuples()))
    print("get training class labels")
    training_class_labels = data.unpickle_or_build("training_class_labels.pickle",
                                                   lambda: data.get_training_class_labels())
    print("train the classifier")
    print("\tsplitting data into training and validation datasets")
    training, validation = list(), list()
    for i in training_class_labels:
        training.append(i) if randint(0, 10) < 7 else validation.append(i)

    classifier_input_tuples = [training_tuples[k] for k in training]
    classifier_input_class_labels = [training_class_labels[k] for k in training]

    print("\ttraining classifier")
    classifier = RandomForestClassifier(n_estimators=50, verbose=2)
    classifier.fit(classifier_input_tuples, classifier_input_class_labels)

    print("calculate accuracy of classifier")
    score = classifier.score([training_tuples[k] for k in validation], [training_class_labels[k] for k in validation])
    print("\tmean accuracy with training data: {0}".format(score))
    return classifier, score


if __name__ == "__main__":
    classifier, score = build_paper_author_classifier()
