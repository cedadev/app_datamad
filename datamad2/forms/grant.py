# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '25 Sep 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'


from django import forms
from datamad2.models import Grant, ImportedGrant
from bootstrap_datepicker_plus.widgets import DatePickerInput

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, ButtonHolder, HTML

import math


class UpdateClaimForm(forms.ModelForm):

    class Meta:
        model = Grant
        fields = ('assigned_data_centre',)


class GrantInfoForm(forms.ModelForm):

    date_contacted_pi = forms.DateField(input_formats=['%Y-%m-%d'], label='Date contacted PI', widget=DatePickerInput(), required=False)

    class Meta:
        model = Grant
        fields = (
            'alt_data_contact',
            'alt_data_contact_email',
            'alt_data_contact_phone',
            'other_data_centre',
            'date_contacted_pi',
            'will_grant_produce_data',
            'datasets_delivered',
            'sanctions_recommended',
            'dmp_agreed'
        )


class GrantFieldsExportForm(forms.Form):

    COLUMN_COUNT = 5

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
 
        self.helper = FormHelper()

        grant_excluded_fields = ['ID']

        # Get the grant fields
        for field in Grant._meta.concrete_fields:
            if field.verbose_name not in grant_excluded_fields:
                self.fields[field.name] = forms.BooleanField(label=field.verbose_name.title(), required=False)

        igrant_excluded_fields = ['ID','grant', 'grant ref']

        # Get the imported grant fields
        for field in ImportedGrant._meta.concrete_fields:
            if field.verbose_name not in igrant_excluded_fields:
                self.fields[f'importedgrant.{field.name}'] = forms.BooleanField(label=field.verbose_name.title(), required=False)

        column_length = math.ceil(len(self.fields)/self.COLUMN_COUNT)

        columns = []

        for i in range(self.COLUMN_COUNT):
            field_names = list(self.fields.keys())
            columns.append(
                Div(*field_names[i*column_length:(i+1)*column_length], css_class='col')
            )

        self.helper.layout = Layout(
            Div(*columns, css_class='row'),
            ButtonHolder(
                HTML(f'<button id="id-submit" type="submit" class="btn btn-primary">Export</button>')
            )
        )


















