from django.conf.urls import patterns, url
from six_degrees_of_drake import views
from django.views.generic.base import RedirectView

urlpatterns = patterns('',
    # ex: /six_degrees_of_drake/
    url(r'^$', views.index, name='index'),

    # ex: /six_degrees_of_drake/graph/drake_(rapper)
    url(r'^graph/(?P<artist_wiki_name>.+?)/$', views.graph, name='graph'),

    # ex: /six_degrees_of_drake/info/drake_(rapper)
    url(r'^info/(?P<artist_wiki_name>.+?)/$', views.info, name='info'),

    # ex: /six_degrees_of_drake/drake/stats/
    url(r'^stats/(?P<artist_name>\w+)/stats/$', views.stats, name='stats'),

    # query endpoint for wikipedia autocomplete ajax calls
    url(r'^query/(?P<query>[A-Za-z0-9%]+)/$', views.query, name='query'),

    # example query endpoint for testing prefetch
    url(r'^example_films.json/$', views.example_films),
)
