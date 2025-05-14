from jira import JIRA
from django.conf import settings
from django.urls import reverse
import datetime
import logging

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


def get_jira_client(request):
    """
    Returns a provisioned JIRA client
    """
    oauth_dict = {
        'access_token': request.session.get('jira_access_token'),
        'access_token_secret': request.session.get('jira_access_token_secret'),
        'consumer_key': settings.JIRA_CONSUMER_KEY,
        'key_cert': settings.JIRA_PRIVATE_RSA_KEY
    }

    return JIRA(settings.JIRA_SERVER, oauth=oauth_dict)


def map_datamad_to_jira(request, imported_grant):
    """
    Map datamad fields to JIRA issue fields

    :param request: WSGI request
    :param imported_grant: Imported grant object for use with the evaluation function
    :return: issue_dict for merging
    """

    issue_dict = {}

    for field, value in request.user.data_centre.jiraissuetype.jira_issue_fields.items():
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


def make_issue(request, imported_grant):
    """
    Convert a grant into a JIRA ticket
    :param request: Django request object
    :param imported_grant:
    :return: JIRA issue. Either a newly created one or the first result from the search
    """
    jira = get_jira_client(request)

    if (imported_grant.nerc_id is "") & (imported_grant.ukri_id is ""):
        issue_dict = {
            'project': str(request.user.data_centre.jira_project),
            'summary': f'{imported_grant.grant_ref}:{imported_grant.title}',
            'description': imported_grant.abstract,
            'issuetype': {'id': str(request.user.data_centre.jiraissuetype.issuetype)},
        }

        nerc_id = imported_grant.grant_ref.replace('/', '\\u002f')
    else:
        issue_dict = {
            'project': str(request.user.data_centre.jira_project),
            'summary': f'{imported_grant.nerc_id}:{imported_grant.title}',
            'description': imported_grant.abstract,
            'issuetype': {'id': str(request.user.data_centre.jiraissuetype.issuetype)},
        }

        nerc_id = imported_grant.nerc_id.replace('/', '\\u002f')

    issue_dict.update(map_datamad_to_jira(request, imported_grant))

    # Check if issue already exists
    # Check the issuetype and limit the fields returned to save time and data transfer
    results = jira.search_issues(
        f'summary~{nerc_id} AND issuetype={request.user.data_centre.jiraissuetype.issuetype}',
        fields=[
            'issuetype',
            'summary'
        ]
    )
    reporter = request.user.data_centre.jiraissuetype.reporter

    # Create a new one if none found or return first hit (there should only be one)
    if not results:
        new_issue = jira.create_issue(fields=issue_dict)

        if reporter:
            new_issue.update(reporter={'name': str(reporter)})

        # Generate back-reference to datamad
        datamad_permalink = request.build_absolute_uri(reverse('grant_detail', kwargs={'pk': imported_grant.grant.pk}))

        # Add backreference to datamad
        jira.add_simple_link(new_issue, {
            'url': datamad_permalink,
            'title': f'View grant ref: {imported_grant.grant_ref}, NERC ID: {imported_grant.nerc_id} in Datamad'
        })

        # create subtasks
        subtasks = request.user.data_centre.subtask_set.all()
        for task in subtasks:
            create_subtask(task, request, new_issue, imported_grant, reporter)

    else:
        new_issue = results[0]

    return new_issue


def create_subtask(subtask, request, new_issue, imported_grant, reporter):
    jira = get_jira_client(request)

    if subtask.ref_time == 'end_date':
        ref_time = imported_grant.actual_end_date
    else:
        ref_time = imported_grant.actual_start_date

    if (imported_grant.nerc_id is "") & (imported_grant.ukri_id is ""):
        subtask_dict = {'project': str(request.user.data_centre.jira_project),
                'summary': f"{imported_grant.grant_ref}:{subtask.name}",
                'description': '',
                'issuetype': {'name': 'Sub-Task'},
                'parent': {'key': new_issue.key},
                'customfield_11660': str(imported_grant.actual_start_date),  # grant start date
                'duedate': str(ref_time + datetime.timedelta(weeks=subtask.schedule_time))}
    else:
        subtask_dict = {'project': str(request.user.data_centre.jira_project),
                        'summary': f"{imported_grant.nerc_id}:{subtask.name}",
                        'description': '',
                        'issuetype': {'name': 'Sub-Task'},
                        'parent': {'key': new_issue.key},
                        'customfield_11660': str(imported_grant.actual_start_date),  # grant start date
                        'duedate': str(ref_time + datetime.timedelta(weeks=subtask.schedule_time))}

    subtask = jira.create_issue(fields=subtask_dict)

    if reporter:
        subtask.update(reporter={'name': str(reporter)})
