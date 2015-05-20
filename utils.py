import urllib2
import json

from django.templatetags.static import static

WIKIPEDIA_API_IMAGE_INFO_MODULE_ENDPOINT = \
    'http://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&pithumbsize=100&titles='

def json_to_response_object(url):
    raw_response = urllib2.urlopen(url).read()
    response_object = json.loads(raw_response, 'utf-8')
    return response_object

def get_artist_image_url(name):
    """
    CAREFUL: The argument here could be utf-8
    """
    query_url = WIKIPEDIA_API_IMAGE_INFO_MODULE_ENDPOINT + urllib2.quote(name.encode('utf-8'))
    print(query_url)
    response_object = json_to_response_object(query_url)
    page_info = response_object['query']['pages'].values()[0]
    return page_info['thumbnail']['source'] if page_info.get('thumbnail') else static('six_degrees_of_drake/unknown.jpg')
