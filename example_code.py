from six_degrees_of_drake.models import Artist
from pprint import pprint

drake = Artist.objects.all()[0]
drake.nodes_json()
drake.links_json()
