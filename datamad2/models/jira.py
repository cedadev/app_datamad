# encoding: utf-8
"""
Django models relating to the JIRA connection.
"""
__author__ = 'Richard Smith'
__date__ = '10 Dec 2020'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'


# Django imports
from django.db import models

# Datamad imports
from .users import DataCentre, User
from .grants import Grant


# Python imports

class JIRATicket(models.Model):
    grant = models.ForeignKey(Grant, on_delete=models.CASCADE)
    datacentre = models.ForeignKey(DataCentre, on_delete=models.CASCADE)
    url = models.URLField()

    def __str__(self):
        return self.url


class JIRAIssueType(models.Model):
    """
    Maps the datamad model fields to the fields in the Datacentre's JIRA
    Data Management Tracking JIRA IssueType
    """
    datacentre = models.ForeignKey(DataCentre, on_delete=models.CASCADE)
    issuetype = models.IntegerField(
        help_text='JIRA Data Management issue type ID. e.g. 10602',
        blank=True,
        null=True,
        verbose_name='Issue Type Id'
    )
    reporter = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text='User to set as the reporter for all JIRA issues. If left blank the reporter will be the user'
                  ' that creates the issue.'
    )
    start_date_field = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Actual Start Date Field ID',
        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )
    end_date_field = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Actual End Date Field ID',

        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )
    proposed_start_date_field = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Proposed Start Date Field ID',

        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )
    proposed_end_date_field = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Proposed End Date Field ID',

        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )
    grant_ref_field = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Grant Ref Field ID',

        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )
    nerc_id_field = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='NERC ID Field ID',

        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )

    pi_field = models.CharField(
        max_length=100,
        verbose_name='Principle Investigator Field ID',
        blank=True,

        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )
    research_org_field = models.CharField(
        max_length=100,
        verbose_name='Research Org Field ID',
        blank=True,

        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )
    primary_datacentre_field = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Primary Datacentre Field ID',

        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )
    amount_awarded_field = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Amount Awarded Field ID',

        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )
    grant_type_field = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Grant Type Field ID',

        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )
    lead_grant_field = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Lead Grant Field ID',

        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )
    parent_grant_field = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Parent Grant Field ID',

        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )
    child_grants_field = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Child Grants Field ID',

        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )
    email_field = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Email Field ID',

        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )
    work_number_field = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Work Number Field ID',

        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )
    alt_data_contact_field = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Alt Data Contact Field ID',

        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )
    alt_data_contact_email_field = models.CharField(
        max_length=50,
        blank=True,

        verbose_name='Alt Data Contact Email Field ID',

        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )
    other_datacentre_field = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Other Datacentre Field ID',

        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )

    call_field = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Call Field ID',
        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )

    scheme_field = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Scheme Field ID',
        help_text='Format: customfield_{{number}} | Returned DataType: String'
    )


    @property
    def jira_issue_fields(self):
        issue_fields = {k: v for k, v in self.__dict__.items() if k.endswith('field') and v}
        return issue_fields


class Subtask(models.Model):
    """
    Model to create a template for JIRA subtasks. These subtasks are Datacentre specific
    """
    data_centre = models.ForeignKey(to=DataCentre, on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    schedule_time = models.IntegerField(blank=True, null=True,
                                        help_text='Time in weeks to at which to schedule sub-task in reference to the reference time. '
                                                  'Using a negative value schedules the task before the reference time',
                                        verbose_name='Schedule at')  # in weeks
    ref_time = models.CharField(max_length=200, blank=True, null=True,
                                choices=(("start_date", "Start Date"), ("end_date", "End Date")), help_text=
                                'Start date means the sub-task will be scheduled in reference to the start date. End date means it will be scheduled in reference to the end date.',
                                verbose_name='Reference time')

    def __str__(self):
        return f"{self.name}"
