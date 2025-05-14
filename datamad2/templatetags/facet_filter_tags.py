# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '27 Jul 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from datamad2.search_indexes import GrantIndex
from datamad2.forms.preferences import facet_fields
from django import template
from datamad2.utils import removesuffix
from django.template.loader import get_template
import urllib.parse

register = template.Library()


@register.simple_tag
def available_facets(request):
    """
    Return the available facets which have not been set as preferences
    :param request:
    :return:
    """
    igx = GrantIndex()

    fields = facet_fields
    preferences = request.user.preferences
    facet_preferences = preferences.get('preferred_facets',[])
    avail_facets = []
    for field in fields:
        if field not in facet_preferences:
            avail_facets.append(field)

    return [field for field in fields if field not in facet_preferences]


@register.simple_tag(takes_context=True)
def selected_facets(context):
    request = context.request
    selected_facets = request.GET.getlist('selected_facets')
    converted_facets = {}

    for facet in selected_facets:
        f, label = facet.split(':', 1)
        title = f.replace('_', ' ').title()
        converted_facets[title] = label

    if converted_facets:
        template = get_template('datamad2/includes/selected_facets.html')
        return template.render({'converted_facets': converted_facets})
    
    return ''


@register.simple_tag
def facet_filter_url(request, field, facet):
    """
    Generate the url for the facet filters
    :param request: WSGIRequest
    :param field: field to narrow
    :param facet: facet value
    :return: url to narrow on
    """
    path = request.path

    # Make a copy so can modify it
    if request.GET:
        qs_copy = request.GET.copy()
        if qs_copy.get('page'):
            qs_copy.pop('page')

        # Popping the page number can make the querystring 0 length
        if qs_copy:
            qs = f'?{qs_copy.urlencode()}&selected_facets={field}:{urllib.parse.quote(facet[0])}'
        else:
            qs = f'?selected_facets={field}:{urllib.parse.quote(facet[0])}'

    else:
        qs = f'?selected_facets={field}:{urllib.parse.quote(facet[0])}'

    return f'{path}{qs}'
