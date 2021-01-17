from __future__ import absolute_import

from github_automation.common.utils import (get_column_items_with_prev_column,
                                            get_first_column_items,
                                            is_matching_project_item, get_labels)
from github_automation.core.project_item.issue.issue import Issue, parse_issue
from github_automation.core.project_item.pull_request.pull_request import PullRequest, parse_pull_request
from github_automation.core.project.project import Project, parse_project
from github_automation.management.configuration import Configuration
from github_automation.management.github_client import GraphQLClient


class ProjectManager(object):

    def __init__(self, configuration: Configuration, client=None, api_key=None):
        self.config = configuration
        self.client = client if client else GraphQLClient(api_key)

        self.project = self.get_github_project()
        self.matching_issues = self.get_github_issues()
        self.matching_pull_requests = self.get_github_pull_requests()

    def construct_issue_object(self, github_issues):
        issues = {}
        for edge in github_issues['edges']:
            node_data = edge['node']
            issue_labels = get_labels(node_data['labels']['edges'])
            if is_matching_project_item(issue_labels, self.config.must_have_labels, self.config.cant_have_labels,
                                        self.config.filter_labels):
                issue = Issue(**parse_issue(node_data), priority_list=self.config.priority_list)
                issues[issue.id] = issue

        return issues

    def construct_pull_request_object(self, github_prs):
        prs = {}
        for edge in github_prs['edges']:
            node_data = edge['node']
            pr_labels = get_labels(node_data['labels']['edges'])
            if is_matching_project_item(pr_labels, self.config.must_have_labels, self.config.cant_have_labels,
                                        self.config.filter_labels):
                pull_request = PullRequest(**parse_pull_request(node_data), priority_list=self.config.priority_list)
                prs[pull_request.id] = pull_request

        return prs

    def get_github_project(self):
        layout = self.client.get_project_layout(owner=self.config.project_owner,
                                                repository_name=self.config.repository_name,
                                                project_number=self.config.project_number)

        column_edges = layout['repository']['project']['columns']['edges']
        project_builder = get_first_column_items(self.client, self.config)
        for index, column in enumerate(column_edges):
            if column['node']['name'] in self.config.column_names:
                if index == 0:
                    continue
                else:
                    prev_cursor = column_edges[index - 1]['cursor']
                    column_response = get_column_items_with_prev_column(self.client, self.config, prev_cursor)
                    project_builder['repository']['project']['columns']['nodes'].extend(
                        column_response['repository']['project']['columns']['nodes'])
        return Project(**parse_project(project_builder['repository']['project'], self.config))

    def get_github_issues(self):
        response = self.client.get_github_issues(owner=self.config.project_owner,
                                                 name=self.config.repository_name,
                                                 labels=self.config.filter_labels,
                                                 milestone=self.config.filter_milestone,
                                                 after=None)
        issues = response.get('repository', {}).get('issues', {})

        while response.get('repository', {}).get('issues', {}).get('pageInfo').get('hasNextPage'):
            after = response.get('repository', {}).get('issues', {}).get('pageInfo').get('endCursor')
            response = self.client.get_github_issues(owner=self.config.project_owner,
                                                     name=self.config.repository_name,
                                                     after=after,
                                                     labels=self.config.filter_labels,
                                                     milestone=self.config.filter_milestone)
            issues.get('edges').extend(response.get('repository', {}).get('issues', {}).get('edges'))

        return self.construct_issue_object(issues)

    def get_github_pull_requests(self):
        #TODO: Finish impl
        response = self.client.get_github_pull_requests(owner=self.config.project_owner,
                                                        name=self.config.repository_name,
                                                        labels=self.config.filter_labels,
                                                        milestone=self.config.filter_milestone,
                                                        after=None)
        pull_requests = response.get('repository', {}).get('pull_requests', {})

        while response.get('repository', {}).get('issues', {}).get('pageInfo').get('hasNextPage'):
            after = response.get('repository', {}).get('issues', {}).get('pageInfo').get('endCursor')
            response = self.client.get_github_pull_requests(owner=self.config.project_owner,
                                                            name=self.config.repository_name,
                                                            after=after,
                                                            labels=self.config.filter_labels,
                                                            milestone=self.config.filter_milestone)
            pull_requests.get('edges').extend(response.get('repository', {}).get('pull_requests', {}).get('edges'))

        return self.construct_pull_request_object(pull_requests)

    def add_items_to_project(self, all_items):
        items_to_add = self.project.find_missing_item_ids(all_items)
        self.project.add_items(self.client, all_items, items_to_add, self.config)

    def manage(self):
        if self.config.remove:  # Better to first remove items that should not be in the board
            self.project.remove_items(self.client, self.config)

        if self.config.add:
            if self.matching_issues:
                self.add_items_to_project(self.matching_issues)
            if self.matching_pull_requests:
                self.add_items_to_project(self.matching_pull_requests)

        if self.config.sort:
            self.project.sort_items_in_columns(self.client, self.config)

        if self.config.move:
            if self.matching_issues:
                self.project.move_items(self.client, self.config, self.matching_issues)
            if self.matching_pull_requests:
                self.project.move_items(self.client, self.config, self.matching_pull_requests)
