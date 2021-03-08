from __future__ import absolute_import

from github_automation.core.project_item.pull_request import (PullRequest, parse_pull_request_for_issue)


def test_parse_pull_request():
    assignee = "ronykoz"

    pull_request = PullRequest(**parse_pull_request_for_issue({
        "willCloseTarget": True,
        "source": {
            "__typename": "PullRequest",
            "id": 245,
            "title": "test",
            "state": "OPEN",
            "assignees": {
                "nodes": [
                    {
                        "login": assignee
                    }
                ],
            },
            "labels": {
                "nodes": [
                    {
                        "name": "label"
                    }
                ],
            },
            "reviewRequests": {
                "totalCount": 0
            },
            "reviews": {
                "totalCount": 1
            },
            "number": 1,
            "reviewDecision": "REVIEW_REQUIRED"
        },
        "__typename": "CrossReferencedEvent"
    }))

    assert pull_request.number == 1
    assert pull_request.assignees == [assignee]
    assert pull_request.review_requested is True
    assert pull_request.review_completed is False
    assert "label" in pull_request.labels


def test_parse_pull_request_no_review():
    assignee = "ronykoz"

    pull_request = PullRequest(**parse_pull_request_for_issue({
        "willCloseTarget": True,
        "source": {
            "__typename": "PullRequest",
            "id": "42",
            "title": "test",
            "state": "OPEN",
            "assignees": {
                "nodes": [
                    {
                        "login": assignee
                    }
                ],
            },
            "labels": {
                "nodes": [
                    {
                        "name": "label"
                    }
                ],
            },
            "reviewRequests": {
                "totalCount": 0
            },
            "reviews": {
                "totalCount": 0
            },
            "number": 1,
            "reviewDecision": "REVIEW_REQUIRED"
        },
        "__typename": "CrossReferencedEvent"
    }))

    assert pull_request.number == 1
    assert pull_request.assignees == [assignee]
    assert pull_request.review_requested is False
    assert pull_request.review_completed is False
    assert "label" in pull_request.labels


def test_not_requested_review():
    assignee = "ronykoz"
    pull_request = PullRequest(
        number=1,
        assignees=[assignee],
        review_requested=False,
        review_completed=True,
        id="42",
        title="No title"
    )

    assert pull_request.number == 1
    assert pull_request.assignees == [assignee]
    assert pull_request.review_requested is False
    assert pull_request.review_completed is True
