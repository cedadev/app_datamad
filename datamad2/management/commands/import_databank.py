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

# TODO, change SQL query to ORM, after initial check that the script works (M. Paice far more familiar with SQL at this moment in time 30-Oct-2024 so easier to debug with SQL that I know works).
class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        input_group = parser.add_mutually_exclusive_group()
        input_group.add_argument('--lookback', help='Time to look back in DataBank to update DataMad')

    @staticmethod
    def hybrid_tfs_siebel_list():
        hybrid_tfs_siebel = [3256, 3299, 3445, 3674, 3762, 3774, 3793, 3839, 3871, 6840, 7536, 9989, 11522, 
                            12787, 12879, 13526, 13690, 13833, 14767, 14774, 14868, 14965, 15230, 15269, 
                            15461, 15552, 15818, 17496, 17898, 18032, 18128, 18263, 18673, 18829, 19183, 
                            19556, 20783, 20794, 21001, 21767, 22001, 22072, 22161, 22325, 22912, 23040, 
                            23483, 24008, 24427, 24454, 24642, 24673, 24797, 25236, 25286, 25569, 25771, 
                            28586, 28722, 28953, 35114, 36319, 36432, 37669, 39101, 39911, 41106]
        
        hybrid_tfs_siebel = [str(x) for x in hybrid_tfs_siebel]

        return hybrid_tfs_siebel


    # SQL query to pull information needed by DataMAD, also renames to DataMad names.
    def custom_databank_datamad_sql_query(self):
        sql_databank_renamed = "SELECT \
                    fact_application.ApplicationID AS GRANTREFERENCE, \
                    fact_application.FinanceAwardID AS NERC_ID, \
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
                    WHERE fact_application.AdministratingCouncil = 'NERC' AND \
                    CHAR_LENGTH(fact_application.ApplicationID) < 7 AND \
                    (fact_application.ApplicationStatus = 'ACCEPTED' OR \
                    fact_application.ApplicationStatus = 'ACTIVE')\
                    "
        return sql_databank_renamed
    
    def custom_sra_dw_datamad_sql_query(self, grant_references):
        # Turn list of grant references into string (grant1, grant2, ...., grantN)
        gr_str = "('" + "', '".join(grant_references) + "')"

        # Query to retrieve 
        # mv_ssd_organisation.organisation_city AS CITY, \

        
        sql_sra_dw_renamed = "SELECT \
                    mv_application_trans.ApplicationIdentifier AS GRANTREFERENCE, \
                    mv_application_trans.ApplicationTechnicalSummary AS OBJECTIVES, \
                    mv_application_trans.CouncilShortName AS NEW_ADMINISTRATING_COUNCIL, \
                    mv_outcome_facilities.RecordTitle AS FACILITY1, \
                    mv_outcome_facilities.OutcomeSubtype AS FACILITY2, \
                    mv_outcome_facilities.Description AS FACILITY3 \
                    FROM mv_application_trans \
                    LEFT OUTER JOIN  mv_outcome_facilities \
                        ON  mv_application_trans.ApplicationIdentifier = mv_outcome_facilities.ApplicationIdentifier \
                    WHERE mv_application_trans.ApplicationIdentifier in " + gr_str + "AND \
                    CHAR_LENGTH(mv_application_trans.ApplicationIdentifier) < 7 AND \
                    mv_application_trans.CouncilShortName = 'NERC' AND \
                    (mv_application_trans.ApplicationStatus = 'ACCEPTED' \
                    OR  mv_application_trans.ApplicationStatus = 'ACTIVE') \
                    "
        
        # mv_application_trans.ApplicationIdentifier in (22072, 22001) AND \ + 
        
        return sql_sra_dw_renamed
    

    def dictfetchall(self, cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
        ]


    def handle(self, *args, **options):
        if options.get('lookback'):
            sql_command = self.temp() # TODO, amend SQL query to include date range to look for new/ changed grants, not just the date look back, unsure how, need more info from NERC/ UKRI
        else:
            sql_command_databank = self.custom_databank_datamad_sql_query()

        with connections["DataBank"].cursor() as cursor:
            cursor.execute(sql_command_databank)
            row = self.dictfetchall(cursor)

        # Creation of dataframe with data from SQL query
        df_databank = pd.DataFrame(row)

        # Extract unique grant references as a list
        grant_refs = df_databank.GRANTREFERENCE.unique().tolist()

        sql_command_sra_dw = self.custom_sra_dw_datamad_sql_query(grant_references=grant_refs)

        with connections["sra_dw"].cursor() as cursor:
            cursor.execute(sql_command_sra_dw)
            row_sra_dw = self.dictfetchall(cursor)

        # Creation of facility dataframe
        df_sra_dw = pd.DataFrame(row_sra_dw)

        # Merge facility entries
        df_sra_dw["FACILITY"] = df_sra_dw["FACILITY1"].astype(str) + " " + df_sra_dw["FACILITY2"].astype(str) + " " + df_sra_dw["FACILITY3"].astype(str)

        # Replace "None None None" with empty string "" and delete FACILITY1, FACILITY2 and FACILITY3 columns
        df_sra_dw['FACILITY'] = df_sra_dw['FACILITY'].str.replace('None None None','')
        df_sra_dw.drop(columns=['FACILITY1', 'FACILITY2', 'FACILITY3'])

        # Join the two dataframes on grant reference
        df = pd.merge(df_databank, df_sra_dw, on="GRANTREFERENCE")

        df.to_csv("Finding_MACC.csv")

        # Delete any Databank application IDs which are part of the hybrid submitted in TFS paid in Siebel, or they will
        # be double imported.
        hybrid_list = self.hybrid_tfs_siebel_list()
        df = df[~df.GRANTREFERENCE.isin(hybrid_list)]

        # Clean up NERC IDs so they don't have "UKRI" prefix if the string contains NE/
        df['NERC_ID'] = df['NERC_ID'].str.replace('UKRI/NE/', 'NE/')

        # Populate n_cols, columns which have boolean True/False values
        n_cols = ["NCAS", "NCEO", "LEAD_GRANT"]
        df = df.reindex(columns=[*df.columns.tolist(), *n_cols], fill_value=0)

        # Use TEAM_MEMBER_ROLES to populate LEAD_GRANT and potentially PARENT_GRANT
        df.loc[df.TEAM_MEMBER_ROLE == "Principal Investigator", "LEAD_GRANT"] = 1 # Change LEAD_GRANT to Y if TEAM_MEMBER_ROLE is PI
        df = df.sort_values(by=['GRANTREFERENCE'])

        # Delete entirely duplicate rows (caused by database query and not calling back information which would have made rows unique)
        df = df.drop_duplicates()  

        # Delete any duplicate name rows caused by people being listed as more than one member role, prioritise PI for now
        df = df.sort_values(by=['LEAD_GRANT'], ascending=False)
        df = df.drop_duplicates(subset=(['GRANTREFERENCE', 'GRANT_HOLDER']), keep='first')

        # Look for NCAS, NCEO in RESEARCH_ORG and set to "Y" if found in row, stays as "N" if not.
        df.loc[df.RESEARCH_ORG == "National Centre for Atmospheric Science", "NCAS"] = 1
        df.loc[df.RESEARCH_ORG == "National Centre for Earth Observation", "NCEO"] = 1

        # Renumber GRANTREFERENCE for non- LEAD_GRANT so there aren't GRANTREFERENCE DataMad database clashes. Leave the PI grant as the "parent" grant with no suffix
        # Identify PIs (in case of multiple label the first one), if no PI then they are labelled in order of preference:
        # Grant-Manager, CI, Project-Lead, Project-Co-Lead-UK, etc unspecified and unknown last.
        
        tmr_unique = df["TEAM_MEMBER_ROLE"].unique().tolist()
        tmr_known_in_pref_order = ['Principal Investigator', 'Co Investigator', 'Researcher Co Investigator', 'Project lead', 'Project co-lead (UK)', 
                                   'Grant manager', 'Fellow', 'Researcher co-lead','Researcher', 'Specialist', 'Research and innovation associate', 
                                   'Technician', 'Professional enabling staff', 'Unspecified']
        
        special_order = {u: i for i, u in enumerate(reversed(tmr_known_in_pref_order), 1)}
        tmr_unique.sort(key=lambda s: special_order.get(s, 0), reverse=True)

        # Create categorial in order given above
        df["tmr_mapping_cat"] = pd.Categorical(df['TEAM_MEMBER_ROLE'], tmr_unique, )

        # Sort values by GRANTREFERENCE and tmr_mapping with its categorical order given above
        df = df.sort_values(by=['GRANTREFERENCE', 'tmr_mapping_cat'])
        df["PI_FLAG"] = df.groupby(['GRANTREFERENCE']).cumcount() + 1

        # Label non PI grants with tmr_mapping suffix
        df.loc[(df.PI_FLAG != 1) & (df.LEAD_GRANT != 1), 'GRANTREFERENCE'] = df.loc[(df.PI_FLAG != 1) & (df.LEAD_GRANT != 1), 'GRANTREFERENCE'] + "_" + df.loc[(df.PI_FLAG != 1) & (df.LEAD_GRANT != "Y"), 'TEAM_MEMBER_ROLE']

        # Label grants with more than one PI with "PI_additional" suffix
        df.loc[(df.PI_FLAG != 1) & (df.LEAD_GRANT == 1), 'GRANTREFERENCE'] = df.loc[(df.PI_FLAG != 1) & (df.LEAD_GRANT == 1), 'GRANTREFERENCE'] + "_PI-additional"

        # Now set "LEAD_GRANT" "Y" to match PI_FLAG==1, set everything else to N
        df.loc[(df.PI_FLAG == 1), 'LEAD_GRANT'] = 1
        df.loc[(df.PI_FLAG != 1), 'LEAD_GRANT'] = 0
        
        # Create hide record, set all but LEAD_GRANT to hidden "1" status
        df["HIDE_RECORD"] = 1
        df.loc[(df.PI_FLAG == 1), 'HIDE_RECORD'] = 0

        # Need to populate PARENT_GRANT with grant number for LEAD_GRANT, where appropriate
        df["PARENT_GRANT"] = df['GRANTREFERENCE'].str.findall('^.+?(?=_)').str.join(", ")

        df = df.drop(["TEAM_MEMBER_ROLE", "tmr_mapping_cat", "PI_FLAG"], axis=1) # Delete TEAM_MEMBER_ROLE, no longer needed

        # Reorder columns to Siebel order (easier to read for user when debugging, not needed for import via Django)
        col_order = ['GRANTREFERENCE', 'NERC_ID', 'PROJECT_TITLE', 'LEAD_GRANT', 'PARENT_GRANT',
                        'SCHEME', 'CALL', 'GRANT_TYPE',
                        'GRANT_HOLDER', 'EMAIL', 'RESEARCH_ORG',
                        'DEPARTMENT', 'ACTUAL_START_DATE', 'ACTUAL_END_DATE',
                        'NCAS', 'NCEO', 'PROPOSED_ST_DT', 'PROPOSED_END_DT',
                        'GRANT_STATUS', 'ADDRESS1', 'CITY',
                        'POSTCODE', 'AMOUNT',
                        'ROUTING_CLASSIFICATION', 'SCIENCE_AREA',
                        'GEOGRAPHIC_AREA', 'SECONDARY_CLASSIFICATION',
                        'ABSTRACT', 'OBJECTIVES', 'FACILITY', 'HIDE_RECORD']

        df = df[col_order]

        # Ensure types are correct on bool and datetime fields
        df["LEAD_GRANT"] = df["LEAD_GRANT"].astype("bool")
        df["HIDE_RECORD"] = df["HIDE_RECORD"].astype("bool")
        df["NCEO"] = df["NCEO"].astype("bool")
        df["NCAS"] = df["NCAS"].astype("bool")

        # df['PROPOSED_ST_DT'] = pd.to_datetime(df['PROPOSED_ST_DT'])
        # df['PROPOSED_END_DT'] = pd.to_datetime(df['PROPOSED_END_DT'])
        # df['ACTUAL_START_DATE'] = pd.to_datetime(df['ACTUAL_START_DATE'])
        # df['ACTUAL_END_DATE'] = pd.to_datetime(df['ACTUAL_END_DATE'])
 
        # Create mapping to go from renamed DataBank fields to CEDA DataMad database
        mapping = {
                'GRANTREFERENCE': 'grant_ref',
                'NERC_ID': 'nerc_id',
                'PROJECT_TITLE': 'title',
                'SCHEME': 'scheme',
                'CALL': 'call',
                'GRANT_TYPE': 'grant_type',
                'GRANT_HOLDER': 'grant_holder',
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
                'HIDE_RECORD': 'hide_record'
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

                elif source_field in ('PROPOSED_ST_DT', 'PROPOSED_END_DT', 'ACTUAL_START_DATE', 'ACTUAL_END_DATE'):
                    # Ensure the date is converted correctly (although DataBank should always give datetime fields for the above)
                    if not isinstance(value, datetime.date):
                        value = parse(value, default=None).date()

                if source_field not in "HIDE_RECORD":
                    # Add to the data dict
                    data[model_field] = value

            ig = ImportedGrant(**data)

            # Generate list of fields to check. These fields come from grant import
            model_fields = [model_field for source_field, model_field in mapping.items()]
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
            hide_record = row.HIDE_RECORD
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
                grant.hide_record = hide_record
                grant.parent_grant = pg
            else:
                grant.hide_record = hide_record

            grant.save()
