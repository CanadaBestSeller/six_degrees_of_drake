from six_degrees_of_drake.models import Artist
from pprint import pprint

drake_url = "http://en.wikipedia.org/wiki/Drake_(entertainer)"
drake, created = Artist.get_or_create_with_url(drake_url)
drake.save()
drake.populate()

# for associated_act in drake.associated_acts.all():
#     associated_act.populate()

pprint(drake.associated_acts.all())
