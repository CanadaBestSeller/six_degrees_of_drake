from django.db import models

import urllib
import urllib2
import re

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

    def populate(self):
        # Get source code
        request = urllib2.urlopen(self.url)
        source_code = request.read(40000)

        # Populate name
        artist_name_pattern = "<title>(.*?)<\/title>"
        artist_name = re.search(artist_name_pattern, source_code, re.DOTALL).group(1)
        clean_artist_name = artist_name.split('(')[0].split(' - ')[0].rstrip()
        self.name = clean_artist_name

        # Get list of associated acts as url
        domain = "http://en.wikipedia.org"
        aa_url_pattern = "Associated acts(.*?)<\/td>"
        aa_url_raw = re.search(aa_url_pattern, source_code, re.DOTALL)

        # Entry might be a label and therefore have no associated acts
        # if the above regex returns empty, then there are no associated acts
        if aa_url_raw:
            aa_url = aa_url_raw.group(1)
            href_delimiter_pattern = 'href="(.*?)"'
            aa_url_list = re.findall(href_delimiter_pattern, aa_url, re.DOTALL)

            associated_acts_urls = [domain + urllib.quote(a) for a in aa_url_list]

            for associated_act_url in associated_acts_urls:
                associated_act, created = Artist.objects.get_or_create(url=associated_act_url)
                if not created:
                    associated_act.save()
                self.associated_acts.add(associated_act)

        self.save()
