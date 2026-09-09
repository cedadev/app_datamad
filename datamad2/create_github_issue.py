from django.conf import settings
from django.urls import reverse
import datetime
import logging
import urllib
import httpx
import githubetl

# TODO, make this work with GitHub projects instead of JIRA.
# This is a copy of create_jira_issue.py with the necessary changes
# to make it work with GitHub projects.

logger = logging.getLogger(__name__)

FIELD_MAPPING = {
    'start_date_field': 'str(imported_grant.actual_start_date)',
    'end_date_field': 'str(imported_grant.actual_end_date)',
    'proposed_start_date': 'str(imported_grant.proposed_start_date)',
    'proposed_end_date': 'str(imported_grant.proposed_end_date)',
    'grant_ref_field': 'imported_grant.grant_ref',
    'nerc_id_field': 'imported_grant.nerc_id',
    'pi_field': 'imported_grant.grant_holder',
    'research_org_field': 'imported_grant.research_org',
    'primary_datacentre_field': 'request.user.data_centre.name',
    'amount_awarded_field': 'str(imported_grant.amount_awarded)',
    'grant_type_field': 'imported_grant.grant_type',
    'lead_grant_field': 'str(imported_grant.lead_grant)',
    'parent_grant_field': 'imported_grant.parent_grant.grant_ref',
    'child_grants_field': '", ".join([child.grant_ref for child in imported_grant.grant.child_grant.get_queryset()])',
    'email_field': 'imported_grant.email',
    'work_number_field': 'imported_grant.work_number',
    'alt_data_contact_field': 'imported_grant.grant.alt_data_contact',
    'alt_data_contact_email_field': 'imported_grant.grant.alt_data_contact_email',
    'other_datacentre_field': 'imported_grant.grant.other_data_centre.name',
    'call_datacentre_field': 'imported_grant.scheme',
    'scheme_datacentre_field': 'imported_grant.call'

}


def get_github_client():
    """
    Returns a provisioned GitHub client # TODO
    """

    project = getattr(settings, "GITHUB_PROJECT_NAME", "")
    token = getattr(settings, "GITHUB_ISSUE_TOKEN")

    p_project = urllib.parse.urlparse(project)
    server = f"{p_project.scheme}://{p_project.hostname}"
    project = p_project.path[1:]
    if server == "https://github.com":
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
        }
        endpoint = f"https://api.github.com/repos/{project}/issues"
    else:
        headers = {"PRIVATE-TOKEN": token}
        endpoint = f"{server}/api/v4/projects/{p_project.path}/issues"

    return headers, endpoint

@property
def github_prop(self):
    return self.endpoint.startswith("https://api.github.com")


def map_datamad_to_github(request, imported_grant):
    """
    Map datamad fields to GitHub issue fields

    :param request: WSGI request
    :param imported_grant: Imported grant object for use with the evaluation function
    :return: issue_dict for merging
    """

    issue_dict = {}

    for field, value in request.user.data_centre.githubissuetype.github_issue_fields.items(): # TODO
        mapped_datamad_field = FIELD_MAPPING.get(field)
        if mapped_datamad_field:
            if field == 'primary_datacentre_field':
                issue_dict[value] = {'value': eval(mapped_datamad_field)}
            else:

                # Catch situations where the evaluation string has a none somewhere on it's nested path
                try:
                    issue_dict[value] = eval(mapped_datamad_field)
                except AttributeError as e:
                    logger.debug(f'Could not evaluate {mapped_datamad_field}: {e}')

    return issue_dict


def search_github_issues(nerc_id, issuetype, request):
    """
    Search for existing GitHub issues based on nerc_id and issuetype

    :param nerc_id: NERC ID of the grant
    :param issuetype: GitHub issue type
    :param request: WSGI request
    :return: List of matching GitHub issues
    """
    headers, endpoint = get_github_client()
    search_query = f'summary~{nerc_id} AND issuetype={issuetype}'
    search_url = f"{endpoint}?q={urllib.parse.quote(search_query)}"

    response = httpx.get(search_url, headers=headers)
    response.raise_for_status()

    return response.json().get('items', [])

def github_create_issue(fields, title, body, labels):
    """
    Create a new GitHub issue with the provided fields

    :param fields: Dictionary of fields for the new issue
    :param title: Title of the new issue
    :param body: Body of the new issue
    :param labels: List of labels for the new issue
    :return: Created GitHub issue
    """
    headers, endpoint = get_github_client()
    response = httpx.post(endpoint, json=fields, headers=headers)
    response.raise_for_status()

    labels = [str(label) for label in labels]
    data = {"title": title, "description": body, "labels": labels}
    if github_prop:
        data = {"title": title, "body": body, "labels": labels}
    r = httpx.post(endpoint, json=data, headers=headers)
    r.raise_for_status()

    return response.json()

def github_add_simple_link(issue, link):
    """
    Add a simple link to a GitHub issue

    :param issue: GitHub issue object
    :param link: Dictionary containing the link details
    :return: Updated GitHub issue
    """
    headers, endpoint = get_github_client()
    response = httpx.post(f"{endpoint}/{issue['id']}/links", json=link, headers=headers)
    response.raise_for_status()

    return response.json()

def make_github_issue(request, imported_grant) -> bool:

    headers, endpoint = get_github_client()

    if (imported_grant.nerc_id == "") & (imported_grant.ukri_id == ""):
        issue_dict = {
            'project': str(request.user.data_centre.github_project),
            'summary': f'{imported_grant.grant_ref}:{imported_grant.title}',
            'description': imported_grant.abstract,
            'issuetype': {'id': str(request.user.data_centre.githubissuetype.issuetype)},
        }

        nerc_id = imported_grant.grant_ref.replace('/', '\\u002f')
    else:
        issue_dict = {
            'project': str(request.user.data_centre.github_project),
            'summary': f'{imported_grant.nerc_id}:{imported_grant.title}',
            'description': imported_grant.abstract,
            'issuetype': {'id': str(request.user.data_centre.githubissuetype.issuetype)},
        }

        nerc_id = imported_grant.nerc_id.replace('/', '\\u002f')

    issue_dict.update(map_datamad_to_github (request, imported_grant))

    # Check if issue already exists
    # Check the issuetype and limit the fields returned to save time and data transfer
    results = search_github_issues(nerc_id, request.user.data_centre.githubissuetype.issuetype, request)

    reporter = request.user.data_centre.githubissuetype.reporter

    # Create a new one if none found or return first hit (there should only be one)
    if not results:
        new_issue = github_create_issue(fields=issue_dict)

        if reporter:
            new_issue.update(reporter={'name': str(reporter)})

        # Generate back-reference to datamad
        datamad_permalink = request.build_absolute_uri(reverse('grant_detail', kwargs={'pk': imported_grant.grant.pk}))

        # Add backreference to datamad
        github_add_simple_link(new_issue, {
            'url': datamad_permalink,
            'title': f'View grant ref: {imported_grant.grant_ref}, NERC ID: {imported_grant.nerc_id} in Datamad'
        })
    else:
        new_issue = results[0]

    return new_issue
