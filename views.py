from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from django.templatetags.static import static

import urllib2
import json
import re

from six_degrees_of_drake.models import Artist

WIKIPEDIA_DOMAIN = 'http://en.wikipedia.org/wiki/'
WIKIPEDIA_API_QUERY_MODULE_ENDPOINT = \
    'http://en.wikipedia.org/w/api.php?action=query&list=search&format=json&srwhat=text&srlimit=3&continue=&srprop=snippet&srsearch=%22associated%20acts%22+intitle:'
WIKIPEDIA_API_IMAGE_INFO_MODULE_ENDPOINT = \
    'http://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&pithumbsize=100&titles='

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
    # Make request to Wikipedia API, which has been given parameters to 
    # search for articles containing the string "associated acts"
    query_url = WIKIPEDIA_API_QUERY_MODULE_ENDPOINT + query

    # Transform response into list of artists
    response_object = json_to_response_object(query_url)

    # Add artist + metatdata to result
    result = []
    for artist_entry in response_object['query']['search']:
        artist_dictionary = {}
        artist_dictionary['name'] = artist_entry['title']
        artist_dictionary['url'] = WIKIPEDIA_DOMAIN + urllib2.quote(artist_entry['title'])
        artist_dictionary['snippet'] = delete_tags(artist_entry['snippet'])
        artist_dictionary['image_url'] = get_artist_image_url(artist_entry['title'])
        # TODO get the url of the artist's image
        result.append(artist_dictionary)

    return JsonResponse(result, safe=False)

# UTILS
def json_to_response_object(url):
    raw_response = urllib2.urlopen(url).read()
    response_object = json.loads(raw_response)
    return response_object
    
def delete_tags(text):
    return re.sub('<.*?>', '', text)

def get_artist_image_url(name):
    query_url = WIKIPEDIA_API_IMAGE_INFO_MODULE_ENDPOINT + urllib2.quote(name)
    response_object = json_to_response_object(query_url)
    page_info = response_object['query']['pages'].values()[0]
    return page_info['thumbnail']['source'] if page_info.get('thumbnail') else static('unknown.jpg')
