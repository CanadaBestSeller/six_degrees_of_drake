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
        automatically resolves redirects such as
        www.wiki.com/Drake_(Rapper) & www.wiki.com/Drake_(Entertainer)
        returns a tuple, where the first element is the found/created
        reference, and second element is true iff the reference was just created
        if the url is invalid, then this returns (None, False)
        """
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

        return artist, just_created

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
                if associated_act and just_created:
                    associated_act.save()
                    self.associated_acts.add(associated_act)

        self.save()

    def self_node_json(self):
        """
        Returns a JSON compatible with d3js grphs
        Contains ONLY the node information of self
        """
        return json.dumps({'id': self.id, 'name': self.name, 'group': self.id % 10})

    def nodes_json(self):
        """
        Returns a JSON compatible with d3js graphs
        Contains node information of self and associated acts
        """
        nodes = []
        nodes.append({'id': self.id, 'name': self.name, 'group': self.id % 10})

        for associated_act in self.associated_acts.all():
            nodes.append({'id': associated_act.id, 'name': associated_act.name, 'group': associated_act.id % 10})
        return json.dumps(nodes)

    def links_json(self):
        """
        Returns a JSON compatible with d3js graphs
        Contains relationship information of self and associated acts
        """
        links = []

        for associated_act in self.associated_acts.all():
            links.append({'source': self.id, 'target': associated_act.id, 'value': 1}) # TODO: value func

        return json.dumps(links)
