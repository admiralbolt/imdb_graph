import collections

# The expected columns of the csv file to read data from.
csv_cols = [
  'actor_5_name',
  'color',
  'director_name',
  'num_critic_for_reviews',
  'duration',
  'director_facebook_likes',
  'actor_3_facebook_likes',
  'actor_2_name',
  'actor_1_facebook_likes',
  'actor_3_name',
  'genres',
  'actor_1_name',
  'movie_title',
  'actor_4_name',
  'actor_2_facebook_likes',
  'num_voted_users',
  'cast_total_facebook_likes',
  'plot_keywords',
  'worldwide_gross',
  'movie_imdb_link',
  'actor_4_facebook_likes',
  'domestic_gross',
  'num_user_for_reviews',
  'language',
  'country',
  'content_rating',
  'budget',
  'title_year',
  'image_url',
  'imdb_score',
  'actor_5_facebook_likes',
  'aspect_ratio',
  'movie_facebook_likes'
]

num_actors = 5

def convert_row_to_dict(row):
  """
  Converts a csv line into a dictionary mapping from column_name -> value.
  Much easier to work with than using indexes constantly.
  """
  data_dict = collections.defaultdict(dict)
  for i, col in enumerate(csv_cols):
    data_dict[col] = row[i].strip().decode("utf-8").encode("ascii", "ignore")
  return data_dict

def parse_with_default(val, default):
  return default if not val else val
