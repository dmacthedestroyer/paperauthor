"""
Use this script to calculate the mean average precision of the submitted file
"""

import csv
from ml_metrics import mapk
import predict
import settings


def __read_rows(file_name):
    with open(file_name, "r", encoding="utf8") as file:
        return {int(r["AuthorId"]): [int(x) for x in r["PaperIds"].split()] for r in csv.DictReader(file)}


if __name__ == "__main__":
    try:
        submission = __read_rows(settings.SUBMISSION_PATH)
    except FileNotFoundError:
        predict.submit_prediction()
        submission = __read_rows(settings.SUBMISSION_PATH)

    valid_solution = __read_rows(settings.VALID_SOLUTION_PATH)

    assert sorted(valid_solution.keys()) == sorted(submission.keys()), "submission doesn't have the same author ids as valid"
    score = mapk([valid_solution[k] for k in valid_solution.keys()], [submission[k] for k in valid_solution.keys()])
    print("Mean average precision for solution file: {0}".format(score))
