from django.shortcuts import render
from django.shortcuts import HttpResponse

from six_degrees_of_drake.models import Artist

# HOME PAGE
def index(request):
    all_artists_list = Artist.objects.all()
    context = {'artist_list': all_artists_list}
    return render(request, 'six_degrees_of_drake/index.html', context)

# DETAILS PAGE
def detail(request, artist_name):
    response = "This is the detail page for %s <br><br>" % artist_name
    artist_list = Artist.objects.filter(name__iexact=artist_name)

    if artist_list:
        artist = artist_list[0]
        response += "%s has the following associated acts:<br><br>" % artist_name
        for a in artist.associated_acts.all():
            response += '- ' + a.name + '<br>'
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
