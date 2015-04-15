from django.conf.urls import patterns, url
from six_degrees_of_drake import views

urlpatterns = patterns('',
    # ex: /six_degrees_of_drake/
    url(r'^$', views.index, name='index'),
    # ex: /six_degrees_of_drake/drake/
    url(r'^(?P<artist_name>\w+)/$', views.detail, name='detail'),
    # ex: /six_degrees_of_drake/drake/stats/
    url(r'^(?P<artist_name>\w+)/stats/$', views.stats, name='stats'),
)
