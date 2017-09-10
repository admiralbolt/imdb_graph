from django.core.management.base import BaseCommand, CommandError
import utils
from imdb_graph.models import *
import csv
from pprint import pprint

class Command(BaseCommand):

  help = "Inserts data into the sqlite database from a csv file."

  def add_arguments(self, parser):
    # Positional argument
    parser.add_argument("csv_file", type=str)
    parser.add_argument(
      "--debug",
      action="store_true",
      dest="debug",
      help="Print out information about each movie being inserted."
    )
    return

  def handle(self, *args, **options):
    # fun times
    with open(options["csv_file"], "r") as rh:
      reader = csv.reader(rh)
      # Skip the header info see utils.data_cols for list of columns
      next(reader, None)
      for line in reader:
        if len(line) > 0:
          data_dict = utils.convert_row_to_dict(line)
          try:
            # Now we create our actual objects, directors first
            # important note, get_or_create returns a tuple
            # The first value is the actual object,
            # the scond value is if it was created
            director = Director.objects.get_or_create(
              name=data_dict["director_name"],
              fb_likes=utils.parse_with_default(
                data_dict["director_facebook_likes"],
                0
              )
            )[0]
            # Next our actors
            actors = []
            for i in range(1, utils.num_actors + 1):
              if data_dict["actor_%s_name" % (i,)]:
                actors.append(Actor.objects.get_or_create(
                  name=data_dict["actor_%s_name" % (i,)],
                  fb_likes=utils.parse_with_default(
                    data_dict["actor_%s_facebook_likes" % (i,)],
                    0
                  )
                )[0])

            # Finally we create our movie
            movie, is_new_movie = Movie.objects.get_or_create(
              director=director,
              title=data_dict["movie_title"],
              year=data_dict["title_year"],
              duration=data_dict["duration"],
              is_color=(data_dict["color"] == "Color"),
              num_critic_for_reviews=utils.parse_with_default(data_dict["num_critic_for_reviews"], 0),
              num_users_for_reviews=utils.parse_with_default(data_dict["num_user_for_reviews"], 0),
              num_voted_users=utils.parse_with_default(data_dict["num_voted_users"], 0),
              domestic_gross=data_dict["domestic_gross"],
              worldwide_gross=data_dict["worldwide_gross"],
              budget=data_dict["budget"],
              cast_total_facebook_likes=data_dict["cast_total_facebook_likes"],
              imdb_link=data_dict["movie_imdb_link"],
              language=data_dict["language"],
              country=data_dict["country"],
              content_rating=data_dict["content_rating"],
              imdb_score=data_dict["imdb_score"],
              aspect_ratio=utils.parse_with_default(data_dict["aspect_ratio"], 1.78),
              fb_likes=data_dict["movie_facebook_likes"],
              image_url=data_dict["image_url"]
            )

            if is_new_movie:
              # Many to many for actors
              for actor in actors:
                MovieActor(movie=movie, actor=actor).save()

              # Load genres
              for genre in data_dict["genres"].split("|"):
                MovieGenre(movie=movie, genre=genre).save()

              # Load keywords
              for keyword in data_dict["plot_keywords"].split("|"):
                MoviePlotKeyword(movie=movie, keyword=keyword).save()
          except Exception as e:
            if options["debug"]:
              print e
              pprint(data_dict)
              print "\n======\n"
