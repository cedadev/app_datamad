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
import numpy as np
import math
from dateutil.parser import parse
import datetime
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


    def temp():
         ...
   
    # SQL query to pull information needed by DataMAD, also renames to DataMad names.
    # TODO, update so that it only pulls from last week unless additional argument is passed
    # TODO remove limit once it has been checked that it works
    def custom_databank_datamad_sql_query(self):
        # TODO, try and get PI field (LEAD_GRANT) populated in some way
        sql_datamad_renamed = "SELECT \
                    fact_application.ApplicationID AS GRANTREFERENCE, \
                    fact_application.ApplicationTitle AS PROJECT_TITLE, \
                    dim_scheme.SchemeName AS SCHEME, \
                    dim_opportunity.OpportunityName AS 'CALL', \
                    dim_scheme.SchemeType AS GRANT_TYPE, \
                    dim_person.FullName AS GRANT_HOLDER, \
                    fact_application_team.TeamMemberRole AS TEAM_MEMBER_ROLE, \
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
                    LEFT OUTER JOIN  fact_application_team \
                            ON fact_application.ApplicationSKey = fact_application_team.ApplicationSKey \
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
                    LIMIT 200"
        return sql_datamad_renamed
    

    def dictfetchall(self, cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
        ]


    def handle(self, *args, **options):
        if options.get('lookback'):
            sql_command = self.temp()
        else:
            # TODO, amend SQL query to include date range to look for new/ changed grants
            sql_command = self.custom_databank_datamad_sql_query()

        with connections["DataBank"].cursor() as cursor:
            cursor.execute(sql_command)
            row = self.dictfetchall(cursor)

        # Creation of dataframe with 
        df = pd.DataFrame(row)

        # Populate n_cols, columns which have boolean True/False values
        n_cols = ["NCAS", "NCEO", "LEAD_GRANT"]
        df = df.reindex(columns=[*df.columns.tolist(), *n_cols], fill_value='N')

        # Use TEAM_MEMBER_ROLES to populate LEAD_GRANT and potentially PARENT_GRANT
        df.loc[df.TEAM_MEMBER_ROLE == "Principal Investigator", "LEAD_GRANT"] = "Y" # Change LEAD_GRANT to Y if TEAM_MEMBER_ROLE is PI
        df = df.drop("TEAM_MEMBER_ROLE", axis=1) # Delete TEAM_MEMBER_ROLE, no longer needed

        # Replace columns missing in DataBank, that were in DataMad to maintain compatibility with DataMad
        no_longer_needed_cols = ['WORK_NUMBER', 'ADDRESS2', 'OVERALL_SCORE', 
                                'PROPOSED_ST_DT_ORG', 'PROPOSED_END_DT_ORG'] # NaN cols
        df = df.reindex(columns=[*df.columns.tolist(), *no_longer_needed_cols], fill_value=np.nan)

        needed_cols = ['FACILITY', 'PARENT_GRANT', 'OBJECTIVES']
        df = df.reindex(columns=[*df.columns.tolist(), *needed_cols], fill_value="")

        # Reorder columns to Siebel order (easier to read for user, not needed for import via Django)
        col_order = ['GRANTREFERENCE', 'PROJECT_TITLE', 'LEAD_GRANT', 'PARENT_GRANT',
                        'SCHEME', 'CALL', 'GRANT_TYPE',
                        'GRANT_HOLDER', 'WORK_NUMBER', 'EMAIL', 'RESEARCH_ORG',
                        'DEPARTMENT', 'ACTUAL_START_DATE', 'ACTUAL_END_DATE',
                        'NCAS', 'NCEO', 'PROPOSED_ST_DT', 'PROPOSED_END_DT',
                        'GRANT_STATUS', 'ADDRESS1', 'ADDRESS2', 'CITY',
                        'POSTCODE', 'AMOUNT',
                        'ROUTING_CLASSIFICATION', 'SCIENCE_AREA',
                        'GEOGRAPHIC_AREA', 'SECONDARY_CLASSIFICATION',
                        'ABSTRACT', 'OBJECTIVES', 'FACILITY', 'OVERALL_SCORE',
                        'PROPOSED_ST_DT_ORG', 'PROPOSED_END_DT_ORG']

        df = df[col_order]

        # Delete rows which are complete complete duplicates, ordering by "LEAD_GRANT" to ensure that any LEAD_GRANT "Y" are kept (happens due to LEAD_GRANT
        # column because of the database table it was queried from, generally LEAD_GRANT Y has a lot of "N" duplicate rows as 
        # fact_application_team contains additional (non-duplicate) information which is not needed by DataMad)
        df = df.sort_values(by=['LEAD_GRANT'], ascending=False)
        df = df.drop_duplicates(subset=df.columns.difference(['LEAD_GRANT']), keep='first')

        # Create mapping to go from renamed DataBank fields to CEDA DataMad database
        mapping = {
                'GRANTREFERENCE': 'grant_ref',
                'PROJECT_TITLE': 'title',
                'SCHEME': 'scheme',
                'CALL': 'call',
                'GRANT_TYPE': 'grant_type',
                'GRANT_HOLDER': 'grant_holder',
                'WORK_NUMBER': 'work_number',
                'EMAIL': 'email',
                'RESEARCH_ORG': 'research_org',
                'DEPARTMENT': 'department',
                'ACTUAL_START_DATE': 'actual_start_date',
                'ACTUAL_END_DATE': 'actual_end_date',
                'NCAS': 'ncas',
                'NCEO': 'nceo',
                'PROPOSED_ST_DT': 'proposed_start_date',
                'PROPOSED_END_DT': 'proposed_end_date',
                'GRANT_STATUS': 'grant_status',
                'ADDRESS1': 'address1',
                'ADDRESS2': 'address2',
                'CITY': 'city',
                'POSTCODE': 'post_code',
                'LEAD_GRANT': 'lead_grant',
                'AMOUNT': 'amount_awarded',
                'ROUTING_CLASSIFICATION': 'routing_classification',
                'SCIENCE_AREA': 'science_area',
                'SECONDARY_CLASSIFICATION': 'secondary_classification',
                'ABSTRACT': 'abstract',
                'OBJECTIVES': 'objectives',
                'FACILITY': 'facility',
                'OVERALL_SCORE': 'overall_score'
                }
        


        # Checks on incoming data
        for row in tqdm(df.itertuples(), desc='Importing grants'):
            data = {}

            for source_field, model_field in mapping.items():

                value = getattr(row, source_field)

                # Ignore None value
                if value is None:
                    continue

                # Ignore nan values (if they aren't strings or datetime)
                if not isinstance(value, datetime.date):
                        if not isinstance(value, str) and math.isnan(value):
                                continue

                if source_field in ('LEAD_GRANT', 'NCAS', 'NCEO'):
                    # Turn into boolean
                    value = bool('y' in value.lower())

                elif source_field in ('PROPOSED_ST_DT', 'PROPOSED_END_DT', 'ACTUAL_START_DATE', 'ACTUAL_END_DATE'):
                    # Ensure the date is converted correctly (although DataBank should always give datetime fields for the above)
                    if not isinstance(value, datetime.date):
                        value = parse(value, default=None).date()

                # Add to the data dict
                data[model_field] = value

            ig = ImportedGrant(**data)

            # Generate list of fields to check. These fields come from grant import
            model_fields = [model_field for source_field, model_field in mapping.items()]

            # TODO For now remove the fields below from model_fields
            # Otherwise the correct values previously imported from Siebel via UKCEH will be overwritten by default
            # NaNs/ ""/ "N" values written for DataBank import
            do_not_check = ["ncas", "nceo", "lead_grant", 'work_number', 'address2', 'overall_score', 
                            'proposed_st_dt_org', 'proposed_end_dt_org', 'facility', 'parent_grant', 'objectives']
            model_fields = [e for e in model_fields if e not in do_not_check]

            grant_ref = row.GRANTREFERENCE

            try:
                existing_G = Grant.objects.get(grant_ref=grant_ref)
                existing_ig = existing_G.importedgrant
                changed_fields = list(filter(
                    lambda field: getattr(existing_ig, field, None) != getattr(ig, field, None), model_fields))

                if len(changed_fields) > 0:
                    ig.save()

                else:
                    pass

            except ObjectDoesNotExist:
                ig = ImportedGrant(**data)
                ig.save()

        # Attach parent child relationships
        for row in tqdm(df.itertuples(), desc='Making parent child connections'):
            parent_grant = row.PARENT_GRANT
            row_grant = row.GRANTREFERENCE

            # Ignore NaN values
            if not isinstance(parent_grant, str) and math.isnan(parent_grant):
                continue

            try:
                pg = Grant.objects.get(grant_ref=parent_grant)
            except ObjectDoesNotExist:
                print(f'Parent Grant {parent_grant} does not exist.')
                pg = None

            # Get grant to add parent grant to
            grant = Grant.objects.filter(grant_ref=row_grant).first()

            if pg and grant:
                grant.parent_grant = pg
                grant.save()
