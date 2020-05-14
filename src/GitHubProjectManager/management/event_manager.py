from __future__ import absolute_import

import json

from GitHubProjectManager.common.utils import (
    get_column_issues_with_prev_column, get_first_column_issues)
from GitHubProjectManager.core.issue.issue import Issue, parse_issue
from GitHubProjectManager.core.project.project import Project, parse_project
from GitHubProjectManager.management.configuration import Configuration
from GitHubProjectManager.management.github_client import GraphQLClient


class EventManager(object):
    DEFAULT_PRIORITY_LIST = ['Critical', 'High', 'Medium', 'Low']

    def __init__(self, conf: str, event: str, quiet: bool = False, log_path: str = '', verbose: int = 2,
                 client=None, api_key=None):
        self.config = None
        self.conf_paths = conf.split(',')
        self.quiet = quiet
        self.log_path = log_path
        self.verbose = verbose

        config = Configuration(self.conf_paths[0])
        config.load_general_properties()
        self.project_owner = config.project_owner
        self.repository_name = config.repository_name

        self.event = json.loads(event)
        self.client = client if client else GraphQLClient(api_key)

    @staticmethod
    def is_matching_issue(issue_labels, must_have_labels, cant_have_labels):
        for label in must_have_labels:
            if label not in issue_labels:
                return False

        for label in cant_have_labels:
            if label in issue_labels:
                return False

        return True

    @staticmethod
    def get_issue_number(event):
        return event['issue']['number']

    def get_prev_column_cursor(self, column_name):
        layout = self.client.get_project_layout(owner=self.config.project_owner,
                                                repository_name=self.config.repository_name,
                                                project_number=self.config.project_number)

        prev_cursor = ''
        column_edges = layout['repository']['project']['columns']['edges']
        for index, column in enumerate(column_edges):
            if column_name == column['node']['name']:
                if index != 0:
                    prev_cursor = column_edges[index - 1]['cursor']

        return prev_cursor

    def load_project_column(self, column_name):
        prev_cursor = self.get_prev_column_cursor(column_name)
        if prev_cursor:
            response = get_column_issues_with_prev_column(self.client, self.config, prev_cursor)

        else:
            response = get_first_column_issues(self.client, self.config)

        return Project(**parse_project(response.get("repository", {}).get('project', {}), config=self.config))

    def manage_issue_in_project(self, issue):
        if (self.config.remove and self.config.project_number in issue.get_associated_project()
                and not self.is_matching_issue(issue.labels,
                                               self.config.must_have_labels, self.config.cant_have_labels)):

            card_id = [_id for _id, value in issue.card_id_project.items()
                       if value['project_number'] == self.config.project_number][0]
            Project.remove_issue(self.client, issue.title, card_id, self.config)
            return

        matching_column_name = Project.get_matching_column(issue, self.config)
        project = self.load_project_column(matching_column_name)

        if self.config.add and self.config.project_number not in issue.get_associated_project():
            project.add_issue(self.client, issue, matching_column_name, self.config)
            return

        if (self.config.add and not all(project.get_current_location(issue.id))  # The issue is in the triage
                or self.config.move):
            column_name_before, _ = project.get_current_location(issue.id)
            if column_name_before != matching_column_name:
                project.move_issue(self.client, issue, matching_column_name, self.config)
                return

        if self.config.sort:
            column_name_before, _ = project.get_current_location(issue.id)
            if column_name_before == matching_column_name:
                project.columns[matching_column_name].sort_cards(self.client, self.config)

            return

    def get_issue_object(self):
        issue_number = self.get_issue_number(self.event)
        issue_response = self.client.get_issue(
            self.project_owner, self.repository_name, issue_number)  # need to address the remove here
        issue = Issue(**parse_issue(issue_response['repository']['issue']))
        return issue

    def run(self):
        issue = self.get_issue_object()

        for conf_path in self.conf_paths:
            self.config = Configuration(conf_path, self.verbose, self.quiet, self.log_path)
            self.config.load_properties()

            if (self.config.project_number in issue.get_associated_project() or
                    self.is_matching_issue(issue.labels, self.config.must_have_labels, self.config.cant_have_labels)):
                issue.set_priority(self.config.priority_list)
                self.manage_issue_in_project(issue)

            else:
                self.config.logger.debug(f"The issue does not match the filter provided in the configuration "
                                         f"file {conf_path}.")
