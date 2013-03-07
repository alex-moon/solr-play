from django.conf import settings
from django.views.generic import FormView, TemplateView, View, RedirectView
from django.http import HttpResponse

from smrt.services import SmrtService

from collections import OrderedDict

class SmrtView(TemplateView):
    template_name = 'smrt.html'
    service = SmrtService()

    def get_context_data(self, *args, **kwargs):
        price_from = self.request.GET.get('price_from', 0.00)
        price_to = self.request.GET.get('price_to', 100.00)
        selected_areas = self.request.GET.getlist('areas')
        query = self.request.GET.get('query', '')
        context = {
            'price_from': price_from,
            'price_to': price_to,
            'areas': self.get_areas(query, price_from, price_to, selected_areas),
            'query': query,
            'results': self.service.get_results(query, price_from, price_to, selected_areas),
        }
        return context

    def get_areas(self, query='', price_from=0, price_to=100, selected_areas=[]):
        # expects: ['Economics', 10, 'Sciences', 4, ...]
        # returns: [{'Economics': (10, False)}, {'Sciences': (4, True)}, ...] where False and True refer to selected
        area_facets = self.service.get_area_facets(query, price_from, price_to)
        areas = OrderedDict()

        for area, count in sorted(zip(area_facets[0::2], area_facets[1::2])):
            areas.update({area: (count, area in selected_areas)})

        return areas
