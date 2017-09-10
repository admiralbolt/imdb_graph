from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^auto_complete$', views.auto_complete, name='auto_complete'),
    url(r'^get_movie$', views.get_movie, name='get_movie'),
    url(r'^movie_card$', views.movie_card, name='movie_card'),
]
