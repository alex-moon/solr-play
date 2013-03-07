en = open('europarl-v7.lt-en.en', 'r')
lt = open('europarl-v7.lt-en.lt', 'r')

import requests
import json

#f = open('import.csv', 'r')
#requests.post('http://localhost:8080/solr/sekmes/update/csv/?commit=true', f.read())
#exit()

i = j = 0
data = []
for line in iter(en.readline, ''):
    lt_line = lt.readline()
    if line[0] == '(' or lt_line[0] == '(' or line == lt_line:
        continue
    data.append({'id': str(i).zfill(6), 'en': line.strip(), 'lt': lt_line.strip()})
    i += 1
    j += 1
    if j > 1000:
        try:
            response = requests.post('http://localhost:8080/solr/sekmes/update/json/?commit=true', data=json.dumps(data), headers={'Content-Type': 'application/json'})
            if response.status_code != 200:
                print "WARNING: %s" % response.content
            else:
                data = []
                j = 0
        except Exception, e:
            print "ERROR: %s" % e.message

response = requests.post('http://localhost:8080/solr/sekmes/update/json/?commit=true', data=json.dumps(data), headers={'Content-Type': 'application/json'})
print response
