from collections import Counter
import itertools
from random import randint
from sklearn.ensemble import RandomForestClassifier
import data
from keywords import KeywordRepository
import models
import read
import settings


def __build_author_tuple(aet, affiliation_keywords, paper_keywords, paper_title_keywords,
                         conference_fullname_keywords, journal_fullname_keywords):
    assert len(aet.author) == 1

    yield len(aet.paper)
    years = [p.year for p in aet.paper if p.year > 0]
    yield min(years) if any(years) else 0
    yield sum(years) / float(len(years)) if any(years) else 0
    yield max(years) if any(years) else 0
    yield len(aet.conference)
    yield len(aet.journal)
    author_affiliation_keyword_counts = read.general_keyword_counter(a.affiliation for a in aet.author)
    for kw in affiliation_keywords:
        yield author_affiliation_keyword_counts[kw]

    for f in __build_common_tuple(aet, paper_keywords, paper_title_keywords, conference_fullname_keywords, journal_fullname_keywords):
        yield f


def __build_paper_tuple(aet, paper_keywords, paper_title_keywords, conference_fullname_keywords, journal_fullname_keywords):
    assert len(aet.paper) == 1

    for p in aet.paper:
        yield p.year
    yield len(aet.author)
    for f in __build_common_tuple(aet, paper_keywords, paper_title_keywords, conference_fullname_keywords, journal_fullname_keywords):
        yield f


def __build_paperauthor_tuple(aet, affiliation_keywords):
    assert len(aet.paperauthor) == 1

    paperauthor_affiliation_counts = read.general_keyword_counter(pa.affiliation for pa in aet.paperauthor)
    for kw in affiliation_keywords:
        yield paperauthor_affiliation_counts[kw]


def __build_common_tuple(aet, paper_keywords, paper_title_keywords,
                         conference_fullname_keywords, journal_fullname_keywords):
    paper_keyword_counts = Counter(itertools.chain.from_iterable(read.extract_paper_keywords(p.keyword) for p in aet.paper))
    for kw in paper_keywords:
        yield paper_keyword_counts[kw]
    title_keyword_counts = read.general_keyword_counter(p.title for p in aet.paper)
    for kw in paper_title_keywords:
        yield title_keyword_counts[kw]
    conference_fullname_keyword_counts = read.general_keyword_counter(c.fullname for c in aet.conference)
    for kw in conference_fullname_keywords:
        yield conference_fullname_keyword_counts[kw]
    journal_fullname_keyword_counts = read.general_keyword_counter(j.fullname for j in aet.journal)
    for kw in journal_fullname_keywords:
        yield journal_fullname_keyword_counts[kw]


def build_classification_tuples(expanded_tuples):
    keyword_repository = read.unpickle_or_build(settings.MODEL_DIR + "\\keywords.pickle", KeywordRepository)

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

    return {k: list(itertools.chain(a[k[0]], p[k[1]], pa[k])) for k in pa}


def build_paper_author_classifier():
    training_tuples = read.unpickle_or_build(settings.MODEL_DIR + "\\training_tuples.pickle",
                                             lambda: build_classification_tuples(data.get_train_tuples()))
    print("get training class labels")
    training_class_labels = read.unpickle_or_build(settings.MODEL_DIR + "\\training_class_labels.pickle",
                                                   lambda: data.get_training_class_labels())
    print("train the classifier")
    training, validation = list(), list()
    for i in training_class_labels:
        training.append(i) if randint(0, 10) < 7 else validation.append(i)

    classifier_input_tuples = [training_tuples[k] for k in training]
    classifier_input_class_labels = [training_class_labels[k] for k in training]

    classifier = RandomForestClassifier(n_estimators=50, verbose=2)
    classifier.fit(classifier_input_tuples, classifier_input_class_labels)

    return classifier, [training_tuples[k] for k in validation], [training_class_labels[k] for k in validation]


if __name__ == "__main__":
    classifier, validation_input_tuples, validation_input_class_labels = build_paper_author_classifier()
    print("measure classifier precision")
    print("mean accuracy with validation data: {0}".format(classifier.score(validation_input_tuples,
                                                                            validation_input_class_labels)))