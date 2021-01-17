from __future__ import absolute_import

from github_automation.common.utils import get_labels
from github_automation.core.project_item.base_project_item.base_project_item import BaseProjectItem, extract_assignees, \
    get_milestone, extract_project_cards
from github_automation.core.project_item.issue.pull_request import PullRequest, parse_pull_request


def _get_pull_request(issue_node):
    timeline_nodes = issue_node.get('timelineItems', {}).get('nodes', [])
    for timeline_node in timeline_nodes:
        if not timeline_node or 'willCloseTarget' not in timeline_node:
            continue

        if timeline_node['willCloseTarget'] and timeline_node['source']['__typename'] == 'PullRequest' \
                and timeline_node['source']['state'] == 'OPEN' and not timeline_node['source']['isDraft']:

            return PullRequest(**parse_pull_request(timeline_node))


def parse_issue(github_issue):
    return {
        "id": github_issue['id'],
        "title": github_issue['title'],
        "number": github_issue['number'],
        "assignees": extract_assignees(github_issue.get('assignees', {}).get('edges', [])),
        "pull_request": _get_pull_request(github_issue),
        "labels": get_labels(github_issue.get('labels', {}).get('edges', [])),
        "milestone": get_milestone(github_issue),
        "card_id_to_project": extract_project_cards(github_issue.get('projectCards', {})),
        "state": github_issue.get('state', '')
    }


class Issue(BaseProjectItem):
    def __init__(self, id: str, title: str, number: int, assignees: list = None, pull_request: PullRequest = None,
                 labels: list = None, milestone: str = '', card_id_to_project: dict = None, priority_list: list = None,
                 state: str = ''):
        super().__init__(id, title, number, assignees, labels, milestone, card_id_to_project, priority_list, state)
        self.pull_request = pull_request
