from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import JsonResponse

import urllib2

from six_degrees_of_drake.models import Artist

# HOME PAGE
def index(request):
    all_artists_list = Artist.objects.all()
    context = {'artist_list': all_artists_list}
    return render(request, 'six_degrees_of_drake/index.html', context)

# DETAILS PAGE
def detail(request, artist_name):
    response = "This is the detail page for %s <br><br>" % artist_name
    # TODO: Try to init artist if does not exist
    artist_matches = Artist.objects.filter(name__iexact=artist_name)

    if artist_matches:
        artist = artist_matches[0] # TODO: Try to init artist it doesn't exist
        context = {'nodes': artist.nodes_json(), 'links': artist.links_json()}
        return render(request, 'six_degrees_of_drake/details.html', context)
    else:
        response += "Cannot find name of artist"
        return HttpResponse(response)

# STATS PAGE
def stats(request, artist_name):
    response = "This is the statistics page for %s <br><br>" % artist_name
    artist_list = Artist.objects.filter(name__iexact=artist_name)

    if artist_list:
        associated_acts_count = artist_list[0].associated_acts.count()
        response += "Number of associated acts: %s" % associated_acts_count
    else:
        response += "Cannot find name of artist"

    return HttpResponse(response)

# QUERY ENDPOINT
def query(request, query):
    # Make request to Wikipedia OpenSearch API
    wikipedia_endpoint = "http://en.wikipedia.org/w/api.php?action=opensearch&search="

    # Transform response into list of URLs
    # ...

    # Check to see if any entries are artists
    # ...

    # Add artists entries + url to response object
    response = []
    response.append({'value': query})
    response.append({'value': "drake"})
    response.append({'value': "birdman"})
    return JsonResponse(response, safe=False)
