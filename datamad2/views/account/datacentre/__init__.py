# encoding: utf-8
"""
Package which contains views for managing the datacentre specific customisations.
This includes JIRA Issues and document templating.
"""
__author__ = 'Richard Smith'
__date__ = '11 Dec 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from .data_format import DataFormatListView, DataFormatUpdateCreateView, DataFormatDeleteView
from .datacentre import MyAccountDatacentreView
from .document_templating import DocumentTemplateListView, DocumentTemplateCreateView, DocumentTemplateUpdateView, DocumentTemplateDeleteView
from .jira_issues import MyAccountDatacentreJIRAIssueTypeView, JIRASubtaskListView, JIRASubtaskUpdateCreateView, JIRASubtaskDeleteView
from .github_issues import MyAccountDatacentreGithubIssueTypeView, GithubSubtaskListView, GithubSubtaskUpdateCreateView, GithubSubtaskDeleteView
from .preservation_plan import PreservationPlanListView, PreservationPlanUpdateCreateView, PreservationPlanDeleteView