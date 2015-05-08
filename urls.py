from django.conf.urls import patterns, url
from six_degrees_of_drake import views
from django.views.generic.base import RedirectView

urlpatterns = patterns('',
    # ex: /six_degrees_of_drake/
    url(r'^$', views.index, name='index'),
    # ex: /six_degrees_of_drake/drake/
    url(r'^details/(?P<artist_name>\w+)/$', views.detail, name='detail'),
    # ex: /six_degrees_of_drake/drake/stats/
    url(r'^stats/(?P<artist_name>\w+)/stats/$', views.stats, name='stats'),

    # query endpoint for wikipedia autocomplete ajax calls
    url(r'^query/(?P<query>[A-Za-z0-9%]+)/$', views.query, name='query'),

    # example query endpoint for testing prefetch
    url(r'^example_films.json/$', views.example_films),
)
