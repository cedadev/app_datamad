from django.conf import settings
from django.urls import reverse
import logging
from dateutil.relativedelta import relativedelta
from datamad2.githubetl import jira_to_github

# get_repository_id, create_issue, update_custom_field, get_type_ids, update_issue_type, add_issue_to_project, get_user_ids, get_project_id, get_field_ids, calculate_dmp_due_date

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


def get_github_client(request):
    """
    Returns arguments required for a provisioned GitHub client
    """
    gh_token = getattr(settings, "GITHUB_ISSUE_TOKEN")
    owner = getattr(settings, "GITHUB_OWNER")
    repo = getattr(settings, "GITHUB_REPO")
    project_name = getattr(settings, "GITHUB_PROJECT_NAME")
    github_user = request.user.github_username

    gh_args_dict = {"gh_token": gh_token, "owner": owner, "repo": repo, 
                    "project_name": project_name, "github_user": github_user}

    headers = {"Authorization": f"Bearer {gh_token}", "Content-Type": "application/json"}

    return gh_args_dict, headers


@property
def github_prop(self):
    return self.endpoint.startswith("https://api.github.com")


def create_links(request, imported_grant):
    # Create placeholder links and complete DataMad link.
    external_links = ""
    issue_data_links = ["Help Scout", "Datamad", "DSW"]

    for link in issue_data_links:
        if "Help Scout" in link:
            link_title = "Help Scout"
            external_links += f"- [{link_title}]({""})\n"
        elif "Datamad" in link:
            link_title = "DataMad"
            link_url = request.build_absolute_uri(reverse('grant_detail', kwargs={'pk': imported_grant.grant.pk}))
            external_links += f"- [{link_title}]({link_url})\n"
        elif "DSW" in link:
            link_title = "DSW"
            external_links += f"- [{link_title}]({""})"

    return external_links

def create_issue_body(request, imported_grant):
    """
    Create markdown body for GitHub issue based on imported grant data.

    :param request: WSGI request
    :param imported_grant: Imported grant object for use with the evaluation function
    :return: body for GitHub issue
    """

    # Build external links
    external_links = create_links(request, imported_grant)

    #Extract abstract, or provide a default message if not available
    abstract = imported_grant.abstract if imported_grant.abstract else "No abstract provided."

    # Build issue body
    body = f"""# Links
    {external_links}
    - [Dataset record]()
    - [Project record]()
    - [Instrument/Computation/Platform record]()
    - [Collection record]()

    # Tasks
    ## DMP in progress
    ### DMP setup
    - [ ] Claim grant & create issue (DataMad)
    - [ ] If clearly no archival data: 
      - [ ] Update *Will grant produce data* field (DataMad)
      - [ ] Update *Will grant produce data* field, change status to *No archival data* & close issue (GitHub)
    - [ ] [Set up DMP](https://nerceds.fair-wizard.com/wizard/projects) (DSW)
    - [ ] [Create new Help Scout conversation & send DMP link](https://secure.helpscout.net/inboxes/7b0c55db545d4969/conversation/new/) (saved reply 01.01) (Help Scout)
    - [ ] Link conversation to GitHub issue (Help Scout)
    - [ ] Update *Date contacted PI* field (DataMad & GitHub)
    - [ ] Update *Help Scout* and *DSW* links (GitHub)
    - [ ] ⏰ Add comment to set first chase reminder (GitHub): /remind me to send the first DMP chase if no response in 6 weeks

    ### DMP comms
    - [ ] 👋 If no response in 6 weeks, send first chase (saved reply 01.02) (Help Scout)
    - [ ] ⏰ Add comment to set second chase reminder (GitHub): /remind me to send the second DMP chase if no response in 4 weeks
    - [ ] 👋 If no response in 4 weeks, send second chase (saved reply 01.03) (Help Scout) 
    - [ ] ⏰ Add comment to set escalate to NERC reminder (GitHub): /remind me to escalate this to the NERC grants team if no response in 2 weeks
    - [ ] Currently supporting PI to complete DMP
    - [ ] 👋 If no response in 2 weeks, change status to *Escalate to NERC* (GitHub)

    ### DMP completion
    - [ ] Send DMP agreed email (saved reply 02.01) (Help Scout)
    - [ ] Upload DMP (DataMad)
    - [ ] Update *Will grant produce data* & *DMP agreed* fields (DataMad & GitHub)
    - [ ] Change status to *Pre-delivery comms* (GitHub)

    ## Pre-delivery comms
    - [ ] 👋 Send annual check-in 1 (saved reply 03.01) (Help Scout)
    - [ ] 👋 Send annual check-in 2 (saved reply 03.01) (Help Scout)
    - [ ] 👋 Send annual check-in 3 (saved reply 03.01) (Help Scout)
    - [ ] 👋 Send 6-month check-in (saved reply 03.02) (Help Scout)
    - [ ] 👋 Send project due check-in (saved reply 03.03) (Help Scout)
    - [ ] Change status to *Data due* (GitHub)

    ## Data due
    - [ ] Update *Data delivery expected* field (GitHub)
    - [ ] Create sub-issue for each dataset (GitHub)
    - [ ] ⏰ Set any reminders as needed (GitHub)
    - [ ] When data start to arrive, change status to *Archiving in progress* (GitHub)

    ## Archiving in progress
    - [ ] Data starting to arrive & MOLES records in progress
    - [ ] Complete all tasks in dataset sub-issue(s) (GitHub)
    - [ ] Confirm with PI that all data have been sent (Help Scout)
    - [ ] Update *Datasets delivered* (DataMad)
    - [ ] Flag delivery as ingested (Arrivals)
    - [ ] Delete data using arrivals_deleter (Arrivals)
    - [ ] Send completion confirmation (saved reply 05.01) (Help Scout)
    - [ ] Change status to *Archiving completed* (GitHub)

    ## No archival data
    - [ ] Upload DMP confirming no data (DataMad)
    - [ ] Send completion confirmation (saved reply 02.02) (Help Scout)

    ## Escalate to NERC
    - [ ] Report grant to NERC grants team (saved reply 01.04) (Help Scout)
    - [ ] PI responsive after escalation
    - [ ] PI unresponsive, being handled by NERC

    ## Archiving completed
    🎉 All tasks completed!

    ---
    <details>
    <summary>Project abstract</summary>
    {abstract}
    </details>
    """
    # Remove chunks of four whitespaces from body
    body = body.replace("    ", "")

    return body


