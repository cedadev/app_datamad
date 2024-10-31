# encoding: utf-8
"""
Import the latest data from the UKRI Databank database into the Datamad database

Based on import_database script written by Richard Smith
"""
__author__ = 'Matthew Paice'
__date__ = '29 Oct 2024'
__copyright__ = 'Copyright 2024 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'matthew.paice@stfc.ac.uk'

from django.core.management.base import BaseCommand
from datamad2.models import ImportedGrant, Grant
from django.db import connections

import pandas as pd
import math
from dateutil.parser import parse
from tqdm import tqdm
from django.core.exceptions import ObjectDoesNotExist
import io
import requests
from requests.auth import HTTPBasicAuth

# TODO, change SQL query to ORM, after initial check that the script works (M. Paice far more familiar with SQL at this moment in time 30-Oct-2024 so easier to debug with SQL that I know works).
class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        input_group = parser.add_mutually_exclusive_group()
        input_group.add_argument('--lookback', help='Time to look back in DataBank to update DataMad')

    def handle(self, *args, **options):
        if options.get('lookback'):
            ...
            # TODO, amend SQL query to include date range to look for new/ changed grants

    # SQL query to pull information needed by DataMAD, also renames to DataMad names.
    # TODO, update so that it only pulls from last week unless additional argument is passed
    # TODO remove limit once it has been checked that it works
    def custom_databank_datamad_sql_query(self, sql_command):
        sql_datamad_renamed = "SELECT \
                    fact_application.ApplicationID AS GRANTREFERENCE, \
                    fact_application.ApplicationTitle AS PROJECT_TITLE, \
                    dim_scheme.SchemeName AS SCHEME, \
                    dim_opportunity.OpportunityName AS 'CALL', \
                    dim_scheme.SchemeType AS GRANT_TYPE, \
                    dim_person.FullName AS GRANT_HOLDER, \
                    dim_person.Email AS EMAIL, \
                    dim_organisation.OrganisationName AS RESEARCH_ORG, \
                    dim_department.DepartmentName AS DEPARTMENT, \
                    dim_application_date.ActualStartDate AS ACTUAL_START_DATE, \
                    dim_application_date.ActualEndDate AS ACTUAL_END_DATE, \
                    fact_application.AdministratingCouncil AS NEW_ADMINISTRATING_COUNCIL, \
                    dim_application_date.ProposedStartDate AS PROPOSED_ST_DT, \
                    dim_application_date.ProposedEndDate AS PROPOSED_END_DT, \
                    fact_application.ApplicationStatus AS GRANT_STATUS, \
                    dim_organisation.AddressLine1 AS ADDRESS1, \
                    dim_organisation.TownOrCity AS CITY, \
                    dim_organisation.PostCode AS POSTCODE, \
                    fact_application.AwardedAmount AS 'AMOUNT', \
                    dim_application_ext.RoutingClassification AS ROUTING_CLASSIFICATION, \
                    dim_classification_area.SubjectArea AS SCIENCE_AREA, \
                    dim_organisation.region AS GEOGRAPHIC_AREA, \
                    dim_classification_area.ResearchTopic AS SECONDARY_CLASSIFICATION, \
                    dim_application_ext.ApplicationSummary AS ABSTRACT \
                    FROM fact_application \
                    LEFT OUTER JOIN  dim_scheme \
                            ON fact_application.SchemeSKey = dim_scheme.SchemeSKey \
                    LEFT OUTER JOIN dim_opportunity \
                            ON fact_application.OpportunitySKey = dim_opportunity.OpportunitySKey \
                    LEFT OUTER JOIN dim_person \
                            ON fact_application.ApplicantPersonSKey = dim_person.PersonSKey \
                    LEFT OUTER JOIN dim_department \
                            ON fact_application.OrganisationDepartmentSKey = dim_department.OrganisationDepartmentSKey \
                    LEFT OUTER JOIN dim_application_date  \
                            ON fact_application.ApplicationSKey = dim_application_date.ApplicationSKey \
                    LEFT OUTER JOIN  dim_organisation\
                            ON fact_application.LeadOrganisationSKey = dim_organisation.OrganisationSKey \
                    LEFT OUTER JOIN  dim_application_ext\
                            ON fact_application.ApplicationSKey = dim_application_ext.ApplicationSKey \
                    LEFT OUTER JOIN dim_classification_area \
                            ON fact_application.PrimaryClassificationAreaSKey = dim_classification_area.ClassificationAreaSKey \
                    WHERE fact_application.AdministratingCouncil = 'NERC' AND fact_application.ApplicationStatus = 'ACCEPTED' \
                    GROUP BY  fact_application.ApplicationID \
                    LIMIT 200"


        with connections["databank"].cursor() as cursor:
            cursor.execute(sql_command)
            row = cursor.fetchall()

        return row
