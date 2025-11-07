# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '25 Sep 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from django import forms
from datamad2.models import Document


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ('upload', 'tags')


class MultipleDocumentUploadForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ('upload',)

    upload = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True}))