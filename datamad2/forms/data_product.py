# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '25 Sep 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from django import forms
from datamad2.models import DataProduct, Grant
from datamad2.models.data_management_plans import PreservationPlan, DataFormat
from bootstrap_datepicker_plus.widgets import DatePickerInput

from datamad2.forms.mixins import CrispySubmitMixin


class DataProductBaseFormMixin(CrispySubmitMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grant_id'] = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def save(self, **kwargs):
        # Save the related grant for this data product
        self.instance.grant = Grant.objects.get(pk=self.cleaned_data['grant_id'])
        return super().save()


class DataProductMetaBase:
    widgets = {
        'data_product_type': forms.HiddenInput,
        'delivery_date': DatePickerInput(options={'format':'DD/MM/YYYY'}),
        'embargo_date': DatePickerInput(options={'format':'DD/MM/YYYY'})
    }

    fields = ['data_product_type']


class DigitalDataProductForm(DataProductBaseFormMixin, forms.ModelForm):

    delivery_date = forms.DateField(input_formats=['%Y-%m-%d'], widget=DatePickerInput(), required=False)
    embargo_date = forms.DateField(input_formats=['%Y-%m-%d'], widget=DatePickerInput(), required=False)

    class Meta(DataProductMetaBase):
        model = DataProduct
        fields = [
            'description',
            'contact',
            'data_volume',
            'delivery_date',
            'embargo_date',
            'doi',
            'preservation_plan',
            'data_format',
            'additional_comments',
        ] + DataProductMetaBase.fields


class ModelSourceDataProductForm(DataProductBaseFormMixin, forms.ModelForm):
    class Meta(DataProductMetaBase):
        model = DataProduct
        fields = [
            'name',
            'contact',
            'description',
            'data_location',
            'additional_comments'
        ] + DataProductMetaBase.fields


class PhysicalDataProductForm(DataProductBaseFormMixin, forms.ModelForm):

    delivery_date = forms.DateField(input_formats=['%Y-%m-%d'], widget=DatePickerInput(), required=False)

    class Meta(DataProductMetaBase):
        model = DataProduct
        fields = [
            'name',
            'contact',
            'data_format',
            'sample_destination',
            'additional_comments'
        ] + DataProductMetaBase.fields


class HardcopyDataProductForm(DataProductBaseFormMixin, forms.ModelForm):

    delivery_date = forms.DateField(input_formats=['%Y-%m-%d'], widget=DatePickerInput(), required=False)

    class Meta(DataProductMetaBase):
        model = DataProduct
        fields = [
            'name',
            'contact',
            'data_format',
            'issues',
            'delivery_date',
            'additional_comments'
        ] + DataProductMetaBase.fields


class ThirdPartyDataProductForm(DataProductBaseFormMixin, forms.ModelForm):
    class Meta(DataProductMetaBase):
        model = DataProduct
        fields = [
            'name',
            'contact',
            'data_location',
            'description',
            'data_volume',
            'responsibility',
            'issues',
            'additional_comments'
        ] + DataProductMetaBase.fields


class PreservationPlanForm(CrispySubmitMixin, forms.ModelForm):

    class Meta:
        model = PreservationPlan
        fields = '__all__'

        widgets = {
            'datacentre': forms.HiddenInput
        }


class DataFormatForm(CrispySubmitMixin, forms.ModelForm):

    class Meta:
        model = DataFormat
        fields = '__all__'

        widgets = {
            'datacentre': forms.HiddenInput
        }