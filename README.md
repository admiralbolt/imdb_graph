# Imdb Graph

This is a quick web app written to compare movie imdb scores and profits.
The web app is written in python 2.7, using django & jquery.  There are a few
dependencies needed to run the app, everything can be installed with conda
& pip.  Here's the [environment file](conda_env.yml).  To create the env run:

```bash
conda env create -f conda_env.yml
```

Once that's run, change into the imdb_web folder.  The database needs to be
created by running:

```bash
python manage.py migrate
```

Data gets inserted by running the insert_data command and passing a csv file
(this one takes a little while to run):

```bash
python manage.py insert_data ../data/movie_metadata.csv --debug
```

Finally, run the server!

```bash
python manage.py runserver
```

## Dataset
The actual data used is based off of the kaggle 5000 movie dataset with
some manually modifications to get better data.
([their github link](https://github.com/sundeepblue/movie_rating_prediction)).
The crawling script was searching imdb itself to find movies based on title
and was often returning wrong results.  Additionally, it didn't include
the year in the search, so the same movie would be returned multiple times.
The original budget information the-numbers.com was not saved,
but rather the imdb information was used instead, which has much more missing
data, and has multiple different currencies.  Finally, I retained the links
to the movie images in the final output.  The cleaned metadata is in
[data/movie_metadata.csv](data/movie_metadata.csv).
