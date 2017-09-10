# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Lookup

# Create your models here.

class Actor(models.Model):
  name = models.CharField(max_length=100, null=False, blank=False, unique=True, db_index=True)
  fb_likes = models.IntegerField(null=False, default=0)

  def __repr__(self):
    return self.name

  def __str__(self):
    return self.__repr__()


class Director(models.Model):
  name = models.CharField(max_length=100, null=False, blank=False, unique=True, db_index=True)
  fb_likes = models.IntegerField(null=False, default=0)

  def __repr__(self):
    return self.name

  def __str__(self):
    return self.__repr__()

class Movie(models.Model):
  director = models.ForeignKey(Director, on_delete=models.CASCADE)
  actors = models.ManyToManyField(Actor, through="MovieActor")
  # Actual data fields

  title = models.CharField(max_length=150, null=False, blank=False, db_index=True)
  year = models.IntegerField(null=False, db_index=True)
  duration = models.IntegerField(null=False)
  is_color = models.BooleanField(null=False)
  # Number of reviews written from external critics
  num_critic_for_reviews = models.IntegerField(null=False)
  # Number of reviews written by imdb users
  num_users_for_reviews = models.IntegerField(null=False)
  # Number of users who voted on the imdb score.
  num_voted_users = models.IntegerField(null=False)
  # Money files can be giant numbers, use BigIntegerField instead.
  domestic_gross = models.BigIntegerField(null=False)
  worldwide_gross = models.BigIntegerField(null=False)
  budget = models.BigIntegerField(null=False)
  cast_total_facebook_likes = models.IntegerField(null=False)
  imdb_link = models.CharField(max_length=128, null=False, blank=False)
  # Fully written out language name i.e. English, French, Spanish
  language = models.CharField(max_length=64, null=False, blank=False)
  # *Mostly* written out country i.e. USA, UK, Germany, France...
  country = models.CharField(max_length=128, null=False, blank=False)
  # String representing rating 'R', 'PG-13', 'Not Rated' e.t.c.
  content_rating = models.CharField(max_length=16, null=False, blank=False)
  # Range from 0->10
  imdb_score = models.FloatField(null=False)
  # Expressed as width / height
  aspect_ratio = models.FloatField(null=False)
  fb_likes = models.IntegerField(null=False, default=0)
  image_url = models.CharField(max_length=256, null=False, blank=False)

  def __repr__(self):
    return "%s (%s)" % (self.title, self.year)

  def __str__(self):
    return self.__repr__()

  def profit(self, gross_type="domestic"):
    if gross_type == "domestic":
      return float(self.domestic_gross) / self.budget
    else:
      return float(self.worldwide_gross) / self.budget

  class Meta:

    unique_together = ("title", "year")

class PersonQuerySet(models.query.QuerySet):
    def in_age_range(self, min, max):
        return self.filter(age__gte=min, age__lt=max)

class MovieActor(models.Model):
  movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
  actor = models.ForeignKey(Actor, on_delete=models.CASCADE)

  def __repr__(self):
    return "%s -> %s" % (self.movie, self.actor)

  class Meta:

    unique_together = ("movie", "actor")

class MovieGenre(models.Model):
  movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
  genre = models.CharField(max_length=30, null=False, blank=False, db_index=True)

  def __repr__(self):
    return "%s -> %s" % (self.movie, self.genre)

  class Meta:

    unique_together = ("movie", "genre")

class MoviePlotKeyword(models.Model):
  movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
  keyword = models.CharField(max_length=120, null=False, blank=False)

  def __repr__(self):
    return "%s -> %s" % (self.movie, keyword)

  class Meta:

    unique_together = ("movie", "keyword")
