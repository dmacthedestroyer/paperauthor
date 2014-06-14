from collections import defaultdict
import csv
import data
import read
import settings
import train


def submit_prediction():
    print("build tuples from validation data")
    classification_tuples = read.unpickle_or_build(settings.MODEL_DIR + "\\classification_tuples.pickle",
                                                   lambda: train.build_classification_tuples(data.get_valid_tuples()))
    print("get the classifier based on the training data")
    classifier = read.unpickle_or_build(settings.MODEL_DIR + "\\classifier.pickle",
                                        lambda: train.build_paper_author_classifier()[0])


    classification_tuple_keys = classification_tuples.keys()
    print("build predictions for validation data")
    predictions = list(classifier.predict_proba([classification_tuples[k] for k in classification_tuple_keys])[:, 1])

    print("write predictions to csv in {0}".format(settings.SUBMISSION_PATH))
    author_predictions = defaultdict(list)
    paper_predictions = {}

    for (a_id, p_id), pred in zip(classification_tuple_keys, predictions):
        author_predictions[a_id].append((pred, p_id))
    for author_id in sorted(author_predictions):
        paper_ids_sorted = sorted(author_predictions[author_id], reverse=True)
        paper_predictions[author_id] = [x[1] for x in paper_ids_sorted]

    with open(settings.SUBMISSION_PATH, "w") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerow(("AuthorId", "PaperIds"))
        for author_id in paper_predictions:
            writer.writerow((str(author_id), " ".join(str(i) for i in paper_predictions[author_id])))


if __name__ == "__main__":
    submit_prediction()