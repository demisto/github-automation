from __future__ import absolute_import

from copy import deepcopy

from github_automation.core.project_item.issue import Issue, parse_issue


def test_parse_issue():
    issue_id = "=asdf=sdf="
    title = "issue name"
    labels = ["HighEffort", "Low", "bug"]
    assignee = "ronykoz"
    parsed_issue = parse_issue({
        "projectCards": {
            "nodes": [
                {
                    "id": "id=",
                    "column": {
                        "name": "testing"
                    },
                    "project": {
                        "number": 1
                    }
                },
                {
                    "id": "id2=",
                    "column": {
                        "name": "Queue"
                    },
                    "project": {
                        "number": 2
                    }
                }
            ]
        },
        "timelineItems": {
            "__typename": "IssueTimelineItemsConnection",
            "nodes": [
                {
                    "willCloseTarget": True,
                    "source": {
                        "__typename": "PullRequest",
                        "id": "42",
                        "title": "test1",
                        "state": "OPEN",
                        "isDraft": False,
                        "assignees": {
                            "nodes": [
                                {
                                    "login": "test"
                                },
                                {
                                    "login": "test2"
                                }
                            ]
                        },
                        "labels": {
                            "nodes": [
                                {
                                    "name": "label"
                                }
                            ]
                        },
                        "reviewRequests": {
                            "totalCount": 0
                        },
                        "reviews": {
                            "totalCount": 3
                        },
                        "number": 1,
                        "reviewDecision": "APPROVED"
                    }
                }
            ]
        },
        "title": title,
        "id": issue_id,
        "number": 1,
        "milestone": {
            "title": "test"
        },
        "labels": {
            "edges": [
                {
                    "node": {
                        "name": labels[0]
                    }
                },
                {
                    "node": {
                        "name": labels[1]
                    }
                },
                {
                    "node": {
                        "name": labels[2]
                    }
                }
            ]
        },
        "assignees": {
            "edges": [
                {
                    "node": {
                        "login": assignee
                    }
                }
            ]
        }
    })
    assert parsed_issue['id'] == issue_id
    assert parsed_issue['title'] == title
    assert parsed_issue['labels'] == labels
    assert parsed_issue['assignees'] == [assignee]
    assert parsed_issue['milestone'] == "test"
    assert parsed_issue['number'] == 1


def test_issue_params():
    issue_id = "=asdf=sdf="
    title = "issue name"
    labels = ["HighEffort", "Low", "bug"]
    assignee = "ronykoz"
    issue = Issue(**parse_issue({
        "projectCards": {
            "nodes": [
                {
                    "id": "id=",
                    "column": {
                        "name": "testing"
                    },
                    "project": {
                        "number": 1
                    }
                },
                {
                    "id": "id2=",
                    "column": {
                        "name": "Queue"
                    },
                    "project": {
                        "number": 2
                    }
                }
            ]
        },
        "timelineItems": {
            "__typename": "IssueTimelineItemsConnection",
            "nodes": [
                {
                    "willCloseTarget": True,
                    "source": {
                        "__typename": "PullRequest",
                        "id": "43",
                        "title": "test2",
                        "state": "OPEN",
                        "isDraft": False,
                        "assignees": {
                            "nodes": [
                                {
                                    "login": "test"
                                },
                                {
                                    "login": "test2"
                                }
                            ]
                        },
                        "labels": {
                            "nodes": [
                                {
                                    "name": "label"
                                }
                            ]
                        },
                        "reviewRequests": {
                            "totalCount": 0
                        },
                        "reviews": {
                            "totalCount": 3
                        },
                        "number": 1,
                        "reviewDecision": "APPROVED"
                    }
                }
            ]
        },
        "title": title,
        "id": issue_id,
        "number": 1,
        "milestone": {
            "title": "test"
        },
        "labels": {
            "edges": [
                {
                    "node": {
                        "name": labels[0]
                    }
                },
                {
                    "node": {
                        "name": labels[1]
                    }
                },
                {
                    "node": {
                        "name": labels[2]
                    }
                }
            ]
        },
        "assignees": {
            "edges": [
                {
                    "node": {
                        "login": assignee
                    }
                }
            ]
        }
    }))

    assert issue.id == issue_id
    assert issue.title == title
    assert issue.number == 1
    assert 'project_column' in issue.card_id_project['id=']
    assert issue.card_id_project['id=']['project_column'] == 'testing'
    assert sorted(issue.labels) == sorted(labels)
    assert issue.priority_rank == 1
    assert issue.milestone == "test"

    assert sorted(issue.get_associated_project()) == [1, 2]

    assert issue.get_card_id_from_project(1) == 'id='
    assert issue.get_card_id_from_project(2) == 'id2='
    assert issue.get_card_id_from_project(3) is None

    assert issue.pull_request.number == 1
    assert issue.pull_request.assignees == ['test', 'test2']


def test_no_priority_rank():
    issue_id = "=asdf=sdf="
    title = "issue name"
    labels = ["HighEffort", "bug"]
    assignees = ["ronykoz"]
    milestone = "test"
    number = 1

    issue = Issue(
        id=issue_id,
        number=number,
        title=title,
        labels=labels,
        assignees=assignees,
        milestone=milestone
    )

    assert issue.id == issue_id
    assert issue.title == title
    assert issue.number == 1
    assert sorted(issue.labels) == sorted(labels)
    assert issue.priority_rank == 0
    assert issue.milestone == "test"

    assert issue.pull_request is None


def test_gt():
    issue_id = "=asdf=sdf="
    title = "issue name"
    labels = ["HighEffort", "Low", "bug"]
    assignee = "ronykoz"
    milestone = "test"

    issue = Issue(
        id=issue_id,
        number=1,
        title=title,
        labels=labels,
        assignees=[assignee],
        milestone=milestone
    )

    issue_id2 = "test"
    title2 = "issue name 2"
    labels2 = ["HighEffort", "bug"]

    issue2 = Issue(
        id=issue_id2,
        number=2,
        title=title2,
        labels=labels2,
    )

    issue3 = Issue(
        id=issue_id2,
        number=3,
        title=title2,
        labels=labels2,
    )

    assert issue2 < issue
    assert issue > issue2
    assert issue2 > issue3
    assert issue3 < issue2 < issue
    assert issue3 < issue


def test_add_details():
    issue_id = "=asdf=sdf="
    title = "issue name"
    labels = ["HighEffort", "Low", "bug"]
    assignee = "ronykoz"
    milestone = "test"

    issue = Issue(
        id=issue_id,
        number=1,
        title=title,
        labels=labels,
        assignees=[assignee],
        milestone=milestone
    )

    issue.add_assignee("another one")
    assert sorted(issue.assignees) == sorted([assignee, "another one"])

    labels_new = deepcopy(labels)
    issue.add_label("label")
    labels_new.append("label")
    assert sorted(issue.labels) == sorted(labels_new)
