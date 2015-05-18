from six_degrees_of_drake.models import Artist
from django.core.urlresolvers import reverse
import six_degrees_of_drake.views

reverse
reverse('graph', args=['Drake (rapper)'])

#########

from six_degrees_of_drake.models import Artist

url1 = 'http://en.wikipedia.org/wiki/Drake_(rapper)'
drake1, just_saved1 = Artist.get_or_create_with_url(url1)
drake1.save()

url2 = 'http://en.wikipedia.org/wiki/Drake_(entertainer)'
drake2, just_saved2 = Artist.get_or_create_with_url(url2)
drake2.save()

url3 = 'http://en.wikipedia.org/wiki/Drake (rapper)'
drake3, just_saved3 = Artist.get_or_create_with_url(url3)
drake3.save()

url4 = 'http://en.wikipedia.org/wiki/Drake (entertainer)'
drake4, just_saved4 = Artist.get_or_create_with_url(url4)
drake4.save()
