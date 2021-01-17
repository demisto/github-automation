from __future__ import absolute_import

import json

from github_automation.common.utils import (get_column_items_with_prev_column,
                                            get_first_column_items,
                                            is_matching_project_item)
from github_automation.core.project_item.issue.issue import Issue, parse_issue
from github_automation.core.project.project import Project, parse_project
from github_automation.core.project_item.pull_request.pull_request import PullRequest, parse_pull_request
from github_automation.management.configuration import Configuration
from github_automation.management.github_client import GraphQLClient


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
    def get_pull_request_number(event):
        if 'pull_request' in event:
            return event['pull_request']['number']
        else:
            print("This is not a pull request.")
            return

    @staticmethod
    def get_issue_number(event):
        if 'issue' in event:
            return event['issue']['number']
        else:
            print("This is not an issue.")
            return

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
            response = get_column_items_with_prev_column(self.client, self.config, prev_cursor)

        else:
            response = get_first_column_items(self.client, self.config)

        return Project(**parse_project(response.get("repository", {}).get('project', {}), config=self.config))

    def manage_issue_in_project(self, issue):
        if (self.config.remove and self.config.project_number in issue.get_associated_project()
                and not is_matching_project_item(issue.labels,
                                                 self.config.must_have_labels, self.config.cant_have_labels,
                                                 self.config.filter_labels)):

            card_id = [_id for _id, value in issue.card_id_project.items()
                       if value['project_number'] == self.config.project_number][0]
            Project.remove_item(self.client, issue.title, card_id, self.config)
            return

        matching_column_name = Project.get_matching_column(issue, self.config)

        if self.config.add and self.config.project_number not in issue.get_associated_project():
            project = self.load_project_column(matching_column_name)
            project.add_item(self.client, issue, matching_column_name, self.config)
            return

        column_name_before = [value['project_column'] for _id, value in issue.card_id_project.items()
                              if value['project_number'] == self.config.project_number][0]
        if (self.config.add and not column_name_before) or \
                (self.config.move and matching_column_name != column_name_before):
            print(f'Moving {issue.title} from {column_name_before}')
            project = self.load_project_column(matching_column_name)
            project.move_item(self.client, issue, matching_column_name, self.config)
            return

        if self.config.sort and column_name_before == matching_column_name:
            project = self.load_project_column(matching_column_name)
            project.columns[matching_column_name].sort_cards(self.client, self.config)

            return

    def get_issue_object(self):
        issue_number = self.get_issue_number(self.event)
        if issue_number is None:
            return   # In case the event is not for an issue

        issue_response = self.client.get_issue(
            self.project_owner, self.repository_name, issue_number)  # need to address the remove here
        issue = Issue(**parse_issue(issue_response['repository']['issue']))
        return issue

    def get_pull_request_object(self):
        pull_request_number = self.get_pull_request_number(self.event)
        if pull_request_number is None:
            return  # In case the event is not a pull request

        pr_response = self.client.get_pull_request(...)
        pull_request = PullRequest(**parse_pull_request(pr_response['repository']['pull_request']))
        return pull_request

    def run(self):
        issue = self.get_issue_object()
        if issue:
            if issue.state == 'CLOSED':
                print("The issue is closed, not taking an action.")
                return

            for conf_path in self.conf_paths:
                self.config = Configuration(conf_path, self.verbose, self.quiet, self.log_path)
                self.config.load_properties()

                if (self.config.project_number in issue.get_associated_project() or
                        is_matching_project_item(issue.labels, self.config.must_have_labels, self.config.cant_have_labels,
                                                 self.config.filter_labels)):
                    issue.set_priority(self.config.priority_list)
                    self.manage_issue_in_project(issue)

                else:
                    self.config.logger.debug(f"The issue does not match the filter provided in the configuration "
                                             f"file {conf_path}.")
        else:
            pull_request = self.get_pull_request_object()  # TODO: Complete this part
            return  # In case the event is not for an issue / pull request
