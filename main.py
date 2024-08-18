from atlassian import Jira, Confluence
from datetime import datetime as    dt
import os
import sys
import argparse

## Handle arguments parsing for incoming service now change number.

parser = argparse.ArgumentParser(description='Get change number process.')
parser.add_argument('--change_number', type=str, help='The change number to be processed')
args = parser.parse_args()
CHG_NUMBER = args.change_number


# Configure the Jira instance.

jira = Jira(
    url=os.getenv("JIRA_URL"),
    username=os.getenv("JIRA_USER"),
    password=os.getenv("JIRA_TOKEN"),
    cloud=True
)

# get corresponding project and board

proj  = os.getenv("JIRA_PROJECT")
board = jira.get_all_agile_boards(project_key=proj)["values"][0]
sprint = jira.get_all_sprints_from_board(board_id=board["id"])["values"]


# Create Jira stories and subtasks

fields = {
    "issuetype": {
        "name": "Story"
    },
    "project": {
        "key": proj
    },
    'assignee':
        {'emailAddress': 'roelh96@gmail.com'}
    ,
    "summary": CHG_NUMBER,
    "description": "A story triggered via the api",
}


field_sub_task = {
    "issuetype": {
        "name": "Subtaak",
    },
    "parent":{
        "key": None
        },
    "project": {
        "key": proj
    },'assignee': {'emailAddress': 'roelh96@gmail.com'},
    "summary": f"subtask {CHG_NUMBER}",
    "description": "A  subtask story triggered via the api",
}


issues = jira.get_all_issues_for_sprint_in_board(board_id=board["id"], sprint_id=sprint[0]["id"])["issues"]
existing_issue = [issue for issue in issues if issue["fields"]["summary"] == CHG_NUMBER]

if not existing_issue:
    print("Issue does not exist, creating issue")
    issue = jira.issue_create_or_update(
        fields=fields
    )
    jira.add_issues_to_sprint(
        sprint_id=sprint[0]["id"],
        issues=[issue["key"]]
        )

    field_sub_task["parent"]["key"] = issue["key"]
    jira.issue_create(fields=field_sub_task)
else:
    print("Issue already exists")
    issue = existing_issue[0]





################# Confluence ####################


# Configure the Confluence instance.


confluence = Confluence(
    url=os.getenv("CONFLUENCE_URL"),
    username=os.getenv("CONFLUENCE_USER"),
    password=os.getenv("CONFLUENCE_TOKEN"),
    cloud=True
    )

# Get page body

template_id = os.getenv("CONFLUENCE_TEMPLATE_ID")
content = confluence.get_content_template(template_id)["body"]["storage"]["value"]


fromatted_content = content.format(
    CHANGE_NUMBER=CHG_NUMBER,
    DESCRIPTION="This is a description",
    EXECUTE_DATE=dt.now().strftime("%Y-%m-%d"),
    CHANGE_LEAD="Roel H",
    JIRA_ID=issue["key"]
)


pages = confluence.get_all_pages_by_label("posit_change")

present  = {page["title"]:page for page in pages}

if CHG_NUMBER not in present:
    page = confluence.create_page(
        space="SSDS",
        title=CHG_NUMBER,
        body=fromatted_content,
        parent_id=os.getenv("CONFLUENCE_PARENT_PAGE")
    )

    confluence.set_page_label(page["id"], "posit_change")
else:
    page = confluence.update_existing_page(
        page_id=present[CHG_NUMBER]["id"],
        title=CHG_NUMBER,
        body=fromatted_content
    )