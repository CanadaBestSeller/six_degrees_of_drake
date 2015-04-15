from django.db import models

import urllib
import urllib2
import re
import json

domain = "http://en.wikipedia.org"

class Artist(models.Model):
    # url is the most important field. It must be unique, and
    # it is the single source of information
    # for name and associated acts
    #
    # For now, every Artist has 2 states:
    # 1: Created with only URL populated
    # 2: Metadata & Associated acts are also populated
    url             = models.CharField(max_length=1000, blank=False, unique=True)
    name            = models.CharField(max_length=200)
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
        makes sure that the inputted url is indeed the final redirect (canonical url)
        so that we avoid creating extra instances of Artists, such as 
        www.wiki.com/Drake_(Rapper) & www.wiki.com/Drake_(Entertainer)
        """
        # Get source code
        request = urllib2.urlopen(url)
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

        return artist, just_created

    @classmethod
    def get_jsonified_artists(cls):
        """
        Returns a JSON string of existing artists compatible with d3js graph renderings
        """
        artist_list = []
        for artist in Artist.objects.all():
            artist_list.append({'index': artist.id, 'name': artist.name, 'group': artist.id % 5})
        return json.dumps(artist_list)

    # @classmethod
    # def get_jsonified_relationships(cls):
    #     """
    #     Returns a JSON string of existing artists' relationships compatible with d3js graph renderings
    #     """
    #     artist_list = []
    #     for artist in Artist.objects.all():
    #         artist_list.append({'name': artist.name, 'group': artist.id})
    #     return json.dumps(artist_list)

    #
    # INSTANCE METHODS
    #
    def populate(self):
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
                if just_created:
                    associated_act.save()
                self.associated_acts.add(associated_act)

        self.save()