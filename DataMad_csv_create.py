import pandas as pd
import sqlalchemy as sa
import numpy as np

# TODO, try and get both parent and child grants in the SQL query, 
#   for now only parent grants are present (i.e. lead PI grants)

# Load connection string for SQLAlchemy
conn_str = []

with open('./local_temp/sql_alchemy_mysql_conn_string.txt', 'r') as fn:
    for line in fn:
        conn_str.append(str(line))

# Setup SQLAlchemy to use mysqlclient as MySQL driver
# (need to use SQLAlchemy as pandas now only accepts SQLAlchemey engine + SQL query input, not pyodbc or similar)

engine = sa.create_engine(conn_str[0]) # mysqlclient connection for Docker

# engine = sa.create_engine('mysql+pyodbc://DataBank?charset=utf8mb4') # pyodbc connection (used for Windows testing)
saconn = engine.connect()

# SQL query to pull information needed by DataMAD, also renames to DataMad names.
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

# TODO May potentially need to add this back in (trying to join on fact_application_team.LeadApplicantPersonSKey instead)
"""
               LEFT OUTER JOIN dim_person \
                    ON fact_application.ApplicantPersonSKey = dim_person.PersonSKey \
"""


# Query data from Databank
data_renamed = pd.read_sql(sql_datamad_renamed, engine)

# Add in blank columns to cover fields missing in Databank that were in Siebel
# TODO, should delete some of these once app_datamad is updated to remove these fields from the models
#   Definitely don't need WORK_NUMBER, NCAS, NCEO, ADDRESS2, OVERALL_SCORE, PROPOSED_ST_DT_ORG or PROPOSED_END_DT_ORG
#   Try to find (or extract from another field): FACILITY, LEAD_GRANT, PARENT_GRANT and OBJECTIVES

no_longer_needed_cols = ['WORK_NUMBER', 'NCAS', 'NCEO', 'ADDRESS2', 'OVERALL_SCORE', 
                            'PROPOSED_ST_DT_ORG', 'PROPOSED_END_DT_ORG']
data_renamed = data_renamed.reindex(columns=[*data_renamed.columns.tolist(), *no_longer_needed_cols], fill_value=np.nan)

needed_cols = ['FACILITY', 'LEAD_GRANT', 'PARENT_GRANT', 'OBJECTIVES']
data_renamed = data_renamed.reindex(columns=[*data_renamed.columns.tolist(), *needed_cols], fill_value=np.nan)

# Reorder columns to Siebel order (easier to read for user, not needed for import via Django)
col_order = ['GRANTREFERENCE', 'PROJECT_TITLE', 'SCHEME', 'CALL', 'GRANT_TYPE',
                'GRANT_HOLDER', 'WORK_NUMBER', 'EMAIL', 'RESEARCH_ORG',
                'DEPARTMENT', 'ACTUAL_START_DATE', 'ACTUAL_END_DATE',
                'NCAS', 'NCEO', 'PROPOSED_ST_DT', 'PROPOSED_END_DT',
                'GRANT_STATUS', 'ADDRESS1', 'ADDRESS2', 'CITY',
                'POSTCODE', 'LEAD_GRANT', 'PARENT_GRANT', 'AMOUNT',
                'ROUTING_CLASSIFICATION', 'SCIENCE_AREA',
                'GEOGRAPHIC_AREA', 'SECONDARY_CLASSIFICATION',
                'ABSTRACT', 'OBJECTIVES', 'FACILITY', 'OVERALL_SCORE',
                'PROPOSED_ST_DT_ORG', 'PROPOSED_END_DT_ORG']

data_renamed = data_renamed[col_order]

# Save .csv file
data_renamed.to_csv("./import_csvs/datamad_databank_debug.csv")

pause = 1
