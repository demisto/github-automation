from __future__ import absolute_import

from github_automation.common.constants import (DEFAULT_PRIORITY_LIST,
                                                SAME_LEVEL_PRIORITY_IDENTIFIER)


def extract_assignees(assignee_edges):
    assignees = []
    for edge in assignee_edges:
        node_data = edge.get('node')
        if node_data:
            assignees.append(node_data['login'])

    return assignees


def extract_project_cards(project_cards):
    card_id_project = {}
    for node in project_cards.get('nodes', []):
        if node and node.get('project'):
            card_id_project[node['id']] = {
                "project_number": node['project']['number']
            }
            if 'column' in node and node['column'] and 'name' in node['column']:
                card_id_project[node['id']]['project_column'] = node['column']['name']

    return card_id_project


def is_review_requested(pull_request_node):
    if pull_request_node['reviewRequests']['totalCount'] or pull_request_node['reviews']['totalCount']:
        return True

    else:
        return False


def is_review_completed(pull_request_node):
    return pull_request_node["reviewDecision"] == "APPROVED"


def is_review_requested_changes(pull_request_node):
    return pull_request_node["reviewDecision"] == "CHANGES_REQUESTED"


class BaseProjectItem(object):
    def __init__(self, id: str, title: str, number: int, assignees: list = None, labels: list = None,
                 card_id_to_project: dict = None, priority_list: list = None, state: str = ''):
        self.id = id
        self.title = title
        self.number = number
        self.state = state

        self.assignees = assignees if assignees else []

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
