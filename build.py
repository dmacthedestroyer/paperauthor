from collections import Counter, defaultdict
import read

authors = dict()
conferences = dict()
journals = dict()
papers = dict()
paper_authors_by_paper = defaultdict(list)
paper_authors_by_author = defaultdict(list)

affiliation_counter = Counter()
conference_fullname_counter = Counter()
journal_fullname_counter = Counter()
paper_title_counter = Counter()
paper_keyword_counter = Counter()

file_prefix = "C:\Development\TCSS555\dataRev2"


def read_csv(filename):
    for row in read.read_csv(file_prefix + filename, 1000):
        yield row


def build_models():
    for row in read_csv("\Author.csv"):
        authors[row["Id"]] = row
        for kw in read.extract_general_keywords(row["Affiliation"]):
            affiliation_counter[kw] += 1

    for row in read_csv("\Conference.csv"):
        conferences[row["Id"]] = row
        for kw in read.extract_general_keywords(row["FullName"]):
            conference_fullname_counter[kw] += 1

    for row in read_csv("\Journal.csv"):
        journals[row["Id"]] = row
        for kw in read.extract_general_keywords(row["FullName"]):
            journal_fullname_counter[kw] += 1

    for row in read_csv("\Paper.csv"):
        papers[row["Id"]] = row
        for kw in read.extract_general_keywords(row["Title"]):
            paper_title_counter[kw] += 1
        for kw in read.extract_paper_keywords(row["Keyword"]):
            paper_keyword_counter[kw] += 1
    for row in read_csv("\PaperAuthor.csv"):
        paper_authors_by_paper[row["PaperId"]].append(row)
        paper_authors_by_author[row["AuthorId"]].append(row)

if __name__ == "__main__":
    build_models()
    pass