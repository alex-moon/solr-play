import os
import csv

from django.core.management.base import BaseCommand
from django.utils.encoding import smart_unicode

from smrt.models import Area, Article

# handy streaming XML-dict conversion
# https://github.com/martinblech/xmltodict
import xmltodict
import requests
import random
import json

SOLR_UPDATE_URL = 'http://localhost:8080/solr/smrt/update/json/?commit=true'

class Command(BaseCommand):

    def handle(self, *args, **options):
        response = requests.post(SOLR_UPDATE_URL, data=json.dumps([data]), headers={'Content-Type': 'application/json'})
        if response.status_code != 200:
            print "WARNING: %s" % response.content
