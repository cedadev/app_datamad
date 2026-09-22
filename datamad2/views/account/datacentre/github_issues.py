# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '11 Dec 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

# Datamad imports
import datamad2.forms as datamad_forms
from datamad2.models import GithubIssueType, GithubSubtask
from datamad2.models.github import GithubSubtask
from datamad2.views.mixins import DatacentreAdminTestMixin, UpdateOrCreateMixin
from datamad2.views.generic import ObjectDeleteView
from datamad2.tables import GithubSubtaskTable

# Django imports
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView
from django.core.exceptions import ObjectDoesNotExist

# Utility imports
from django_tables2.views import SingleTableView


class MyAccountDatacentreGithubIssueTypeView(LoginRequiredMixin, DatacentreAdminTestMixin, UpdateView):
    """
    Provides the view to allow datacentre to map Datamad to the fields they have in
    Github. Used when Users create Github issues.
    """
    template_name = 'datamad2/user_account/account_datacentre_issuetype.html'
    model = GithubIssueType
    form_class = datamad_forms.DatacentreGithubIssueTypeForm

    def get_success_url(self):
        return reverse('github_issue_type')

    def get_object(self, **kwargs):
        """
        Overwrite the get_object method to only display the GithubIssueType object for
        the current logged in users datacentre. This modification also means this view
        behaves as an update or create view. If the object doesn't exist, it will create
        one.
        """
        try:
            return self.model.objects.get(datacentre=self.request.user.data_centre)
        except ObjectDoesNotExist:
            return None

    def get_initial(self):
        initial = super().get_initial()
        if not self.object:
            initial.update({
                'datacentre': self.request.user.data_centre
            })
        return initial


class GithubSubtaskListView(LoginRequiredMixin, SingleTableView):
    """
    List of Github Subtasks which can be attached to Github issues
    """
    model = GithubSubtask
    template_name = 'datamad2/user_account/Githubsubtask_list.html'
    table_class = GithubSubtaskTable

    def get_queryset(self):
        qs = super().get_queryset()
        qs.filter(data_centre=self.request.user.data_centre)

        return qs


class GithubSubtaskUpdateCreateView(LoginRequiredMixin, UpdateOrCreateMixin, UpdateView):
    """
    Github Subtask Update or Create view. If an object with the specified ID exists,
    it opens and edit form, otherwise creation form.

    Form is autofilled with creators Data Centre
    """
    model = GithubSubtask
    template_name = 'datamad2/user_account/Githubsubtask_form.html'
    form_class = datamad_forms.GithubSubtaskForm
    success_url = reverse_lazy('Githubsubtask_list')

    def get_initial(self):
        initial = super().get_initial()
        if not self.object:
            initial.update({
                'data_centre': self.request.user.data_centre
            })
        return initial


class GithubSubtaskDeleteView(DatacentreAdminTestMixin, ObjectDeleteView):
    """
    Delete the Github Subtask
    """
    model = GithubSubtask
    success_url = reverse_lazy('Githubsubtask_list')