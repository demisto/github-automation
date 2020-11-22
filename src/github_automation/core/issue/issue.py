from __future__ import absolute_import

from github_automation.common.constants import (DEFAULT_PRIORITY_LIST,
                                                SAME_LEVEL_PRIORITY_IDENTIFIER)
from github_automation.core.issue.pull_request import (PullRequest,
                                                       parse_pull_request)


def _extract_assignees(assignee_edges):
    assignees = []
    for edge in assignee_edges:
        node_data = edge.get('node')
        if node_data:
            assignees.append(node_data['login'])

    return assignees


def _get_pull_request(issue_node):
    timeline_nodes = issue_node.get('timelineItems', {}).get('nodes', [])
    for timeline_node in timeline_nodes:
        if not timeline_node or 'willCloseTarget' not in timeline_node:
            continue

        if timeline_node['willCloseTarget'] and timeline_node['source']['__typename'] == 'PullRequest' \
                and timeline_node['source']['state'] == 'OPEN' and not timeline_node['source']['isDraft']:

            return PullRequest(**parse_pull_request(timeline_node))


def get_labels(label_edges):
    label_names = []
    for edge in label_edges:
        node_data = edge.get('node')
        if node_data:
            label_names.append(node_data['name'])

    return label_names


def _get_milestone(github_issue_object):
    if 'milestone' in github_issue_object and github_issue_object['milestone']:
        return github_issue_object['milestone']['title']

    return None


def _extract_project_cards(project_cards):
    card_id_project = {}
    for node in project_cards.get('nodes', []):
        card_id_project[node['id']] = {
            "project_number": node['project']['number']
        }
        if 'column' in node and node['column'] and 'name' in node['column']:
            card_id_project[node['id']]['project_column'] = node['column']['name']

    return card_id_project


def parse_issue(github_issue):
    return {
        "id": github_issue['id'],
        "title": github_issue['title'],
        "number": github_issue['number'],
        "assignees": _extract_assignees(github_issue.get('assignees', {}).get('edges', [])),
        "pull_request": _get_pull_request(github_issue),
        "labels": get_labels(github_issue.get('labels', {}).get('edges', [])),
        "milestone": _get_milestone(github_issue),
        "card_id_to_project": _extract_project_cards(github_issue.get('projectCards', {})),
        "state": github_issue.get('state', '')
    }


class Issue(object):
    def __init__(self, id: str, title: str, number: int, assignees: list = None, pull_request: PullRequest = None,
                 labels: list = None, milestone: str = '', card_id_to_project: dict = None, priority_list: list = None,
                 state: str = ''):
        self.id = id
        self.title = title
        self.number = number
        self.state = state

        self.assignees = assignees if assignees else []
        self.pull_request = pull_request

        self.milestone = milestone
        self.labels = labels if labels else []

        self.priority_rank = None
        self.set_priority(priority_list)

        self.card_id_project = card_id_to_project if card_id_to_project else {}

    def add_assignee(self, assignee):
        self.assignees.append(assignee)

    def add_label(self, label):
        self.labels.append(label)

    def get_associated_project(self):
        return [project.get('project_number') for project in self.card_id_project.values() if project]

    def get_card_id_from_project(self, project_number):
        for card_id, project in self.card_id_project.items():
            if project_number == project['project_number']:
                return card_id

    def set_priority(self, priority_list: list = None):
        if not priority_list:
            priority_list = DEFAULT_PRIORITY_LIST

        for index, priority_level in enumerate(priority_list):
            for priority_name in priority_level.split(SAME_LEVEL_PRIORITY_IDENTIFIER):
                if priority_name in self.labels:
                    self.priority_rank = len(priority_list) - index
                    break

            if self.priority_rank:
                break

        else:
            self.priority_rank = 0

    def __gt__(self, other):
        if self.priority_rank > other.priority_rank:
            return True

        elif self.priority_rank == other.priority_rank:
            if self.number < other.number:  # lower issue number means older issue - hence more prioritized
                return True

        return False

    def __lt__(self, other):
        return not self.__gt__(other) and other != self
