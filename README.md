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

Outcome
===========
My classifier scores in the mid-70% for the MAP, which is utterly disapointing.  I wasn't able to incorporate all the
features I had planned, and some of the ones I did come up with seemed to have less of an effect than I anticipated.

The more time-consuming portion of the project had to do with extracting keywords from author affiliations, paper 
titles, paper keywords, and journal and conference titles.  My hypothesis was that an author that has many keywords 
associated with the particular paper in question would show up to be a good match for that paper.  Perhaps this 
line of thinking is correct, but my implementation was incorrect.

I implemented this by displaying the top n keywords associated with the given author, and the top n keywords associated 
with the given paper.  This resulted in 2n features per tuple.  I tweaked the parameters so that it'd generate anywhere 
between 100-500 features per tuple in keywords alone, with a very weak positive correlation between the number of 
keyword features and the MAP score.  Based on the sparsity of keywords in any of the five attributes I pulled from, this
 is less surprising than it should have been when I started calculating MAP scores.

Another set of features I wasn't able to implement was comparing string distances between author name/affiliation and 
paperauthor name/affiliation.  This, I feel, would contribute strongly to a higher MAP score since name/affiliation is 
much less sparse than keyword matches, and a higher string distance on name means much more than an author and paper 
both sharing a very common keyword.  Had I anticipated coming so close to the submission deadline, I would have started 
with name distances then built on upon keyword matches afterward.
 
 Overall, I felt I spent far too much time struggling with avoidable issues and failed implementations and, while still 
 a learning experience, not quite on the topics I had hoped for.