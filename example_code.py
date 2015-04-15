from six_degrees_of_drake.models import Artist
from pprint import pprint

drake_url = "http://en.wikipedia.org/wiki/Drake_(entertainer)"
drake, created = Artist.get_or_create_with_url(drake_url)
drake.save()
drake.populate()

# for associated_act in drake.associated_acts.all():
#     associated_act.populate()
https://www.google.ca/search?q=lil+wayne+drake&ie=utf-8&oe=utf-8&aq=t&rls=org.mozilla:en-US:official&client=firefox-a&channel=sb&gfe_rd=cr&ei=ssUkVbqlCevs8wfR1ICQDg

pprint(drake.associated_acts.all())
