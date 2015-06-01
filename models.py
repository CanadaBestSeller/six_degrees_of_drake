from django.db import models

import urllib
import urllib2
import re
import json

from six_degrees_of_drake import utils

domain = "http://en.wikipedia.org"

class Artist(models.Model):
    # url is the primary key and therefore the most important field.
    # It must be unique, and it is the single source of information
    # for name and associated acts
    url             = models.CharField(max_length=1000, blank=False, unique=True)
    image_url       = models.CharField(max_length=1000, blank=True)
    name            = models.CharField(max_length=200, blank=False)
    wiki_name            = models.CharField(max_length=200, blank=False)
    associated_acts = models.ManyToManyField("self")

    def __unicode__(self):
        return self.name

    #
    # CLASS METHODS
    #
    @classmethod
    def get_or_create_with_url(cls, url):
        """
        The only method you should use for getting/creating Artist
        automatically resolves redirects such as
        www.wiki.com/Drake_(Rapper) & www.wiki.com/Drake_(Entertainer)
        returns a tuple, where the first element is the found/created
        reference, and second element is true iff the reference was just created
        if the url is invalid, then this returns (None, False)
        """
        # Just in case the url is already percentage-encoded,
        # We need to replace %xx escapes by their single-character equivalents
        url = urllib2.unquote(url)

        # First try to find the canonical url offline via the CanonicalUrlCache
        query_set = CanonicalUrlCache.objects.filter(given_url=url)
        if query_set:
            result = Artist.objects.get(url=query_set[0].canonical_url)
            print("[INFO] retrieved %s offline" % result.name)
            return (result, False)

        # Get source code, return none if page not found
        try:
            # For some reason, redirect link does not show up if there are spaces
            # in the url, so we must replace them with underscores
            # Moreover, this method must be able to handle both string type for testing,
            # as well as unicode type for prod
            if type(url) == unicode:
                url = unicode.replace(url, u' ', u'_')
            request = urllib2.urlopen(url)
        except urllib2.HTTPError:
            return (None, False)

        source_code = request.read(40000)

        # Get canonical url
        redirect_pattern = 'wgInternalRedirectTargetUrl":"(.*?)"'
        redirect_subdomain = re.search(redirect_pattern, source_code, re.DOTALL)

        if redirect_subdomain:
            canonical_url = domain + urllib.quote(redirect_subdomain.group(1))
        else :
            canonical_url = urllib.quote(url, safe=':/')

        artist, just_created = cls.objects.get_or_create(url=canonical_url)
        
        # Populate name
        if just_created:
            artist_name_pattern = "<title>(.*?)<\/title>"
            artist_name = re.search(artist_name_pattern, source_code, re.DOTALL).group(1)
            clean_artist_name = artist_name.split('(')[0].split(' - ')[0].rstrip()
            artist.name = clean_artist_name
            artist.image_url = utils.get_artist_image_url(artist.name)
            artist.wiki_name = artist.url.rsplit('/', 1)[1]
            artist.save()

            CanonicalUrlCache(given_url=url, canonical_url=canonical_url).save()
            print("[INFO] cached %s --> %s" % (url, canonical_url))

        return artist, just_created

    @classmethod
    def jsonify(cls, associated_acts, artist):
        """
        example result v2.0 for oboe.js - ducktyping:
            {
               "info": [
                    {"id": "1", "name": "name1", "imageUrl": "http://ecards.connectingsingles.com/photos/ecards/1/ecardu69873_1334.jpg"},
                    {"id": "2", "name": "name2"},
                    {"id": "3", "name": "name3"},
                    {"id": "4", "name": "name1", "imageUrl": "http://ecards.connectingsingles.com/photos/ecards/1/ecardu69873_1334.jpg"},
                    {"id": "5", "name": "name1", "imageUrl": "http://ecards.connectingsingles.com/photos/ecards/1/ecardu69873_1334.jpg"},
                    {"source": "1", "target": "2"},
                    {"source": "1", "target": "3"},
                    {"source": "3", "target": "2"}
               ]
            }
        """
        result = []
        for associated_act in associated_acts:
            result.append(u'{{"id":"{}", "name":"{}", "imageUrl":"{}"}},'.format(associated_act.id, unicode.replace(associated_act.name, u'"', u'\\"'), associated_act.image_url))
            result.append(u'{{"source":"{}", "target":"{}"}},'.format(artist.id, associated_act.id))
        return result

    #
    # INSTANCE METHODS
    #
    def populate(self):
        print("[INFO] populating %s..." % self.name)
        # Get source code
        request = urllib2.urlopen(self.url)
        source_code = request.read(40000)

        # Get list of associated acts as url
        aa_url_pattern = "Associated acts(.*?)<\/td>"
        aa_url_raw = re.search(aa_url_pattern, source_code, re.DOTALL)

        # Entry might be a label and therefore have no associated acts
        # if the above regex returns empty, then there are no associated acts
        if aa_url_raw:
            aa_url = aa_url_raw.group(1)
            href_delimiter_pattern = 'href="(.*?)"'
            aa_url_list = re.findall(href_delimiter_pattern, aa_url, re.DOTALL)

            # There urls are dirty, but will be clean upon artist creation
            associated_acts_urls = [domain + a for a in aa_url_list]

            for associated_act_url in associated_acts_urls:
                associated_act, just_created = Artist.get_or_create_with_url(associated_act_url)
                if associated_act and just_created:
                    associated_act.save()
                    self.associated_acts.add(associated_act)

        self.save()

    def create_generator(self):
        """
        returns a generator which will continuously yeild artist information,
        starting from the artist, then iterating in a breadth-first search fashion
        """
        ITERATIONS = 4
        yield u'{"graphInfo":['
        yield u'{{"id":"{}", "name":"{}", "imageUrl":"{}"}},'.format(self.id, unicode.replace(self.name, u'"', u'\\"'), self.image_url)
        queue = [(self, None)]
        generated_artists = [self]
        for x in range(ITERATIONS):
            source, target = queue.pop(0)
            generated_artists.append(source)
            source.populate()
            associated_acts = filter(lambda artist: artist not in generated_artists, source.associated_acts.all())
            for artist in associated_acts: generated_artists.append(artist)
            for entry in Artist.jsonify(associated_acts, source):
                yield entry
            for artist in associated_acts:
                queue.append((artist, source))
        yield u'{"placeholder": "placeholder"}]}'

class CanonicalUrlCache(models.Model):
    """
    This model exists sole for the purpose of fast, offline lookups.
    Because an Artist's canonical url is the unique identifier (primary key),
    any non-canonical url which redirects to the canonical url should lookup the same artist
    """
    given_url     = models.CharField(max_length=1000, blank=False, unique=True)
    canonical_url = models.CharField(max_length=1000, blank=False, unique=False)
