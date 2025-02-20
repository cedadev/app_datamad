# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '25 Sep 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from haystack.forms import FacetedSearchForm
from django import forms
from crispy_forms.helper import FormHelper

class DatamadFacetedSearchForm(FacetedSearchForm):
    CHOICES = (
        (None, 'Relevance'),
        ('date_added', 'Date Added (asc)'),
        ('-date_added', 'Date Added (desc)'),
        ('actual_start_date', 'Start Date (asc)'),
        ('-actual_start_date', 'Start Date (desc)'),
        ('grant_ref_exact', 'Grant Ref (A-Z)'),
        ('-grant_ref_exact', 'Grant Ref (Z-A)'),
        ('ukri_ref_exact', 'UKRI ID (A-Z)'),
        ('-ukri_ref_exact', 'UKRI ID (Z-A)'),
        ('nerc_ref_exact', 'NERC ID (A-Z)'),
        ('-nerc_ref_exact', 'NERC ID (Z-A)'),
        ('grant_title_exact', 'Grant Title (A-Z)'),
        ('-grant_title_exact', 'Grant Title (Z-A)'),
        ('grant_holder_exact', 'Grant Holder (A-Z)'),
        ('-grant_holder_exact', 'Grant Holder (Z-A)'),
    )

    sort_by = forms.ChoiceField(choices=CHOICES, required=False,
                                widget=forms.Select(attrs={"onchange":"trigger_submit(this)"}))

    show_hidden = forms.BooleanField(label='Show Hidden Grants', required=False,
                                     widget=forms.CheckboxInput(attrs={"onchange":"trigger_submit(this)"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method='get'
        self.helper.form_class='ml-0'
        self.helper.form_id='search_form'

    def no_query_found(self):
        """
        Determines the behavior when no query was found.

        By default, no results are returned (``EmptySearchQuerySet``).

        Should you want to show all results, override this method in your
        own ``SearchForm`` subclass and do ``return self.searchqueryset.all()``.
        """
        return self.searchqueryset.all()

    def search(self):
        sqs = super(DatamadFacetedSearchForm, self).search()

        if self.cleaned_data['sort_by']:
            order = self.cleaned_data['sort_by']
            sqs = sqs.order_by(order)

        if not self.cleaned_data['show_hidden']:
            sqs = sqs.filter(visible=True)

        return sqs
    