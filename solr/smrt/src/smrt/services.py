import json
import requests
from urllib import quote

class SmrtService(object):
    SEARCH_FIELDS = [
        'summary',
        'title',
        'category',
    ]

    SOLR_UPDATE_URL = 'http://localhost:8080/solr/smrt/update/json/'
    SOLR_QUERY_URL = 'http://localhost:8080/solr/smrt/query'

    FACET_STRING = '&rows=0&facet=true&facet.field=area'

    def index_article(self, article):
        response = requests.post(
            self.SOLR_UPDATE_URL,
            data=json.dumps([self.to_solr(article)]),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            print "UPDATE QUERY FAILED: %s" % response.content

    def to_solr(self, article):
        return {
            'id': article.pk,
            'area': article.area.name,
            'category': article.category,
            'title': article.title,
            'published': article.published.isoformat() + 'T00:00:00Z',  # .replace('+00:00', 'Z'),
            'updated': article.updated.isoformat().replace('+00:00', 'Z'),
            'link': article.link,
            'summary': article.summary,
            'price': float(article.price),
            'wordcount': article.wordcount
        }

    def get_query_string(self, query='', price_from=0, price_to=100, selected_areas=[]):
        term_query_parts = []
        for field in self.SEARCH_FIELDS:
            for term in query.split(' '):
                term_query_parts.append('%s:"%s"' % (field, term))
        term_query_string = '(' + ' OR '.join(term_query_parts) + ')'

        price_query_string = "price:[%s TO %s]" % (price_from, price_to)

        query_parts = [term_query_string, price_query_string]

        if selected_areas:
            area_parts = []
            for area in selected_areas:
                area_parts.append('area:"%s"' % quote(area))
            area_query_string = '(' + ' OR '.join(area_parts) + ')'

            query_parts.append(area_query_string)

        query_string = ' AND '.join(query_parts)

        print "DEBUG: %s" % query_string

        return query_string

    def get_area_facets(self, query='', price_from=0, price_to=100):
        query_string = self.get_query_string(query, price_from, price_to, [])
        response = requests.get(
            self.SOLR_QUERY_URL + ('?q=%s' % query_string) + self.FACET_STRING
        )
        if response.status_code != 200:
            print "FACETS QUERY FAILED: %s" % response.content
            return []
        else:
            data = json.loads(response.content)
            return data['facet_counts']['facet_fields']['area']

    def get_results(self, query='', price_from=0, price_to=100, selected_areas=[]):
        query_string = self.get_query_string(query, price_from, price_to, selected_areas)
        response = requests.get(
            self.SOLR_QUERY_URL + ('?q=%s' % query_string)
        )
        if response.status_code != 200:
            print "RESULTS QUERY FAILED: %s" % response.content
            return []
        else:
            data = json.loads(response.content)
            docs = data['response']['docs']
            return docs

            """
            # This is not working as expected alas
            highlights = data['highlighting'].values()
            for doc, highlight in zip(docs, highlights):
                doc['summary'] = highlight['summary'][0]
            return docs
            """

    def delete_all(self):
        response = requests.post(
            self.SOLR_UPDATE_URL,
            data=json.dumps({'delete': {'query': '*:*'}}),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            print "DELETE FAILED: %s" % response.content
        self.commit()

    def commit(self):
        response = requests.post(self.SOLR_UPDATE_URL + '?commit=true')
        if response.status_code != 200:
            print "COMMIT FAILED: %s" % response.content
