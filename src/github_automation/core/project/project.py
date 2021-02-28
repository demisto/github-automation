from __future__ import absolute_import

from copy import deepcopy
from typing import Dict, List, Union

from github_automation.common.constants import OR
from github_automation.common.utils import is_matching_project_item
from github_automation.core.project_item.issue import Issue, parse_issue
from github_automation.core.project_item.pull_request import PullRequest, parse_pull_request
from github_automation.management.configuration import Configuration
from github_automation.management.github_client import GraphQLClient


def parse_issue_card(card_edge: dict, config: Configuration):
    return {
        "id": card_edge.get('node', {}).get('id'),
        "cursor": card_edge['cursor'],
        "item": Issue(**parse_issue(card_edge.get('node', {}).get('content')),
                      priority_list=config.priority_list)
    }


def parse_pull_request_card(card_edge: dict, config: Configuration):
    return {
        "id": card_edge.get('node', {}).get('id'),
        "cursor": card_edge['cursor'],
        "item": PullRequest(**parse_pull_request(card_edge.get('node', {}).get('content')),
                            priority_list=config.priority_list)
    }


def parse_item_card(card_edge: dict, config: Configuration):
    # __typename PullRequest is expected for PullRequest and Issue for Issue
    typename = card_edge.get('node', {}).get('content', {}).get('__typename')
    if typename == 'PullRequest':
        return parse_pull_request_card(card_edge, config)
    elif typename == 'Issue':
        return parse_issue_card(card_edge, config)
    else:
        print("This is not an issue or a pull request, and we still do not support other github "
              "entities in the project.")


class ItemCard(object):
    def __init__(self, id: str, item: Union[Issue, PullRequest] = None, cursor: str = ''):

        self.id = id
        self.cursor = cursor
        self.item = item
        self.item_id = self.item.id if self.item else ""
        self.item_title = self.item.title if self.item else ""


def _extract_card_node_data(column_node: dict, config: Configuration):
    cards = []
    for card in column_node['cards']['edges']:
        card_content = card.get('node', {}).get('content')
        if not card_content:
            continue
        cards.append(ItemCard(**parse_item_card(card, config)))

    return cards


def parse_project_column(column_node: dict, config: Configuration):
    return {
        "id": column_node['id'],
        "name": column_node['name'],
        "cards": _extract_card_node_data(column_node, config),
        "config": config
    }


