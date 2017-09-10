# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from models import Movie
from fuzzywuzzy import fuzz
from django.core import serializers
from django.template.loader import get_template
from imdb_graph.models import Movie, MovieGenre, MoviePlotKeyword
import json

# Create your views here.

def jaccard(set_a, set_b):
  return float(len(set_a.intersection(set_b))) / len(set_a.union(set_b))

def score(movie, keyword):
  # Fucking nailed it.
  # We score based on two critieria:
  # 1. The fuzzy finding partial_ratio -- This is based on Levenshtein distance
  #      from the input keyword to the target movie title.  I.e. how many steps
  #      it takes to get from one to the other.  However, this by itself
  #      is not sufficient, as 'The Rings' is a perfect partial of a movie
  #      like 'The Lord of the Rings'.  The partial ratio is a number from
  #      0-100.
  # 2. Jaccard Coefficient of the character set.  We take the set of characters
  #      in the keyword and the movie title and take the length of their
  #      intersection divided by the length of their union.  This helps
  #      filter out only partially matching strings.  This returns a number
  #      from 0-1, we scale up to half the max value of the partial_ratio.
  title = movie.title.lower()
  keyword_l = keyword.lower()
  return fuzz.partial_ratio(title, keyword_l) + 50 * jaccard(set(keyword_l), set(title))

def list_display_string(l):
  return " &middot; ".join(filter(None, l))

# Actual views below here
# =======================

def index(request):
  return render(request, "imdb_graph/index.html")

def auto_complete(request):
  keyword = request.GET["keyword"]
  movies = []
  if keyword:
    movies = Movie.objects.all()
    #movies = sorted(movies, key=lambda movie: fuzz.ratio(movie.title.lower(), keyword.lower()) + fuzz.partial_ratio(movie.title.lower(), keyword.lower()), reverse=True)
    movies = sorted(movies, key=lambda movie: score(movie, keyword), reverse = True)
  return JsonResponse(serializers.serialize("json", movies[:5]), safe=False)

def get_movie(request):
  movie_id = request.GET["movie_id"]
  movie = {}
  if movie_id:
    movie = Movie.objects.filter(id=movie_id)
    # Django is too dumb to serialize a single object
    serialized_movie = json.dumps(json.loads(serializers.serialize("json", movie))[0])
  return JsonResponse(serialized_movie, safe=False)

def movie_card(request):
  movie_id = request.GET["movie_id"]
  template = get_template("imdb_graph/card.html")
  context = {}
  if movie_id:
    movie = Movie.objects.filter(id=movie_id).first()
    director = movie.director
    actors = movie.actors.all()
    genres = MovieGenre.objects.filter(movie_id=movie_id)
    plot_keywords = MoviePlotKeyword.objects.filter(movie_id=movie_id)
    # Do stuff here so we don't have to later
    hours = movie.duration / 60
    minutes = movie.duration % 60
    duration_string = "%sh %sm" % (hours, minutes)
    info_string = list_display_string([
      movie.content_rating,
      duration_string,
      str(movie.year)
    ])
    actor_string = list_display_string([actor.name for actor in actors])
    genre_string = list_display_string([genre.genre for genre in genres])
    keyword_string = list_display_string([
      keyword.keyword for keyword in plot_keywords
    ])
    context = {
      "movie": movie,
      "director": director,
      "actors": actors,
      "genres": genres,
      "plot_keywords": plot_keywords,
      "info_string": info_string,
      "score_range": range(1, 11),
      "score_plus_half": movie.imdb_score + 0.5,
      "actor_string": actor_string,
      "genre_string": genre_string,
      "keyword_string": keyword_string
    }
  return HttpResponse(template.render(context, request))
