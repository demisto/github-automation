def _extract_assignees(assignee_nodes):
    assignees = []
    for assignee in assignee_nodes:
        if assignee:
            assignees.append(assignee['login'])

    return assignees


def _get_labels(label_nodes):
    labels = []
    for label in label_nodes:
        if label:
            labels.append(label['name'])

    return labels


def _is_review_requested(pull_request_source):
    if pull_request_source['reviewRequests']['totalCount'] or pull_request_source['reviews']['totalCount']:
        return True

    else:
        return False


def _is_review_completed(pull_request_node):
    return False if pull_request_node['source']['reviewDecision'] != 'APPROVED' else True


def parse_pull_request(pull_request_node):
    return {
        "number": pull_request_node['source']['number'],
        "assignees": _extract_assignees(pull_request_node['source']['assignees']['nodes']),
        "labels": _get_labels(pull_request_node['source']['labels']['nodes']),
        "review_requested": _is_review_requested(pull_request_node['source']),
        "review_completed": _is_review_completed(pull_request_node)
    }


class PullRequest(object):
    def __init__(self, number: int, review_requested: bool = False, review_completed: bool = False,
                 assignees: list = None, labels: list = None):
        self.number = number
        self.assignees = assignees if assignees else []
        self.labels = labels if labels else []
        self.review_requested = review_requested
        self.review_completed = review_completed
