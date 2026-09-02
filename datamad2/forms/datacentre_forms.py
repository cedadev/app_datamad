# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '25 Sep 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from django import forms
from datamad2.models import DataCentre, User, JIRAIssueType, GithubIssueType, DocumentTemplate, Subtask
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from datamad2.forms.mixins import CrispySubmitMixin


class DatacentreForm(CrispySubmitMixin, forms.ModelForm):

    class Meta:
        model = DataCentre
        fields = '__all__'


class NewUserForm(CrispySubmitMixin, forms.ModelForm):
    """
    Generates a random first-time password on account
    creation. The User then has to reset this to login
    for the first time.
    """
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'data_centre', 'is_admin')

    def save(self, commit=True):
        user = super().save(commit=False)

        user.set_unusable_password()

        if commit:
            user.save()
        return user


class UserEditForm(CrispySubmitMixin, forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'is_admin')
        exclude = ('password',)


class DatacentreJIRAIssueTypeForm(CrispySubmitMixin, forms.ModelForm):
    class Meta:
        model = JIRAIssueType
        fields = '__all__'

class DatacentreGithubIssueTypeForm(CrispySubmitMixin, forms.ModelForm):
    class Meta:
        model = GithubIssueType
        fields = '__all__'

class DocumentTemplateForm(CrispySubmitMixin, forms.ModelForm):
    class Meta:
        model = DocumentTemplate
        fields = '__all__'

        widgets = {
            'datacentre': forms.HiddenInput
        }


class DocumentGenerationForm(forms.Form):
    document_template = forms.ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        datacentre = kwargs.pop('datacentre', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Generate'))

        self.fields['document_template'].queryset = DocumentTemplate.objects.filter(datacentre=datacentre)


class JIRASubtaskForm(CrispySubmitMixin, forms.ModelForm):
    class Meta:
        model= Subtask
        fields = '__all__'

        widgets = {
            'data_centre': forms.HiddenInput
        }

class GithubSubtaskForm(CrispySubmitMixin, forms.ModelForm):
    class Meta:
        model= Subtask
        fields = '__all__'

        widgets = {
            'data_centre': forms.HiddenInput
        }