class ProjectColumn(object):
    def __init__(self, id: str, name: str, cards: List[ItemCard], config: Configuration = None):
        self.id = id
        self.name = name
        self.cards = cards
        self.config = config

    def get_all_item_ids(self):
        return {card.item_id for card in self.cards}

    def add_card(self, card_id: str, new_item: Union[Issue, PullRequest], client: GraphQLClient):
        insert_after_position = len(self.cards) - 1  # In case it should be the lowest issue
        if not self.cards or new_item > self.cards[0].item:
            self.cards.insert(0, ItemCard(id=card_id, item=new_item))
            try:
                client.add_to_column(card_id=card_id,
                                     column_id=self.id)
            except Exception as ex:
                exception_msg = str(ex)
                if 'The card must not be archived' in exception_msg:
                    try:
                        self.config.logger.info(f"Un-archiving the card of {new_item.title}")
                        client.un_archive_card(card_id)
                        client.add_to_column(card_id=card_id,
                                             column_id=self.id)
                        return
                    except Exception as ex:
                        exception_msg += '\n' + str(ex)

                self.config.logger.warning(f'The {str(new_item)} {new_item.title} was not added due to {exception_msg}')

            return

        for i in range(len(self.cards) - 1):
            if self.cards[i].item > new_item > self.cards[i + 1].item:
                insert_after_position = i
                break

        self.cards.insert(insert_after_position + 1,
                          ItemCard(id=card_id, item=new_item))
        try:
            client.move_to_specific_place_in_column(card_id=card_id,
                                                    column_id=self.id,
                                                    after_card_id=self.cards[insert_after_position].id)
        except Exception as ex:
            exception_msg = str(ex)
            if 'The card must not be archived' in exception_msg:
                try:
                    self.config.logger.info(f"Un-archiving the card of {new_item.title}")
                    client.un_archive_card(card_id)
                    client.move_to_specific_place_in_column(card_id=card_id,
                                                            column_id=self.id,
                                                            after_card_id=self.cards[insert_after_position].id)
                    return
                except Exception as ex:
                    exception_msg += '\n' + str(ex)

            self.config.logger.warning(f'The {str(new_item)} {new_item.title} was not added due to {exception_msg}')

    def get_card_id(self, item_id):
        for card in self.cards:
            if card.item_id == item_id:
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
        sorted_cards = deepcopy(sorted(self.cards, key=lambda card: card.item, reverse=True))
        for index, card in enumerate(sorted_cards):
            if card.id != self.cards[index].id:
                self.move_card_in_list(card.id, index)
                config.logger.info(f"Moving {str(card.item)} '{card.item_title}' in column "
                                   f"'{self.name}' to position: {index}")
                if index == 0:
                    try:
                        client.add_to_column(card_id=card.id,
                                             column_id=self.id)
                    except Exception as ex:
                        config.logger.warning(f'The item {card.item_title} was not moved due to {str(ex)}')
                else:
                    try:
                        client.move_to_specific_place_in_column(card_id=card.id,
                                                                column_id=self.id,
                                                                after_card_id=sorted_cards[index-1].id)
                    except Exception as ex:
                        config.logger.warning(f'The item {card.item_title} was not moved due to {str(ex)}')

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
    def get_matching_column(item, config: Configuration):
        is_issue = isinstance(item, Issue)  # assumes if not issue -> pull_request
        column_name = ''
        for tested_column_name in config.column_rule_desc_order:
            conditions = config.column_to_rules[tested_column_name]

            # filter and rename conditions to match current item type
            relevant_conditions = {}
            for condition, condition_value in conditions.items():
                if is_issue and condition.startswith('issue.'):
                    relevant_conditions[condition.replace('issue', 'item', 1)] = condition_value
                elif not is_issue and condition.startswith('pull_request.'):
                    relevant_conditions[condition.replace('pull_request', 'item', 1)] = condition_value

            # if no relevant conditions - not true
            is_true = len(relevant_conditions) > 0

            if is_true:
                for condition, condition_value in relevant_conditions.items():
                    try:
                        # TODO: consider replacing this with a solution that doesn't use eval()
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

            config.logger.debug(f'{item.title} did not match the filters of the column - \'{tested_column_name}\'')

        return column_name

    def get_all_item_ids(self):
        all_items = set()
        for column in self.columns.values():
            all_items = all_items.union(column.get_all_item_ids())

        return all_items

    def find_missing_item_ids(self, items):
        items_in_project_keys = set(self.get_all_item_ids())
        all_matching_items = set()
        for item in items.values():
            if not any(self.number == value.get('project_number') for value in item.card_id_project.values()):
                all_matching_items.add(item.id)

        return all_matching_items - items_in_project_keys

    def add_items(self, client, items, items_to_add, config: Configuration):
        for item_id in items_to_add:
            column_name = self.get_matching_column(items[item_id], config)
            self.add_item(client, items[item_id], column_name, config)

    def add_item(self, client, item, column_name, config):
        item_type = str(item)
        if column_name not in config.column_names:
            config.logger.warning(f"Did not found a matching column for your {item_type}, "
                                  f"please check your configuration file. The {item_type} was {item.title}")
            return

        column_id = self.columns[column_name].id if column_name else ''
        config.logger.info(f"Adding {item_type} '{item.title}' to column '{column_name}'")
        if config.project_number not in item.get_associated_project():
            try:
                response = client.add_items_to_project(item.id, column_id)
                card_id = response['addProjectCard']['cardEdge']['node']['id']
            except Exception as ex:
                config.logger.warning(f'The {item_type} {item.title} was not added due to {str(ex)}')
                return
        else:
            card_id = item.get_card_id_from_project(config.project_number)

        self.columns[column_name].add_card(card_id=card_id,
                                           new_item=item,
                                           client=client)

    def is_in_column(self, column_name, item_id):
        if item_id in self.columns[column_name].get_all_item_ids():
            return True

        return False

    def get_current_location(self, item_id):
        for column_name, column in self.columns.items():
            card_id = column.get_card_id(item_id)
            if card_id:
                return column_name, card_id

        return None, None

    def move_items(self, client, config: Configuration, all_items):
        # todo: add explanation that we are relying on the github automation to move closed issues to the Done queue
        for item in all_items.values():
            column_name_before, card_id = self.get_current_location(item.id)
            column_name_after = self.get_matching_column(item, config)
            column_id = self.columns[column_name_after].id if column_name_after else ''
            if not column_id or column_name_before == column_name_after or item.state == 'closed':
                continue

            self.move_item(client, item, column_name_after, config)
            self.columns[column_name_before].remove_card(card_id)

    def move_item(self, client, item, column_name, config: Configuration):
        item_type = str(item)
        if item.state == 'closed':
            config.logger.debug(f'skipping {item.title} because the {item_type} is closed')
            return

        card_id = [_id for _id, value in item.card_id_project.items()
                   if value['project_number'] == config.project_number][0]

        config.logger.info(f"Moving card {item.title} to '{column_name}'")
        self.columns[column_name].add_card(card_id=card_id,
                                           new_item=item,
                                           client=client)

    def remove_items(self, client, config: Configuration):
        for column in self.columns.values():
            if column.name in config.get_closed_columns():  # skip closed columns
                continue

            indexes_to_delete = []
            for index, card in enumerate(column.cards):
                if not is_matching_project_item(card.item.labels, config.must_have_labels,
                                                config.cant_have_labels, config.filter_labels):
                    indexes_to_delete.append(index)
                    self.remove_item(client, card.item_title, card.id, config, card.item)

            for index_to_delete in sorted(indexes_to_delete, reverse=True):  # Removing from bottom to top
                del column.cards[index_to_delete]

    @staticmethod
    def remove_item(client, issue_title, card_id, config, item=None):
        item_type = 'issue' if item is None else (str(item))
        config.logger.info(f'Removing {item_type} {issue_title} from project')
        try:
            client.delete_project_card(card_id)
        except Exception as ex:
            config.logger.warning(f'The {item_type} {issue_title} was not removed due to {str(ex)}')

    def sort_items_in_columns(self, client, config):
        for column_name, column in self.columns.items():
            if column.name in config.get_closed_columns():  # Not going over closed columns
                continue

            column.sort_cards(client, config)
