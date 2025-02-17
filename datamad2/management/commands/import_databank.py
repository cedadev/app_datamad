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

import yaml
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
        sql_databank = "SELECT \
                    fact_application.ApplicationID AS GRANTREFERENCE, \
                    fact_application.ApplicationID AS UKRI_ID, \
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
                            ON fact_application_team.TeamMemberPersonSKey = dim_person.PersonSKey \
                    LEFT OUTER JOIN dim_department \
                            ON fact_application.OrganisationDepartmentSKey = dim_department.OrganisationDepartmentSKey \
                    LEFT OUTER JOIN dim_application_date  \
                            ON fact_application.ApplicationSKey = dim_application_date.ApplicationSKey \
                    LEFT OUTER JOIN  dim_organisation\
                            ON fact_application_team.TeamMemberOrganisationSKey = dim_organisation.OrganisationSKey \
                    LEFT OUTER JOIN  dim_application_ext\
                            ON fact_application.ApplicationSKey = dim_application_ext.ApplicationSKey \
                    LEFT OUTER JOIN dim_classification_area \
                            ON fact_application.PrimaryClassificationAreaSKey = dim_classification_area.ClassificationAreaSKey \
                    WHERE fact_application.AdministratingCouncil = 'NERC' AND \
                    CHAR_LENGTH(fact_application.ApplicationID) < 7 AND \
                    (fact_application.ApplicationStatus = 'ACCEPTED' OR \
                    fact_application.ApplicationStatus = 'ACTIVE' OR \
                    fact_application.ApplicationStatus = 'CLOSED')\
                    "
        return sql_databank
    
    def custom_sra_dw_datamad_sql_query(self, grant_references):
        # Turn list of grant references into string (grant1, grant2, ...., grantN)
        gr_str = "('" + "', '".join(grant_references) + "')"

        # Query to retrieve facility        
        sql_sra_dw = "SELECT \
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
                    OR  mv_application_trans.ApplicationStatus = 'ACTIVE' \
                    OR mv_application_trans.ApplicationStatus = 'CLOSED') \
                    "
         
        return sql_sra_dw
    
    def dictfetchall(self, cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
        ]
    
    @staticmethod
    def merge_facility(df_sra_dw):
        df_sra_dw["FACILITY"] = df_sra_dw["FACILITY1"].astype(str) + " " + df_sra_dw["FACILITY2"].astype(str) + " " + df_sra_dw["FACILITY3"].astype(str)

        # Replace "None None None" with empty string "" and delete FACILITY1, FACILITY2 and FACILITY3 AND NEW_ADMINISTRATING_COUNCIL columns
        df_sra_dw['FACILITY'] = df_sra_dw['FACILITY'].str.replace('None None None','')
        df_sra_dw = df_sra_dw.drop(columns=['FACILITY1', 'FACILITY2', 'FACILITY3', 'NEW_ADMINISTRATING_COUNCIL'])

        return df_sra_dw
    
    def define_lead_grant_priority(self, df):
        grant_pref_order= ['Principal Investigator', 'Project lead', 'Grant manager', 'Project co-lead (UK)',
                                   'Co Investigator', 'Researcher Co Investigator',
                                   'Fellow', 'Researcher co-lead','Researcher', 'Specialist',
                                   'Research and innovation associate', 
                                   'Technician', 'Professional enabling staff', 'Unspecified']
        
        tmr_unique = df["TEAM_MEMBER_ROLE"].unique().tolist()

        # Ensure any grants not in grant preference order list are counted, at the end        
        special_order = {u: i for i, u in enumerate(reversed(grant_pref_order), 1)}
        tmr_unique.sort(key=lambda s: special_order.get(s, 0), reverse=True)

        grant_pref_order_final = tmr_unique

        self.grant_pref_order = grant_pref_order_final

    def populate_ncas_nceo_leadgrant_sort_column(self, n_cols, df):
        df = df.reindex(columns=[*df.columns.tolist(), *n_cols], fill_value=0)

        sort_dict = {str(key): idx for idx, key in enumerate(self.grant_pref_order)}

        # Use TEAM_MEMBER_ROLES to populate LEAD_GRANT in order of grant_pref_order (PI first, then others)
        df['sort_column'] = df.TEAM_MEMBER_ROLE.map(sort_dict)
        df = df.sort_values(by=['GRANTREFERENCE', 'sort_column'])

        df["cumu_count"] = df.groupby(['GRANTREFERENCE']).cumcount()        
        df.loc[(df["cumu_count"] == 0), "LEAD_GRANT"] = 1

        # Look for NCAS, NCEO in RESEARCH_ORG and set to "Y" if found in row, stays as "N" if not.
        df.loc[df.RESEARCH_ORG == "National Centre for Atmospheric Science", "NCAS"] = 1
        df.loc[df.RESEARCH_ORG == "National Centre for Earth Observation", "NCEO"] = 1

        return df
    
    @staticmethod
    def rename_grant_ref(df):
        # Sort values by GRANTREFERENCE and tmr_mapping with its categorical order given above
        df = df.sort_values(by=['GRANTREFERENCE', 'sort_column'])
        df["ROLE_FLAG"] = df.groupby(['GRANTREFERENCE', "sort_column"]).cumcount() + 1
        df["ROLE_FLAG"] = df["ROLE_FLAG"].astype(str)

        # Label non lead grant holders with ROLE_FLAG suffix
        df.loc[(df.LEAD_GRANT != 1), 'GRANTREFERENCE'] = df.loc[(df.LEAD_GRANT != 1), 'GRANTREFERENCE'] + \
                                                                             "_" + df.loc[(df.LEAD_GRANT != 1), 'TEAM_MEMBER_ROLE'] + \
                                                                             "_" + df.loc[(df.LEAD_GRANT != 1), 'ROLE_FLAG']

        df = df.sort_values(by=['GRANTREFERENCE'])
    
        return df
    
    @staticmethod
    def hybrid_parent_child(df):
        with open('TFS_Siebel_hybrid_parent_child.yaml', 'r') as file:
            hybrid_parent_child = yaml.safe_load(file)
    
        hybrid_parent_child_df =   pd.DataFrame(hybrid_parent_child).transpose()
        hybrid_parent_child_df = hybrid_parent_child_df.rename(columns={"parent": "PARENT_GRANT"})
        
        # Extract children then merge on child_1 and child_2 to fill in PARENT_GRANT
        children = pd.concat([hybrid_parent_child_df.child_1, hybrid_parent_child_df.child_2])
        children_df = pd.DataFrame(children, columns=["GRANTREFERENCE"])
        children_df = children_df.dropna()  # Remove "Missing" grants

        children_df = children_df.join(hybrid_parent_child_df, lsuffix='_new', rsuffix='_orig')

        # Merge into main dataframe to get parent grants already in datamad
        df = df.merge(children_df[['GRANTREFERENCE', 'PARENT_GRANT']], how='left', on='GRANTREFERENCE')
        
        df = df.sort_values(by="PARENT_GRANT")

        return df
    

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
        df_sra_dw = self.merge_facility(df_sra_dw)

        # Join the two dataframes on grant reference
        df = pd.merge(df_databank, df_sra_dw, on="GRANTREFERENCE")

        # Define lead grant preference order (PI first)
        self.define_lead_grant_priority(df)

        # Populate n_cols (currently NCAS, NCEO and LEAD_GRANT), columns which have boolean True/False values
        n_cols = ["NCAS", "NCEO", "LEAD_GRANT"]
        df = self.populate_ncas_nceo_leadgrant_sort_column(n_cols, df)

        # Clean up NERC IDs so they don't have "UKRI" prefix if the string contains NE/
        df['NERC_ID'] = df['NERC_ID'].str.replace('UKRI/NE/', 'NE/')

        # Rename any Databank application IDs to their NERC_IDs if they are part of the 
        # hybrid grants which were submitted in TFS and paid in Siebel.
        # Otherwise they will be double imported under the new UKRI grant ID and the old NERC ID.
        hybrid_list = self.hybrid_tfs_siebel_list()
        df.loc[df.GRANTREFERENCE.isin(hybrid_list), "GRANTREFERENCE"] = df[df.GRANTREFERENCE.isin(hybrid_list)]["NERC_ID"]

        # Delete any duplicate name rows caused by people being listed as more than one member role, prioritise keeping PI
        df = df.sort_values(by=['LEAD_GRANT'], ascending=False)
        df = df.drop_duplicates(subset=(['GRANTREFERENCE', 'GRANT_HOLDER', 'TEAM_MEMBER_ROLE', 'EMAIL']), keep='first')

        # Rename GRANTREFERENCE for non- LEAD_GRANT so there aren't GRANTREFERENCE DataMad database clashes. Leave the PI grant as the "parent" grant with no suffix
        # Identify PIs (in case of multiple label the first one), if no PI then they are labelled in order of preference:
        # Grant-Manager, CI, Project-Lead, Project-Co-Lead-UK, etc unspecified and unknown last.
        df = self.rename_grant_ref(df)
        
        # Create hide record, set all but LEAD_GRANT to hidden "1" status
        df["HIDE_RECORD"] = 1
        df.loc[(df.LEAD_GRANT == 1), 'HIDE_RECORD'] = 0

        # Ensure existing Datamad parent/ child relationships are maintained and 
        # write child/ parent relationship for pre-existing Datamad grants
        df = self.hybrid_parent_child(df)

        # Now populate the rest of the parent/ child relationships
        # Need to populate PARENT_GRANT with grant number for LEAD_GRANT, where appropriate
        df["PARENT_GRANT"] = df['GRANTREFERENCE'].str.findall('^.+?(?=_)').str.join(", ")

        # Ensure types are correct on bool and datetime fields
        df["LEAD_GRANT"] = df["LEAD_GRANT"].astype("bool")
        df["HIDE_RECORD"] = df["HIDE_RECORD"].astype("bool")
        df["NCEO"] = df["NCEO"].astype("bool")
        df["NCAS"] = df["NCAS"].astype("bool")

        # Delete columns which aren't imported into DataMad
        df = df.drop(["TEAM_MEMBER_ROLE","NEW_ADMINISTRATING_COUNCIL",
                      "sort_column", "cumu_count","ROLE_FLAG"], axis=1) 
 
        # Create mapping to go from renamed DataBank fields to CEDA DataMad database
        mapping = {
                'GRANTREFERENCE': 'grant_ref',
                'UKRI_ID': 'ukri_id',
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
