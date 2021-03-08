from github_automation.common.utils import get_labels
from github_automation.core.project_item.base_project_item import (
    BaseProjectItem,
    extract_assignees,
    extract_project_cards,
    is_review_requested,
    is_review_completed, is_review_requested_changes,
)


def _extract_assignees_from_nodes(assignee_nodes):
    assignees = []
    for assignee in assignee_nodes:
        if assignee:
            assignees.append(assignee['login'])

    return assignees


def _get_labels_from_nodes(label_nodes):
    labels = []
    for label in label_nodes:
        if label:
            labels.append(label['name'])

    return labels


def parse_pull_request_for_issue(pull_request_node):
    return {
        "id": pull_request_node['source']['id'],
        "title": pull_request_node['source']['title'],
        "number": pull_request_node['source']['number'],
        "assignees": _extract_assignees_from_nodes(pull_request_node['source']['assignees']['nodes']),
        "labels": _get_labels_from_nodes(pull_request_node['source']['labels']['nodes']),
        "review_requested": is_review_requested(pull_request_node['source']),
        "review_completed": is_review_completed(pull_request_node['source']),
        "review_requested_changes": is_review_requested_changes(pull_request_node['source']),
        "state": pull_request_node['source'].get('state', "")
    }


def parse_pull_request(pull_request_node):
    return {
        "id": pull_request_node["id"],
        "title": pull_request_node["title"],
        "number": pull_request_node["number"],
        "assignees": extract_assignees(
            pull_request_node.get("assignees", {}).get("edges", [])
        ),
        "labels": get_labels(pull_request_node.get("labels", {}).get("edges", [])),
        "card_id_to_project": extract_project_cards(
            pull_request_node.get("projectCards", {})
        ),
        "state": pull_request_node.get("state", ""),
        "review_requested": is_review_requested(pull_request_node),
        "review_completed": is_review_completed(pull_request_node),
        "review_requested_changes": is_review_requested_changes(pull_request_node),
    }


class PullRequest(BaseProjectItem):
    def __init__(
        self,
        id: str,
        title: str,
        number: int,
        assignees: list = None,
        labels: list = None,
        card_id_to_project: dict = None,
        priority_list: list = None,
        state: str = "",
        review_requested: bool = False,
        review_completed: bool = False,
        review_requested_changes: bool = False,
    ):
        super().__init__(
            id,
            title,
            number,
            assignees,
            labels,
            card_id_to_project,
            priority_list,
            state,
        )
        self.review_requested = review_requested
        self.review_completed = review_completed
        self.review_requested_changes = review_requested_changes

    def __str__(self):
        return f'pull request #{self.number}'
