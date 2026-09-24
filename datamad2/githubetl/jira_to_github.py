"""
# JIRA TO GITHUB
# A python script which creates GitHub issues in a GitHub Project from Jira issues

# Given a Jira issue key in a list of Jira issue keys, this script:
    # 1. Fetches links, abstract, subtask, and comment data using the Jira REST API v2
    # 2. Formats the fetched data into a markdown payload for the GitHub issue
    # 3. Creates a GitHub issue in a specified GitHub Project using the GitHub GraphQL API
    # 4. Adds the GitHub issue link to the Jira issue as a comment using the Jira REST API v2

# Requires two JSON files which map:
    # Jira statuses to GitHub Project statuses
    # Jira usernames to GitHub usernames

# Useage
    # Safe mode (preview only)
        # python jira_to_github.py 
        # --jira_assignee email@example.com 
        # --safe_mode

    # Real mode (create all issues per assignee, or choose to create, skip, or quit per-issue):
        # python jira_to_github.py
        # --jira_assignee email@example.com 
        # --owner cedadev 
        # --repo data-management 
        # --project_name "NERC grant data management tracking" 
        # --jira_token YOUR_JIRA_TOKEN
        # --gh_token YOUR_GITHUB_TOKEN
        # --real_mode 
        # --confirm_each
"""

# import modules
import argparse
import calendar
import json
import requests
from datetime import datetime

# ---------------- SETUP ----------------
JIRA_BASE_URL = "https://jira.ceh.ac.uk"
GITHUB_API_URL = "https://api.github.com/graphql"

# ---------------- CLI HELPERS ----------------
def build_parser():
    """Build the command-line parser for safe and real migration modes."""
    parser = argparse.ArgumentParser(description="Create GitHub issues from Jira using REST and GraphQL APIs.")
    parser.add_argument("--gh_token", help="GitHub Personal Access Token.")
    parser.add_argument("--owner", help="GitHub organization or user name.")
    parser.add_argument("--repo", help="GitHub repository name.")
    parser.add_argument("--project_name", help="GitHub Project name.")
    parser.add_argument("--issue_key", help="Jira issue key to process")
    parser.add_argument("--jira_token", required=True, help="Jira API token.")
    parser.add_argument("--jira_assignee", required=True, help="Jira assignee email.")
    parser.add_argument("--safe_mode", action="store_true", help="Preview only; does not require GitHub settings.")
    parser.add_argument("--real_mode", action="store_true", help="Create GitHub issues using the supplied GitHub settings.")
    parser.add_argument("--confirm_each", action="store_true", help="Ask for confirmation before creating each GitHub issue when running in real_mode.")

    return parser

def resolve_mode(args, parser):
    """Resolve the requested migration mode, defaulting to safe mode."""
    if args.safe_mode and args.real_mode:
        parser.error("Choose either safe mode or real mode, not both.")
    if args.real_mode:
        return "real_mode"
    if args.safe_mode:
        return "safe_mode"
    return "safe_mode"

# ---------------- GITHUB GRAPHQL FUNCTIONS ----------------
def graphql_query(query, variables=None, headers=None, url=GITHUB_API_URL):
    """Execute a GraphQL query or mutation against GitHub API."""
    try:
        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
        if response.status_code != 200:
            return {"errors": [f"HTTP {response.status_code}: {response.text}"], "data": None}
        result = response.json()
        if not isinstance(result, dict):
            return {"errors": ["Invalid response format"], "data": None}
        return result
    except Exception as e:
        return {"errors": [str(e)], "data": None}

def _validate_graphql_result(result, context="GraphQL query"):
    """Raise an exception when a GraphQL response is missing or contains errors."""
    if result is None or not isinstance(result, dict):
        raise Exception(f"Unexpected response from GraphQL for {context}: {result}")
    if result.get("errors"):
        raise Exception(f"GraphQL errors for {context}: {result.get('errors')}")

