# encoding: utf-8
"""
View for the Datamad home page
"""
__author__ = 'Richard Smith'
__date__ = '10 Dec 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

# Datamad imports
import datamad2.forms as datamad_forms
from datamad2.tables import GrantTable

# Django imports
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse

# Utility imports
from haystack.generic_views import FacetedSearchView

import django.utils.decorators
import django.views.decorators.csrf


@django.utils.decorators.method_decorator(django.views.decorators.csrf.ensure_csrf_cookie, name="dispatch")
class FacetedGrantListView(LoginRequiredMixin, FacetedSearchView):
    """
    Faceted search list view of all grants using Django Haystack
    """
    form_class = datamad_forms.DatamadFacetedSearchForm
    facet_fields = datamad_forms.preferences.facet_fields
    template_name = 'datamad2/grant_list.html'

    def get_table(self, context):
        return GrantTable(data=[item.object for item in context['page_obj'].object_list], orderable=False)

    def get_queryset(self):
        options = {
            "size": settings.HAYSTACK_FACET_LIMIT,
            "order": {"_key": "asc"}
        }
        qs = super().get_queryset()
        for field in self.facet_fields:
            qs = qs.facet(field, **options)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add the facet fields to define an order of the facets
        context['facet_fields'] = self.facet_fields
        context['table'] = self.get_table(context)
        context['containerfluid'] = True
        return context

    def get(self, request, *args, **kwargs):
        user_preferred_sorting = request.user.preferences.get('preferred_sorting', None)

        query_dict = request.GET.copy()

        # Add the users default sorting, if not already set
        if not request.GET.get('sort_by') and user_preferred_sorting:
            query_dict.update({'sort_by': user_preferred_sorting})
            return HttpResponseRedirect(f'{reverse("grant_list")}?{query_dict.urlencode()}')

        return super().get(request, *args, **kwargs)