def assign_mappings():
    """
    Assigns the field mappings for the GitHub issue creation.
    """
    field_name_map = {
        "type": "Project",
        "status": "Status",
        "actual_start_date": "Actual start date",
        "dmp_due": "DMP due",
        "data_centre": "Data centre",
        "actual_end_date": "Actual end date",
        "nerc_id": "NERC ID",
        "ukri_id": "UKRI ID",
        "pi_name": "PI name",
        "pi_email": "PI email",
        "labels": "Labels",
        "funder": "Funder"
    }
    internal_keys = [
        "status",
        "actual_start_date",
        "dmp_due",
        "data_centre",
        "actual_end_date",
        "nerc_id",
        "ukri_id",
        "pi_name",
        "pi_email",
        "funder"
    ]
    return field_name_map, internal_keys


def make_github_issue(request, imported_grant) -> bool:
    """
    Convert a grant into a GitHub issue
    """

    github_args, headers= get_github_client(request)
    body = create_issue_body(request, imported_grant)

    repository_id = jira_to_github.get_repository_id(github_args["owner"], github_args["repo"], headers)

    if (imported_grant.nerc_id == "") & (imported_grant.ukri_id == ""):
        nerc_id = imported_grant.grant_ref
        ukri_id = imported_grant.grant_ref
    else:
        nerc_id = imported_grant.nerc_id
        ukri_id = imported_grant.ukri_id

    # Create issue
    status_mapped = "Unknown" # So that Github issue gets initially set with "No status"

    data_centre = request.user.data_centre.name
    ukri_id = imported_grant.ukri_id
    title = f"{nerc_id}:{imported_grant.title}"
    pi_name = imported_grant.grant_holder
    pi_email = imported_grant.email
    actual_start_date = imported_grant.actual_start_date
    actual_end_date = imported_grant.actual_end_date
    dmp_due = actual_start_date + relativedelta(months=+6)
    mapped_usernames = [request.user.github_username]  # TODO, map to GitHub usernames

    assignee_ids = jira_to_github.get_user_ids(github_args["owner"], github_args["repo"], mapped_usernames, headers)
    gh_issue = jira_to_github.create_issue(repository_id, title, body, headers, assignee_ids, None)

    # Attempt to set the repository-level issue type to 'Project'
    try:
        type_ids = jira_to_github.get_type_ids(github_args["owner"], github_args["repo"], ["Project"], headers)
        if type_ids:
            type_id = type_ids[0]
            try:
                jira_to_github.update_issue_type(gh_issue["id"], type_id, headers)
            except Exception as e:
                print(f"Warning: failed to set issue type for {gh_issue['url']}: {e}")
        else:
            print("Warning: repository has no matching issue type 'Project'.")
    except Exception as e:
        print(f"Warning: could not fetch issue type ids: {e}")

    
    # Map the fields from the imported grant to the GitHub issue, TODO this probably needs work.
    # project_id = get_project_id(github_args, headers)
    project_id = jira_to_github.get_project_id(github_args["owner"], github_args["repo"], github_args["project_name"], headers)
    field_name_map, internal_keys = assign_mappings()

    mapped_field_names = [field_name_map.get(name, name) for name in internal_keys]
    field_info_map = jira_to_github.get_field_ids(project_id, mapped_field_names, headers)

    field_ids = dict(zip(internal_keys, field_info_map.values()))
    item_id = jira_to_github.add_issue_to_project(project_id, gh_issue["id"], headers)

    custom_values = {
        "status": status_mapped,
        "nerc_id": nerc_id,
        "ukri_id": ukri_id,
        "data_centre": data_centre,
        "pi_name": pi_name,
        "pi_email": pi_email,
        "actual_start_date": actual_start_date.strftime("%Y-%m-%d"), # Update date fields to string format for update_custom_field function
        "actual_end_date": actual_end_date.strftime("%Y-%m-%d"),
        "dmp_due": dmp_due.strftime("%Y-%m-%d"),
        "funder": "NERC"
    }

    for key, field_info in field_ids.items():
        value = custom_values.get(key, "")
        jira_to_github.update_custom_field(project_id, item_id, field_info, value, headers)

    return gh_issue