def get_repository_id(owner, repo, headers):
    """Return the GitHub repository node ID required by issue mutations."""
    query = """
    query($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) {
        id
      }
    }
    """
    variables = {"owner": owner, "repo": repo}
    result = graphql_query(query, variables, headers)
    repo_data = result.get("data", {}).get("repository")
    if not repo_data:
        raise Exception(f"Repository '{owner}/{repo}' not found.")
    return repo_data["id"]

def get_project_id(owner, repo, project_name, headers):
    """Find a ProjectV2 by title across the owner and repository scopes."""
    query = """
    query($owner: String!, $repo: String!) {
      user(login: $owner) {
        projectsV2(first: 50) { nodes { id title } }
      }
      organization(login: $owner) {
        projectsV2(first: 50) { nodes { id title } }
      }
      repository(owner: $owner, name: $repo) {
        projectsV2(first: 50) { nodes { id title } }
      }
    }
    """
    variables = {"owner": owner, "repo": repo}
    result = graphql_query(query, variables, headers)

    user_projects = (result.get("data", {}).get("user") or {}).get("projectsV2", {}).get("nodes", [])
    org_projects = (result.get("data", {}).get("organization") or {}).get("projectsV2", {}).get("nodes", [])
    repo_projects = (result.get("data", {}).get("repository") or {}).get("projectsV2", {}).get("nodes", [])

    all_projects = user_projects + org_projects + repo_projects
    for project in all_projects:
        if project["title"].lower() == project_name.lower():
            return project["id"]

    raise Exception(f"Project '{project_name}' not found under user, organization, or repository '{owner}/{repo}'.")

