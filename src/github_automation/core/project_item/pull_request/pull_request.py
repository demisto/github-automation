from github_automation.common.utils import get_labels
from github_automation.core.project_item.base_project_item.base_project_item import BaseProjectItem, extract_assignees, \
    get_milestone, extract_project_cards


def _is_review_requested(pull_request_source):
    if pull_request_source.get('reviewRequests', {}).get('totalCount') or pull_request_source.get('reviews', {}).get('totalCount'):
        return True

    else:
        return False


def _is_review_completed(pull_request_node):
    return False if pull_request_node['reviewDecision'] != 'APPROVED' else True


def parse_pull_request(pull_request_node):
    return {
        "id": pull_request_node['id'],
        "title": pull_request_node['title'],
        "number": pull_request_node['number'],
        "assignees": extract_assignees(pull_request_node.get('assignees', {}).get('edges', [])),
        "labels": get_labels(pull_request_node.get('labels', {}).get('edges', [])),
        "milestone": get_milestone(pull_request_node),
        "card_id_to_project": extract_project_cards(pull_request_node.get('projectCards', {})),
        "state": pull_request_node.get('state', ''),
        "review_requested": _is_review_requested(pull_request_node),
        "review_completed": _is_review_completed(pull_request_node)
    }


class PullRequest(BaseProjectItem):
    def __init__(self, id: str, title: str, number: int, assignees: list = None, labels: list = None,
                 milestone: str = '', card_id_to_project: dict = None, priority_list: list = None, state: str = '',
                 review_requested: bool = False, review_completed: bool = False):
        super().__init__(id, title, number, assignees, labels, milestone, card_id_to_project, priority_list, state)
        self.review_requested = review_requested
        self.review_completed = review_completed
