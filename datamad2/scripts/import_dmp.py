# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '17 Mar 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

import django

from datamad2.views.account import user
django.setup()

from django.core.exceptions import ObjectDoesNotExist
from datamad2.models import Grant, JIRATicket, GithubTicket, DataCentre, DataProduct, PreservationPlan
import json
from tqdm import tqdm
from jira import JIRA
from preservation_plans import *

with open('dmp_jira_migration1.json') as reader:
    jira_data = json.load(reader)

with open('dmp_github_migration1.json') as reader:
    github_data = json.load(reader)

jira = JIRA(server='https://jira.ceh.ac.uk', basic_auth=('username', 'password'))
github = "temp_string" # TODO, add Github connection here

CEDA_DATACENTRE = DataCentre.objects.get(name='CEDA')


PRESERVATION_PLAN_MAP = {
    'subset': SUBSET_PLAN,
    'keep indefinately?': KEEP_INDEFINITELY_PLAN,
    'keepasis': KEEP_AS_IS_PLAN,
    'keep indefinately': KEEP_INDEFINITELY_PLAN,
    'keepindefinitely': KEEP_INDEFINITELY_PLAN,
    'dispose5years ': DISPOSE5YEARS_PLAN,
    'archive with cfarr data': {},
    'reference': REFERENCE_PLAN,
    "don't keep": {},
    'tbd': TBD_PLAN,
    'manageinproject': MANAGE_IN_PROJECT_PLAN,
    'keep indefinitely': KEEP_INDEFINITELY_PLAN,
    'intraproject sharing and publication (?)': {},
    "don't keep samples": {},
    'do not keep': {},
    'otherdmp': OTHER_DMP_PLAN,
    'not known': TBD_PLAN
}


################################
# TEMPORARY SUBSET FOR TESTING #
################################

subset = []
preservation_plan_set = set()

for project in jira_data:
    data_products = project.get('datamad', {}).get('data_products')
    if data_products:
        if data_products[0]['grant_ref'] == 'NE/N001508/1':
            subset.append(project)
        for product in data_products:
            preservation_plan = product.get('preservation_plan')
            if preservation_plan:
                preservation_plan_set.add(preservation_plan.lower())

# data = subset

################################
#    END SUBSET FOR TESTING    #
################################
if user.datacentre == "CEDA":
    data = github_data
else:
    data = jira_data

for project in tqdm(data):

    if user.datacentre == "CEDA":
        grant_reference = project['github']['issue']['summary'].split(':')[0] # TODO
        datamad_content = project['datamad']
    else:
        grant_reference = project['jira']['issue']['summary'].split(':')[0]
        datamad_content = project['datamad']

    data_products = datamad_content.get('data_products')
    dmp_agreed_date = datamad_content.get('dmp_agreed_date')
    date_contacted_pi = datamad_content.get('date_contacted_pi')

    # Check for grants in DataMAD which match dmp
    grants = Grant.objects.filter(grant_ref=grant_reference)

    # They all == 1 but just to be explicit
    if grants.count() == 1:
        grant = grants[0]

        # Update grant information
        if dmp_agreed_date:
            grant.dmp_agreed = True
            grant.save()

            grant.dmp_agreed_date = dmp_agreed_date

        if date_contacted_pi:
            grant.date_contacted_pi = date_contacted_pi

        grant.save()

        # Create data products
        if data_products:
            for dp in data_products:

                # check if it already exists
                try:
                    datamad_dp = DataProduct.objects.get(grant=grant, data_product_type='digital', contact=dp.get('contact'), name=dp.get('name'))
                except ObjectDoesNotExist:
                    preservation_plan = dp.pop('preservation_plan')
                    dp.pop('grant_ref')

                    # Retrieve or create the preservation plan
                    if preservation_plan:
                        preservation_plan = PRESERVATION_PLAN_MAP.get(preservation_plan.lower())
                        if preservation_plan:
                            preservation_plan, created = PreservationPlan.objects.get_or_create(datacentre=CEDA_DATACENTRE, **preservation_plan)
                    else:
                        preservation_plan = None

                    dp['preservation_plan'] =  preservation_plan
                    datamad_dp = DataProduct(grant=grant, **dp)
                    datamad_dp.save()



        # Add JIRA or Github permalink
        if grant.datacentre == "CEDA":
            # TODO, need to discuss with Wendy and Lucy,
            # THE CODE BELOW (within the if statement, not the else) IS TEMPORARY 
            # AND NEEDS TO BE REPLACED WITH A PROPER SOLUTION
            issues = github.search_issues(f'summary~"{grant.grant_ref}" AND issuetype=10602', fields=['status'])

            if issues:
                issue = issues[0]
                permalink = issue.permalink()

                github_links = GithubTicket.objects.filter(grant=grant, datacentre=CEDA_DATACENTRE)
                if not github_links:
                    github_link = GithubTicket(grant=grant, datacentre=CEDA_DATACENTRE, url=permalink)
                    github_link.save()
        else:
            issues = jira.search_issues(f'summary~"{grant.grant_ref}" AND issuetype=10602', fields=['status'])

            if issues:
                issue = issues[0]
                permalink = issue.permalink()

                jira_links = JIRATicket.objects.filter(grant=grant, datacentre=CEDA_DATACENTRE)
                if not jira_links:
                    jira_link = JIRATicket(grant=grant, datacentre=CEDA_DATACENTRE, url=permalink)
                    jira_link.save()