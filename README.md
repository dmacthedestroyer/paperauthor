TCSS 555 final project
===========

the KDD Cup 2013 challenge, matching authors with papers.  Details on the challenge can be found
here: https://www.kaggle.com/c/kdd-cup-2013-author-paper-identification-challenge

How to run:
Install Python 3.4 64-bit and the following packages:
    psycopg2 -- to interface with the postgresql database
    unidecode -- a package that unaccents characters
    ml_metrics -- to calculate the mean average precision
    scikit, numpy, etc for RandomForest classification

Download and unpack the postgres database provided on the Kaggle site

Modify the directory and postgres connection string settings found in settings.py

To build the classifier and output its score against the training data, execute the train.py script
To build the classifier and produce the submission, execute the predict.py script
To calculate the MAP on the submission, execute the score.py script