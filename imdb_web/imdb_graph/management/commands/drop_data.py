from django.core.management.base import BaseCommand, CommandError
import utils
from imdb_graph.models import Actor, Director
import csv
from pprint import pprint

class Command(BaseCommand):

  help = "Drops all data from the sqlite database."

  def handle(self, *args, **options):
    Actor.objects.all().delete()
    Director.objects.all().delete()
