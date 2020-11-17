from __future__ import absolute_import

from copy import deepcopy
from typing import Dict, List

from github_automation.common.constants import OR
from github_automation.common.utils import is_matching_issue
from github_automation.core.issue.issue import Issue, parse_issue
from github_automation.management.configuration import Configuration


def parse_issue_card(card_edge: dict, config: Configuration):
    return {
        "id": card_edge.get('node', {}).get('id'),
        "cursor": card_edge['cursor'],
        "issue": Issue(**parse_issue(card_edge.get('node', {}).get('content')),
                       priority_list=config.priority_list)
    }


class IssueCard(object):
    def __init__(self, id: str, issue: Issue = None, cursor: str = ''):
        self.id = id
        self.cursor = cursor
        self.issue = issue

        self.issue_id = self.issue.id  # todo remove this
        self.issue_title = self.issue.title  # todo remove this


def _extract_card_node_data(column_node: dict, config: Configuration):
    cards = []
    for card in column_node['cards']['edges']:
        card_content = card.get('node', {}).get('content')
        if not card_content:
            continue

        cards.append(IssueCard(**parse_issue_card(card, config)))

    return cards


def parse_project_column(column_node: dict, config: Configuration):
    return {
        "id": column_node['id'],
        "name": column_node['name'],
        "cards": _extract_card_node_data(column_node, config),
        "config": config
    }


class ProjectColumn(object):
    def __init__(self, id: str, name: str, cards: List[IssueCard], config: Configuration = None):
        self.id = id
        self.name = name
        self.cards = cards
        self.config = config

    def get_all_issue_ids(self):
        return {card.issue.id for card in self.cards}

    def get_issues(self):
        return [card.issue for card in self.cards]

    def add_card(self, card_id, new_issue, client):
        insert_after_position = len(self.cards) - 1  # In case it should be the lowest issue
        if not self.cards or new_issue > self.cards[0].issue:
            self.cards.insert(0, IssueCard(id=card_id, issue=new_issue))
            try:
                client.add_to_column(card_id=card_id,
                                     column_id=self.id)
            except Exception as ex:
                exception_msg = str(ex)
                if 'The card must not be archived' in exception_msg:
                    try:
                        self.config.logger.info(f"Un-archiving the card of {new_issue.title}")
                        client.un_archive_card(card_id)
                        client.add_to_column(card_id=card_id,
                                             column_id=self.id)
                        return
                    except Exception as ex:
                        exception_msg += '\n' + str(ex)

                self.config.logger.warning(f'The issue {new_issue.title} was not added due to {exception_msg}')

            return

        for i in range(len(self.cards) - 1):
            if self.cards[i].issue > new_issue > self.cards[i + 1].issue:
                insert_after_position = i
                break

        self.cards.insert(insert_after_position + 1,
                          IssueCard(id=card_id, issue=new_issue))
        try:
            client.move_to_specific_place_in_column(card_id=card_id,
                                                    column_id=self.id,
                                                    after_card_id=self.cards[insert_after_position].id)
        except Exception as ex:
            exception_msg = str(ex)
            if 'The card must not be archived' in exception_msg:
                try:
                    self.config.logger.info(f"Un-archiving the card of {new_issue.title}")
                    client.un_archive_card(card_id)
                    client.move_to_specific_place_in_column(card_id=card_id,
                                                            column_id=self.id,
                                                            after_card_id=self.cards[insert_after_position].id)
                    return
                except Exception as ex:
                    exception_msg += '\n' + str(ex)

            self.config.logger.warning(f'The issue {new_issue.title} was not added due to {exception_msg}')

    def get_card_id(self, issue_id):
        for card in self.cards:
            if card.issue_id == issue_id:
                return card.id

    def remove_card(self, card_id):
        for index, card in enumerate(self.cards):
            if card_id == card.id:
                del self.cards[index]
                break

    def move_card_in_list(self, card_id, new_index):
        old_index = -1
        old_card = None
        for index, card in enumerate(self.cards):
            if card.id == card_id and index != new_index:
                old_card = deepcopy(card)
                old_index = index
                break

        del self.cards[old_index]
        self.cards.insert(new_index, deepcopy(old_card))

    def sort_cards(self, client, config):
        sorted_cards = deepcopy(sorted(self.cards, key=lambda card: card.issue, reverse=True))
        for index, card in enumerate(sorted_cards):
            if card.id != self.cards[index].id:
                self.move_card_in_list(card.id, index)
                config.logger.info(f"Moving issue '{card.issue_title}' in column '{self.name}' to position: {index}")
                if index == 0:
                    try:
                        client.add_to_column(card_id=card.id,
                                             column_id=self.id)
                    except Exception as ex:
                        config.logger.warning(f'The issue {card.issue_title} was not moved due to {str(ex)}')
                else:
                    try:
                        client.move_to_specific_place_in_column(card_id=card.id,
                                                                column_id=self.id,
                                                                after_card_id=sorted_cards[index-1].id)
                    except Exception as ex:
                        config.logger.warning(f'The issue {card.issue_title} was not moved due to {str(ex)}')

        self.cards = sorted_cards


def _extract_columns(git_hub_column_nodes, config):
    columns = {}
    for column_node in git_hub_column_nodes:
        column = ProjectColumn(**parse_project_column(column_node, config))

        columns[column.name] = column

    return columns