def get_field_ids(project_id, field_names, headers):
    """Return project field metadata, including option IDs for select fields."""
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          fields(first: 50) {
            nodes {
              ... on ProjectV2FieldCommon {
                id
                name
                dataType
              }
              ... on ProjectV2SingleSelectField {
                options { id name }
              }
              ... on ProjectV2IterationField {
                id
                name
              }
            }
          }
        }
      }
    }
    """
    variables = {"projectId": project_id}
    result = graphql_query(query, variables, headers)
    fields = result.get("data", {}).get("node", {}).get("fields", {}).get("nodes", [])
    if not fields:
        raise Exception(f"No fields found for project {project_id}. Response: {result}")

    field_info = {}
    for name in field_names:
        match = next((f for f in fields if f.get("name", "").strip().lower() == name.strip().lower()), None)
        if not match:
            raise Exception(f"Field '{name}' not found. Available fields: {[f.get('name') for f in fields]}")
        field_info[name] = {
            "id": match["id"],
            "name": match["name"],
            "type": match.get("dataType", "TEXT"),
            "options": match.get("options", [])
        }
    return field_info

def get_label_ids(owner, repo, label_names, headers):
    """Return IDs for matching repository labels, ignoring unknown labels."""
    query = """
    query($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) {
        labels(first: 50) {
          nodes { id name }
        }
      }
    }
    """
    variables = {"owner": owner, "repo": repo}
    result = graphql_query(query, variables, headers)
    labels = result.get("data", {}).get("repository", {}).get("labels", {}).get("nodes", [])
    label_ids = []
    for name in label_names:
        match = next((l for l in labels if l["name"].lower() == name.lower()), None)
        if match:
            label_ids.append(match["id"])
    return label_ids

def get_type_ids(owner, repo, issue_type_names, headers):
    """Return IDs for matching repository-level GitHub issue types."""
    query = """
    query($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) {
        issueTypes(first: 50) {
          nodes { id name }
        }
      }
    }
    """
    variables = {"owner": owner, "repo": repo}
    result = graphql_query(query, variables, headers)
    issue_types = result.get("data", {}).get("repository", {}).get("issueTypes", {}).get("nodes", [])
    type_ids = []
    for name in issue_type_names:
        match = next((i for i in issue_types if i["name"].lower() == name.lower()), None)
        if match:
            type_ids.append(match["id"])
    return type_ids

def update_issue_type(issue_id, type_id, headers, safe_mode=False):
    """Try to set the repository-level issue type for an existing issue.
    This function attempts several plausible input field names until one succeeds.
    """
    if safe_mode:
        return None

    mutation = """
    mutation($input: UpdateIssueInput!) {
      updateIssue(input: $input) {
        issue { id }
      }
    }
    """

    # Candidate input keys to try (singular and plural variations).
    candidates = ["issueTypeId", "typeId", "issueTypeIds", "typeIds"]
    errors = []
    for key in candidates:
        input_data = {"id": issue_id}
        # plural keys expect a list
        if key.endswith("s"):
            input_data[key] = [type_id]
        else:
            input_data[key] = type_id

        variables = {"input": input_data}
        result = graphql_query(mutation, variables, headers)
        # if no result or errors, capture and try next candidate
        if not isinstance(result, dict):
            errors.append(f"{key}: unexpected non-dict response {result}")
            continue
        if result.get("errors"):
            # record the error messages and try next
            msgs = [e.get("message") if isinstance(e, dict) else str(e) for e in result.get("errors")]
            errors.append(f"{key}: {msgs}")
            # try next candidate
            continue

        # success
        return result.get("data", {}).get("updateIssue", {}).get("issue")

    # If we reach here, all attempts failed
    raise Exception(f"Failed to set issue type for {issue_id}. Attempts: {errors}")

def get_user_ids(owner, repo, usernames, headers):
    """Return collaborator IDs for GitHub usernames that can be assigned."""
    query = """
    query($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) {
        collaborators {
          nodes { id login }
        }
      }
    }
    """
    variables = {"owner": owner, "repo": repo}
    result = graphql_query(query, variables, headers)
    users = result.get("data", {}).get("repository", {}).get("collaborators", {}).get("nodes", [])
    user_ids = []
    for name in usernames:
        match = next((u for u in users if u["login"].lower() == name.lower()), None)
        if match:
            user_ids.append(match["id"])
    return user_ids

# ---------------- GITHUB ISSUE CREATION FUNCTIONS ----------------
def create_issue(repository_id, title, body, headers, assignee_ids=None, type_ids=None, safe_mode=False):
    """Create a GitHub issue and return its ID, number, and URL."""
    if safe_mode:
        return None
    mutation = """
    mutation($input: CreateIssueInput!) {
      createIssue(input: $input) {
        issue { id number url }
      }
    }
    """
    input_data = {
        "repositoryId": repository_id,
        "title": title,
        "body": body
    }
    if assignee_ids:
        input_data["assigneeIds"] = assignee_ids
    if type_ids:
        input_data["typeIds"] = type_ids

    variables = {"input": input_data}
    result = graphql_query(mutation, variables, headers)
    if not isinstance(result, dict):
        raise Exception(f"Unexpected response from GraphQL: {result}")
    if result.get("errors"):
        raise Exception(f"GraphQL errors creating issue: {result.get('errors')}")
    data = result.get("data")
    if not data or "createIssue" not in data or not data["createIssue"]:
        raise Exception(f"Failed to create issue. Response: {result}")
    return data["createIssue"]["issue"]

def add_issue_to_project(project_id, issue_id, headers, safe_mode=False):
    """Add a GitHub issue to a ProjectV2 and return its project item ID."""
    if safe_mode:
        return None
    mutation = """
    mutation($input: AddProjectV2ItemByIdInput!) {
      addProjectV2ItemById(input: $input) {
        item { id }
      }
    }
    """
    variables = {"input": {"projectId": project_id, "contentId": issue_id}}
    result = graphql_query(mutation, variables, headers)
    if not isinstance(result, dict):
        raise Exception(f"Unexpected response from GraphQL: {result}")
    if result.get("errors"):
        raise Exception(f"GraphQL errors adding item to project: {result.get('errors')}")
    data = result.get("data")
    if not data or "addProjectV2ItemById" not in data or not data["addProjectV2ItemById"]:
        raise Exception(f"Failed to add issue to project. Response: {result}")
    return data["addProjectV2ItemById"]["item"]["id"]

def update_custom_field(project_id, item_id, field_info, value, headers, safe_mode=False):
    """Set a ProjectV2 field using the GraphQL value format for its type."""
    if safe_mode:
        return
    field_id = field_info["id"]
    field_type = field_info["type"]
    gql_value = None

    if field_type == "TEXT":
        gql_value = {"text": value}
    elif field_type == "DATE":
        try:
            dt = datetime.strptime(value, "%Y-%m-%d")
            gql_value = {"date": dt.strftime("%Y-%m-%d")}
        except ValueError:
            print(f"Warning: Invalid date format for field '{field_info['name']}': {value}")
            return
    elif field_type == "SINGLE_SELECT":
        option = next((o for o in field_info["options"] if o["name"].strip().lower() == value.strip().lower()), None)
        if not option:
            print(f"Warning: Option '{value}' not found for field '{field_info['name']}'.")
            return
        gql_value = {"singleSelectOptionId": option["id"]}
    elif field_type in ["TYPE", "MULTI_SELECT"]:
        types = [l.strip() for l in value.split(",") if l.strip()]
        option_ids = []
        for type in types:
            option = next((o for o in field_info["options"] if o["name"].strip().lower() == type.lower()), None)
            if option:
                option_ids.append(option["id"])
        if option_ids:
            gql_value = {"multiSelectOptionIds": option_ids}
        else:
            print(f"Warning: Option '{value}' not found for field '{field_info['name']}'.")
            return
    else:
        return

    mutation = """
    mutation($input: UpdateProjectV2ItemFieldValueInput!) {
      updateProjectV2ItemFieldValue(input: $input) {
        projectV2Item { id }
      }
    }
    """
    variables = {"input": {"projectId": project_id, "itemId": item_id, "fieldId": field_id, "value": gql_value}}
    result = graphql_query(mutation, variables, headers)
    if not isinstance(result, dict):
        raise Exception(f"Unexpected response from GraphQL when updating field: {result}")
    if result.get("errors"):
        raise Exception(f"GraphQL errors updating field '{field_info.get('name')}': {result.get('errors')}")

def calculate_dmp_due_date(actual_start_date):
    """Return the date six calendar months after a YYYY-MM-DD start date."""
    if not actual_start_date:
        return ""

    start_date = datetime.strptime(actual_start_date, "%Y-%m-%d")
    target_year = start_date.year + (start_date.month + 5) // 12
    target_month = (start_date.month + 5) % 12 + 1
    target_day = min(start_date.day, calendar.monthrange(target_year, target_month)[1])
    return f"{target_year:04d}-{target_month:02d}-{target_day:02d}"

# ---------------- JIRA ISSUE KEYS FUNCTION ----------------
def get_issue_keys(assignee):
    """Return Jira issue keys assigned to the requested Jira user."""

    # Build request for API call to issue keys endpoint
    url = f"{JIRA_BASE_URL}/rest/api/2/search"
    headers = {
    "Authorization": f"Bearer {JIRA_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json"
    }

    # JQL query
    jql = (
        f'assignee = "{assignee}" '
        f'AND issuetype = "Data Management Tracking"'
    )
    
    params={
        "jql": jql,
        "fields": "key",
        "maxResults": 1000
    }

    # Make API call and handle response
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        issues = data.get("issues", [])
    else:
        return []
    
    issue_keys = []
    for issue in issues:
        issue_key = issue["key"]
        issue_keys.append(issue_key)

    return issue_keys

# ---------------- JIRA COMMENT FUNCTION ----------------
def add_jira_comment(issue_key, timestamp, github_issue_url, jira_headers=None):
    """Add a comment to a Jira issue via the Jira REST API v2."""
    if jira_headers is None:
        jira_headers = {
            "Authorization": f"Bearer {JIRA_TOKEN}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    url = f"{JIRA_BASE_URL}/rest/api/2/issue/{issue_key}/comment"
    payload = {"body": f"Migrated to GitHub on {timestamp}: {github_issue_url}."}
    response = requests.post(url, headers=jira_headers, json=payload)

    if response.status_code not in (200, 201):
        raise Exception(f"Failed to add Jira comment: {response.status_code} {response.text}")

    return response.json()

def change_jira_status(issue_key, status_name, jira_headers=None):
    """Transition a Jira issue to the named status."""
    if jira_headers is None:
        jira_headers = {
            "Authorization": f"Bearer {JIRA_TOKEN}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    transitions_url = f"{JIRA_BASE_URL}/rest/api/2/issue/{issue_key}/transitions"
    response = requests.get(transitions_url, headers=jira_headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch Jira transitions: {response.status_code} {response.text}")

    transitions = response.json().get("transitions", [])
    transition = next(
        (item for item in transitions if item.get("to", {}).get("name", "").lower() == status_name.lower()),
        None
    )
    if not transition:
        raise Exception(f"No transition to Jira status '{status_name}' is available for {issue_key}.")

    response = requests.post(
        transitions_url,
        headers=jira_headers,
        json={"transition": {"id": transition["id"]}}
    )
    if response.status_code != 204:
        raise Exception(f"Failed to change Jira status: {response.status_code} {response.text}")

    return response

# ---------------- CREATE ISSUE PAYLOAD FUNCTION ----------------
def fetch_and_create(issue_key, repository_id, project_id, field_ids, headers, owner, repo, safe_mode=False):
    """Fetch one Jira issue, build its GitHub representation, and migrate it."""
    issues_preview = []

    status_mapping = {}
    try:
        with open("jira_to_github_statuses.json", "r") as f:
            status_mapping = json.load(f)
    except FileNotFoundError:
        print("Warning: jira_to_github_statuses.json not found.")

    username_mapping = {}
    try:
        with open("jira_to_github_usernames.json", "r") as f:
            username_mapping = json.load(f)
    except FileNotFoundError:
        print("Warning: jira_to_github_usernames.json not found.")

    # Build request for API call to main issue endpoint
    url = f"{JIRA_BASE_URL}/rest/api/2/issue/{issue_key}"
    jira_headers = {
        "Authorization": f"Bearer {JIRA_TOKEN}",
        "Accept": "application/json"
    }

    # Make API call and handle response
    response = requests.get(url, headers=jira_headers)
    if response.status_code == 200:
        issue_data = response.json()
    else:
        print(f"Failed to fetch issue: {response.status_code}")
        print(response.text)
        return None

    # Link to jira issue = jira_issue_link
    issue_link = f"{JIRA_BASE_URL}/browse/{issue_key}"

    # ["assignee"]["name"] AND ["reporter"]["name"] = assignee
    assignee = []
    if issue_data["fields"]["assignee"] is not None:
        assignee.append(issue_data["fields"]["assignee"]["name"])
    if issue_data["fields"]["reporter"] is not None:
        assignee.append(issue_data["fields"]["reporter"]["name"])
    else:
        assignee.append("Unassigned")

    # Remove duplicates
    assignee = list(set(assignee))
    # Map Jira assignee to GitHub assignee
    mapped_usernames = [username_mapping.get(u) for u in assignee if username_mapping.get(u)]

    # ["status"]["name"] = status
    status = issue_data["fields"]["status"]["name"]
    status_mapped = status_mapping.get(status, "Unknown")

    # ["customfield_11660"] = actual_start_date
    actual_start_date = issue_data["fields"]["customfield_11660"]
    dmp_due = calculate_dmp_due_date(actual_start_date)

    # ["customfield_11455"] = actual_end_date
    actual_end_date = issue_data["fields"]["customfield_11455"]

    # ["customfield_11658"] = nerc_id
    nerc_id = issue_data["fields"]["customfield_11658"]

    # No dedicated field for this in Jira, only accessible if there are child grants whose names start with the five-digit UKRI ID
    # Below is a workaround: first five digits of ["customfield_14750"] = ukri_id, otherwise field will be blank
    child_grants = issue_data["fields"]["customfield_14750"]
    if child_grants == None:
        ukri_id = ""
    elif child_grants[:2] == "NE":
        ukri_id = ""
    else:
        ukri_id = issue_data["fields"]["customfield_14750"][:5]

    # ["customfield_11659"] = pi_name
    pi_name = issue_data["fields"]["customfield_11659"]

    # ["customfield_13576"] = pi_email, or if None in ["customfield_13576"], pi_email = "NOT FOUND DURING MIGRATION"
    if issue_data["fields"]["customfield_13576"] != None:
        pi_email = issue_data["fields"]["customfield_13576"].lower()
    else:
        pi_email = "NOT FOUND DURING MIGRATION"

    # ["summary"] = title
    title = issue_data["fields"]["summary"]

    # ["description"] = abstract
    abstract = issue_data["fields"]["description"]

    # ["fields"]["subtasks"] = subtasks
    subtasks = ""
    for subtask in issue_data["fields"]["subtasks"]:
        subtask_key = subtask["key"]
        subtask_summary = subtask["fields"]["summary"]
        subtask_status = subtask["fields"]["status"]["name"]
        subtasks += f"[{subtask_summary}](https://jira.ceh.ac.uk/browse/{subtask_key}) - {subtask_status}\n"

    # ["fields"]["comment"]["comments"] = comments
    comments = "\n\n"
    for comment in issue_data["fields"]["comment"]["comments"]:
        comment_author = comment["author"]["displayName"]
        comment_created = datetime.strptime(comment["created"], "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%d-%b-%Y %H:%M")
        comment_body = comment["body"]
        comments += f"**{comment_author} - {comment_created}:**\n"
        comments += f"{comment_body}"
        comments += "\n\n"

    # Build request for API call to external links endpoint
    url_links = f"{JIRA_BASE_URL}/rest/api/2/issue/{issue_key}/remotelink"
    jira_headers = {
        "Authorization": f"Bearer {JIRA_TOKEN}",
        "Accept": "application/json"
    }

    # Make API call and handle response
    response_links = requests.get(url_links, headers=jira_headers)
    if response_links.status_code == 200:
        issue_data_links = response_links.json()
    else:
        print(f"Failed to fetch issue: {response_links.status_code}")
        print(response_links.text)
        return

    # Compile all links into a single markdown string
    external_links = ""
    for link in issue_data_links: 
        link_title = link["object"]["title"]
        link_url = link["object"]["url"]
        if "Help Scout" in link_title:
            link_title = "Help Scout"
            external_links += f"- [{link_title}]({link_url})\n"
        elif "Datamad" in link_title:
            link_title = "DataMad"
            external_links += f"- [{link_title}]({link_url})\n"
        elif "DSW" in link_title:
            link_title = "DSW"
            external_links += f"- [{link_title}]({link_url})\n"

    timestamp = datetime.now().strftime("%Y-%m-%d %X")

    # Build issue body
    body = f"""# Links
    {external_links}- [Dataset record]()
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
    - [ ] Create new conversation & send DMP link (saved reply 01.01) (Help Scout)
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
    - [ ] 👋 Send data due check-in (saved reply 03.03) (Help Scout)
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

    Migrated from [this Jira issue]({issue_link}) on {timestamp}. 

    <details><summary>Jira subtasks (legacy)</summary>

    {subtasks}
    </details>

    <details><summary>Jira comments (legacy)</summary>{comments}</details>"""

    # Remove chunks of four whitespaces from body
    body = body.replace("    ", "")

    # Create issue or prepare safe mode preview
    if safe_mode:
        issues_preview.append({
            "title": title, 
            "body": body, 
            "assignees": mapped_usernames, 
            "type": "Project", 
            "status": status_mapped,
            "actual_start_date": actual_start_date,
            "dmp_due": dmp_due,
            "data_centre": "CEDA",
            "actual_end_date": actual_end_date,
            "nerc_id": nerc_id,
            "ukri_id": ukri_id,
            "pi_name": pi_name,
            "pi_email": pi_email,
        })
        return issues_preview
    else:
        assignee_ids = get_user_ids(owner, repo, mapped_usernames, headers)
        gh_issue = create_issue(repository_id, title, body, headers, assignee_ids, None)
        print(f"Created issue: {gh_issue['url']}")

        try:
            add_jira_comment(issue_key, timestamp, gh_issue["url"], jira_headers)
            print(f"Added Jira migration comment for {issue_key}")
            try:
                change_jira_status(issue_key, "Deprecated", jira_headers)
                print(f"Changed Jira status to 'Deprecated' for {issue_key}")
            except Exception as e:
                print(f"Warning: failed to change Jira status for {issue_key}: {e}")
        except Exception as e:
            print(f"Warning: failed to add Jira migration comment for {issue_key}: {e}")

        # Attempt to set the repository-level issue type to 'Project'
        try:
            type_ids = get_type_ids(owner, repo, ["Project"], headers)
            if type_ids:
                type_id = type_ids[0]
                try:
                    update_issue_type(gh_issue["id"], type_id, headers)
                    print(f"Set issue type to 'Project' for {gh_issue['url']}")
                except Exception as e:
                    print(f"Warning: failed to set issue type for {gh_issue['url']}: {e}")
            else:
                print("Warning: repository has no matching issue type 'Project'.")
        except Exception as e:
            print(f"Warning: could not fetch issue type ids: {e}")
        item_id = add_issue_to_project(project_id, gh_issue["id"], headers)
        custom_values = {
            "status": status_mapped,
            "nerc_id": nerc_id,
            "ukri_id": ukri_id,
            "data_centre": "CEDA",
            "pi_name": pi_name,
            "pi_email": pi_email,
            "actual_start_date": actual_start_date,
            "actual_end_date": actual_end_date,
            "dmp_due": dmp_due,
            "funder": "NERC"
        }

        for key, field_info in field_ids.items():
            value = custom_values.get(key, "")
            update_custom_field(project_id, item_id, field_info, value, headers)

    return []

# ---------------- CLI ----------------
if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    JIRA_TOKEN = args.jira_token
    mode = resolve_mode(args, parser)

    if mode == "safe_mode":
        print("")
        print("---- SAFE MODE ENABLED ----")
        print("")
        print (f"Assignee has {len(get_issue_keys(args.jira_assignee))} issues")
        print("")
        if input("Do you want to print all issues? (y/n): ").lower() == "y":
            for issue_key in get_issue_keys(args.jira_assignee):
                preview = fetch_and_create(issue_key, None, None, None, None, None, None, safe_mode=True)
                print(f"\nPreview for {issue_key}:")
                print(json.dumps(preview, indent=2))
    else:
        missing = [name for name in ("gh_token", "owner", "repo", "project_name") if not getattr(args, name)]
        if missing:
            parser.error(f"For real mode, you must provide: {', '.join(missing)}")

        headers = {"Authorization": f"Bearer {args.gh_token}", "Content-Type": "application/json"}

        print("Fetching repository ID...")
        repository_id = get_repository_id(args.owner, args.repo, headers)
        print(f"Repository ID: {repository_id}")

        print("Fetching project ID...")
        project_id = get_project_id(args.owner, args.repo, args.project_name, headers)
        print(f"Project ID: {project_id}")

        print("Fetching field IDs...")
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
        mapped_field_names = [field_name_map.get(name, name) for name in internal_keys]
        field_info_map = get_field_ids(project_id, mapped_field_names, headers)
        field_ids = dict(zip(internal_keys, field_info_map.values()))
        print(f"Field IDs: {field_ids}")
     
        for issue_key in get_issue_keys(args.jira_assignee):
            if getattr(args, "confirm_each", False):
                resp = input(f"Create GitHub issue from Jira issue {issue_key}? (y/n/q): ").strip().lower()
                if resp in ("q", "quit"):
                    print("Quitting migration script.")
                    break
                if resp not in ("y", "yes"):
                    print(f"Skipping {issue_key}.")
                    continue

            print(f"Creating GitHub issue from Jira issue {issue_key}")
            fetch_and_create(issue_key, repository_id, project_id, field_ids, headers, args.owner, args.repo, safe_mode=False)