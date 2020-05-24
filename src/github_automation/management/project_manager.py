from __future__ import absolute_import

from github_automation.common.constants import OR
from github_automation.common.utils import (get_column_issues_with_prev_column,
                                            get_first_column_issues,
                                            is_matching_issue)
from github_automation.core.issue.issue import Issue, get_labels, parse_issue
from github_automation.core.project.project import Project, parse_project
from github_automation.management.configuration import Configuration
from github_automation.management.github_client import GraphQLClient


class ProjectManager(object):

    def __init__(self, configuration: Configuration, client=None, api_key=None):
        self.config = configuration
        self.client = client if client else GraphQLClient(api_key)

        self.project = self.get_github_project()
        self.matching_issues = self.get_github_issues()  # todo: add the option to add more filters

    def construct_issue_object(self, github_issues):
        issues = {}
        for edge in github_issues:
            node_data = edge['node']
            issue_labels = get_labels(node_data['labels']['edges'])
            if is_matching_issue(issue_labels, self.config.must_have_labels, self.config.cant_have_labels,
                                 self.config.filter_labels):
                issue = Issue(**parse_issue(node_data), priority_list=self.config.priority_list)
                issues[issue.id] = issue

        return issues

    def get_github_project(self):
        layout = self.client.get_project_layout(owner=self.config.project_owner,
                                                repository_name=self.config.repository_name,
                                                project_number=self.config.project_number)

        column_edges = layout['repository']['project']['columns']['edges']
        project_builder = get_first_column_issues(self.client, self.config)
        for index, column in enumerate(column_edges):
            if column['node']['name'] in self.config.column_names:
                if index == 0:
                    continue
                else:
                    prev_cursor = column_edges[index - 1]['cursor']
                    column_response = get_column_issues_with_prev_column(self.client, self.config, prev_cursor)
                    project_builder['repository']['project']['columns']['nodes'].extend(
                        column_response['repository']['project']['columns']['nodes'])

        return Project(**parse_project(project_builder['repository']['project'], self.config))

    @staticmethod
    def construct_filters(cant_have_string, milestone_string, must_labels_string, or_labels, filter_labels):
        filters = []
        base_filter = f'{cant_have_string} {milestone_string} {must_labels_string}'
        for filter_label in filter_labels:
            filter_string = f'{base_filter} label:{filter_label}'
            if or_labels:
                for or_label in or_labels:
                    filters.append(f'{filter_string} label:{or_label}')
            else:
                filters.append(filter_string)

        return filters

    @staticmethod
    def get_filters(config):
        cant_have_string = ' '.join([f'-label:{cant_have_label}' for cant_have_label in config.cant_have_labels])
        milestone_string = f'milestone:{config.filter_milestone}' if config.filter_milestone else ''

        must_labels = []
        or_labels = []
        for must_label in config.must_have_labels:
            if OR in must_label:
                or_labels.extend(must_label.split(OR))
            else:
                must_labels.append(must_label)

        must_labels_string = ' '.join([f'label:{must_label}' for must_label in must_labels])

        filters = ProjectManager.construct_filters(cant_have_string, milestone_string, must_labels_string, or_labels,
                                                   config.filter_labels)
        return filters

    def get_github_issues(self):
        issues = []
        for issue_filter in self.get_filters(self.config):
            response = self.client.search_issues_by_query(
                query=f"repo:{self.config.project_owner}/{self.config.repository_name} is:open "
                      f"{issue_filter} -project:{self.config.project_owner}/"
                      f"{self.config.repository_name}/{self.config.project_number}"
            )
            issues.extend(response.get('search', {}).get('edges', []))

            while response.get('search', {}).get('pageInfo').get('hasNextPage'):
                after = response.get('search', {}).get('pageInfo').get('endCursor')
                response = self.client.search_issues_by_query(
                    query=f"repo:{self.config.project_owner}/{self.config.repository_name} is:open "
                          f"{issue_filter} -project:{self.config.project_owner}/"
                          f"{self.config.repository_name}/{self.config.project_number}",
                    start_cursor=after
                )
                issues.extend(response.get('search', {}).get('edges', []))

        return self.construct_issue_object(issues)

    def add_issues_to_project(self):
        issues_to_add = self.project.find_missing_issue_ids(self.matching_issues)
        self.project.add_issues(self.client, self.matching_issues, issues_to_add, self.config)

    def manage(self):
        if self.config.remove:  # Better to first remove issues that should not be in the board
            self.project.remove_issues(self.client, self.config)

        if self.config.add:
            self.add_issues_to_project()

        if self.config.sort:
            self.project.sort_issues_in_columns(self.client, self.config)

        if self.config.move:
            self.project.move_issues(self.client, self.config)