def parse_project(git_hub_project, config):
    return {
        "columns": _extract_columns(git_hub_project['columns']['nodes'], config),
        "name": git_hub_project.get("name", 'Not Found'),
        "number": git_hub_project.get("number", -1),
        "config": config
    }


class Project(object):
    def __init__(self, name: str, columns: Dict[str, ProjectColumn], config: Configuration, number: int = None):
        self.name = name
        self.columns = columns
        self.number = number

        self.config = config

    @staticmethod
    def get_matching_column(issue, config: Configuration):
        column_name = ''
        for tested_column_name in config.column_rule_desc_order:
            conditions = config.column_to_rules[tested_column_name]
            is_true = True
            for condition, condition_value in conditions.items():
                try:
                    condition_results = eval(condition)
                except AttributeError:
                    is_true = False
                    break

                if isinstance(condition_value, list):  # todo: add the option to have not condition
                    for option in condition_value:
                        if OR in option:
                            options = option.split(OR)
                            if not any([True if option in condition_results else False for option in options]):
                                is_true = False
                                break

                        elif option not in condition_results:
                            is_true = False
                            break

                elif isinstance(condition_value, bool):
                    if condition_value is not bool(condition_results):
                        is_true = False
                        break

                elif condition_value != condition_results or condition_value not in condition_results:
                    is_true = False
                    break

            if is_true:
                column_name = tested_column_name
                break

            config.logger.debug(f'{issue.title} did not match the filters of the column - \'{tested_column_name}\'')

        return column_name

    def get_all_issue_ids(self):
        all_issues = set()
        for column in self.columns.values():
            all_issues = all_issues.union(column.get_all_issue_ids())

        return all_issues

    def find_missing_issue_ids(self, issues):
        issues_in_project_keys = set(self.get_all_issue_ids())
        all_matching_issues = set()
        for issue in issues.values():
            if not any(self.number == value.get('project_number') for value in issue.card_id_project.values()):
                all_matching_issues.add(issue.id)

        return all_matching_issues - issues_in_project_keys

    def add_issues(self, client, issues, issues_to_add, config: Configuration):
        for issue_id in issues_to_add:
            column_name = self.get_matching_column(issues[issue_id], config)
            self.add_issue(client, issues[issue_id], column_name, config)

    def add_issue(self, client, issue, column_name, config):
        if column_name not in config.column_names:
            config.logger.warning(f"Did not found a matching column for your issue, please check your configuration "
                                  f"file. The issue was {issue.title}")
            return

        column_id = self.columns[column_name].id if column_name else ''
        config.logger.info("Adding issue '{}' to column '{}'".format(issue.title, column_name))
        if config.project_number not in issue.get_associated_project():
            try:
                response = client.add_issues_to_project(issue.id, column_id)
                card_id = response['addProjectCard']['cardEdge']['node']['id']
            except Exception as ex:
                config.logger.warning(f'The issue {issue.title} was not added due to {str(ex)}')
                return
        else:
            card_id = issue.get_card_id_from_project(config.project_number)

        self.columns[column_name].add_card(card_id=card_id,
                                           new_issue=issue,
                                           client=client)

    def is_in_column(self, column_name, issue_id):
        if issue_id in self.columns[column_name].get_all_issue_ids():
            return True

        return False

    def get_current_location(self, issue_id):
        for column_name, column in self.columns.items():
            card_id = column.get_card_id(issue_id)
            if card_id:
                return column_name, card_id

        return None, None

    def move_issues(self, client, config: Configuration, all_issues):
        # todo: add explanation that we are relying on the github automation to move closed issues to the Done queue
        for issue in all_issues.values():
            column_name_before, card_id = self.get_current_location(issue.id)
            column_name_after = self.get_matching_column(issue, config)
            column_id = self.columns[column_name_after].id if column_name_after else ''
            if not column_id or column_name_before == column_name_after or issue.state == 'closed':
                continue

            self.move_issue(client, issue, column_name_after, config)
            self.columns[column_name_before].remove_card(card_id)

    def move_issue(self, client, issue, column_name, config: Configuration):
        if issue.state == 'closed':
            config.logger.debug(f'skipping {issue.title} because the issue is closed')
            return

        card_id = [_id for _id, value in issue.card_id_project.items()
                   if value['project_number'] == config.project_number][0]

        config.logger.info(f"Moving card {issue.title} to '{column_name}'")
        self.columns[column_name].add_card(card_id=card_id,
                                           new_issue=issue,
                                           client=client)

    def remove_issues(self, client, config: Configuration):
        for column in self.columns.values():
            if column.name == config.closed_issues_column:  # Not going over closed issues
                continue

            indexes_to_delete = []
            for index, card in enumerate(column.cards):
                if not is_matching_issue(card.issue.labels, config.must_have_labels,
                                         config.cant_have_labels, config.filter_labels):
                    indexes_to_delete.append(index)
                    self.remove_issue(client, card.issue_title, card.id, config)

            for index_to_delete in sorted(indexes_to_delete, reverse=True):  # Removing from bottom to top
                del column.cards[index_to_delete]

    @staticmethod
    def remove_issue(client, issue_title, card_id, config):
        config.logger.info(f'Removing issue {issue_title} from project')
        try:
            client.delete_project_card(card_id)
        except Exception as ex:
            config.logger.warning(f'The issue {issue_title} was not removed due to {str(ex)}')

    def sort_issues_in_columns(self, client, config):
        for column_name, column in self.columns.items():
            if column.name == config.closed_issues_column:  # Not going over closed issues
                continue

            column.sort_cards(client, config)
