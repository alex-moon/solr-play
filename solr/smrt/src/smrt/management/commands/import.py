import os
import csv

from django.core.management.base import BaseCommand

from smrt.models import Area, Article
from smrt.services import SmrtService
from smrt import constants

# handy streaming XML-dict conversion
# https://github.com/martinblech/xmltodict
import xmltodict
import requests
from urllib import quote
import iso8601
import random


class SpringerImporter():
    """
    Imports data from XML RSS feeds into Django and into Solr
    """

    service = SmrtService()

    def do_import(self):
        Article.objects.all().delete()
        for area in Area.objects.all():
            read_url = constants.READER_URL + quote(area.feed_url) + '?n=1000'  # get 1000 records

            print "==================================================="
            print "Now handling area %s" % area.name
            print "==================================================="
            print "Connecting to Google Reader..."

            # @todo: streaming
            feed = requests.get(read_url, headers={'Cookie': constants.COOKIE}).text
            print "Parsing XML..."
            result = xmltodict.parse(feed)
            print "Processing..."
            for doc in result['feed']['entry']:
                if 'summary' in doc:
                    self.add_article(area, doc)
            self.service.commit()

    def add_article(self, area, doc):
        print "- %s" % doc['title']['#text']
        data = {
            'area': area,
            'category': doc['category'][1]['@term'],  # second category is meaningful text
            'title': doc['title']['#text'],
            'published': iso8601.parse_date(doc['published']),
            'updated': iso8601.parse_date(doc['updated']),
            'link': doc['link']['@href'],
            'summary': doc['summary']['#text'],
            'price': random.uniform(1, 100),
            'wordcount': random.randint(800, 8000),
        }
        print "-- to Django"
        article = Article(**data)
        article.save()
        print "-- to Solr"
        self.service.index_article(article)

    def do_reindex(self):
        self.service.delete_all()
        for article in Article.objects.all():
            self.service.index_article(article)
        self.service.commit()


class Command(BaseCommand):

    def handle(self, *args, **options):
        # create Area models if need be
        if Area.objects.all().count() == 0:
            for name, feed_url in constants.AREAS.items():
                Area(name=name, feed_url=feed_url).save()

        # do import
        smrt_import = SpringerImporter()
        if Article.objects.count():
            smrt_import.do_reindex()
        else:
            smrt_import.do_import()
