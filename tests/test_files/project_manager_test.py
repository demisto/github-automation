import os

from github_automation.management.configuration import Configuration
from github_automation.management.project_manager import ProjectManager

MOCK_FOLDER_PATH = os.path.join(os.getcwd(), "tests", "mock_data")


def test_loading_repo_project():
    project_layout = {
        "repository": {
            "project": {
                "columns": {
                    "edges": [
                        {
                            "cursor": 1,
                            "node": {
                                "name": "Queue"
                            }
                        },
                        {
                            "cursor": 2,
                            "node": {
                                "name": "Review in progress"
                            }
                        }
                    ]
                }
            }
        }
    }

    column1 = {
        "repository": {
            "project": {
                "name": "test",
                "columns": {
                    "nodes": [
                        {
                            "name": "Queue",
                            "id": "1234",
                            "cards": {
                                "pageInfo": {
                                    "hasNextPage": False,
                                    "endCursor": "MQ"
                                },
                                "edges": [
                                    {
                                        "cursor": "MQ",
                                        "node": {
                                            "note": None,
                                            "state": "CONTENT_ONLY",
                                            "id": "3434=",
                                            "content": {
                                                "__typename": "Issue",
                                                "id": "1234=",
                                                "number": 1,
                                                "title": "issue 1",
                                                "labels": {
                                                    "edges": [
                                                        {
                                                            "node": {
                                                                "name": "High"
                                                            }
                                                        },
                                                        {
                                                            "node": {
                                                                "name": "bug"
                                                            }
                                                        }
                                                    ]
                                                },
                                                "assignees": {
                                                    "edges": []
                                                }
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
    }
    column2 = {
        "repository": {
            "project":
                {
                    "name": "test",
                    "columns": {
                        "nodes": [
                            {
                                "name": "In progress",
                                "id": "5656",
                                "cards": {
                                    "pageInfo": {
                                        "hasNextPage": False,
                                        "endCursor": "MQ"
                                    },
                                    "edges": [
                                        {
                                            "cursor": "MQ",
                                            "node": {
                                                "note": None,
                                                "state": "CONTENT_ONLY",
                                                "id": "56565=",
                                                "content": {
                                                    "__typename": "Issue",
                                                    "id": "56567=",
                                                    "number": 15,
                                                    "title": "issue 2",
                                                    "labels": {
                                                        "edges": [
                                                            {
                                                                "node": {
                                                                    "name": "Medium"
                                                                }
                                                            },
                                                            {
                                                                "node": {
                                                                    "name": "bug"
                                                                }
                                                            }
                                                        ]
                                                    },
                                                    "assignees": {
                                                        "edges": [
                                                            {
                                                                "node": {
                                                                    "id": "234",
                                                                    "login": "Rony Rony"
                                                                }
                                                            }
                                                        ]
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            "cursor": "MB",
                                            "node": {
                                                "note": None,
                                                "state": "CONTENT_ONLY",
                                                "id": "123=",
                                                "content": {
                                                    "__typename": "Issue",
                                                    "id": "1234=",
                                                    "number": 3,
                                                    "title": "issue 3",
                                                    "labels": {
                                                        "edges": [
                                                            {
                                                                "node": {
                                                                    "name": "High"
                                                                }
                                                            },
                                                            {
                                                                "node": {
                                                                    "name": "bug"
                                                                }
                                                            }
                                                        ]
                                                    },
                                                    "assignees": {
                                                        "edges": [
                                                            {
                                                                "node": {
                                                                    "id": "234",
                                                                    "login": "Rony Rony"
                                                                }
                                                            }
                                                        ]
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            "cursor": "HZ",
                                            "node": {
                                                "note": None,
                                                "state": "CONTENT_ONLY",
                                                "id": "76565=",
                                                "content": {
                                                    "__typename": "PullRequest",
                                                    "title": "pull_request 1",
                                                    "id": "76566=",
                                                    "state": "OPEN",
                                                    "number": 20,
                                                    "mergedAt": None,
                                                    "merged": False,
                                                    "reviewDecision": None,
                                                    "reviews": {
                                                        "totalCount": 0
                                                    },
                                                    "reviewRequests": {
                                                        "totalCount": 0
                                                    },
                                                    "labels": {
                                                        "edges": [
                                                            {
                                                                "node": {
                                                                    "name": "Medium"
                                                                }
                                                            },
                                                            {
                                                                "node": {
                                                                    "name": "bug"
                                                                }
                                                            }
                                                        ]
                                                    },
                                                    "assignees": {
                                                        "edges": [
                                                            {
                                                                "node": {
                                                                    "id": "334",
                                                                    "login": "Daud Daud"
                                                                }
                                                            }
                                                        ]
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
        }
    }

    pr_id = "=zxcx=sads="
    pr_title = "pr name"
    labels = ["HighEffort", "Critical", "bug", "test", "Testing"]
    assignee = "daud"

    pull_request = {
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
        "title": pr_title,
        "id": pr_id,
        "number": 1,
        "state": "MERGED",
        "mergedAt": "2021-01-25T15:27:08Z",
        "merged": True,
        "reviewDecision": None,
        "reviews": {
            "totalCount": 0
        },
        "reviewRequests": {
            "totalCount": 1
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
                },
                {
                    "node": {
                        "name": labels[3]
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
    }

    issue_id = "=asdf=sdf="
    issue_title = "issue name"
    issue = {
        "projectCards": {
            "nodes": [
                {
                    "id": "id=",
                    "column": {
                        "name": "Queue"
                    },
                    "project": {
                        "number": 1
                    }
                },
                {
                    "id": "id2=",
                    "column": {
                        "name": "In progress"
                    },
                    "project": {
                        "number": 2
                    }
                }
            ]
        },
        "comments": {
            "nodes": [
                {
                    "author": {
                        "login": "ronykoz"
                    },
                    "body": "comment 1",
                    "createdAt": "2019-03-19T12:24:27Z"
                },
                {
                    "author": {
                        "login": "ronykoz"
                    },
                    "body": "second comment",
                    "createdAt": "2019-03-19T12:27:53Z"
                },
                {
                    "author": {
                        "login": "ronykoz"
                    },
                    "body": "third comment",
                    "createdAt": "2019-03-19T12:52:08Z"
                }
            ]
        },
        "timelineItems": {
            "__typename": "IssueTimelineItemsConnection",
            "nodes": [
                {
                    "__typename": "LabeledEvent",
                    "label": {
                        "name": labels[0]
                    },
                    "createdAt": "2019-03-15T12:40:22Z"
                },
                {
                    "__typename": "LabeledEvent",
                    "label": {
                        "name": labels[1]
                    },
                    "createdAt": "2019-03-17T13:59:27Z"
                },
                {
                    "__typename": "LabeledEvent",
                    "label": {
                        "name": labels[2]
                    },
                    "createdAt": "2019-04-08T10:48:02Z"
                }
            ]
        },
        "title": issue_title,
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
                },
                {
                    "node": {
                        "name": labels[3]
                    }
                },
                {
                    "node": {
                        "name": labels[4]
                    }
                }
            ]
        },
        "assignees": {
            "edges": [
                {
                    "node": {
                        "login": "ronykoz"
                    }
                }
            ]
        }
    }

    items = {
        "repository": {
            "issues": {
                "pageInfo": {
                    "hasNextPage": True,
                    "endCursor": "cursor"
                },
                "edges": [
                    {
                        "node": issue
                    }
                ]
            }
        }
    }
    issues_with_no_after = {
        "repository": {
            "issues": {
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": "cursor"
                },
                "edges": [
                    {
                        "node": issue
                    }
                ]
            }
        }
    }

    config = Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'))
    config.load_properties()
    config.sort = True

    class MockClient(object):
        def delete_project_card(*args, **kwargs):
            return

        def add_issues_to_project(self, **kwargs):
            return {
                "addProjectCard": {
                    "cardEdge": {
                        "node": {
                            "id": "id="
                        }
                    }
                }
            }

        def get_project_layout(self, **kwargs):
            return project_layout

        def get_first_column_items(self, **kwargs):
            return column1

        def get_column_items(self, **kwargs):
            return column2

        def get_github_issues(self, **kwargs):
            if not kwargs['after']:
                return items

            return issues_with_no_after

        def add_to_column(self, **kwargs):
            return

        def move_to_specific_place_in_column(self, **kwargs):
            return

        def get_github_pull_requests(self, **kwargs):
            return {
              "repository": {
                "pullRequests": {
                  "pageInfo": {
                    "endCursor": "cursor",
                    "hasNextPage": False
                  },
                  "edges": [
                    {
                      "node": pull_request,
                    }
                    ]
                }
              }
            }

    client = MockClient()
    manager = ProjectManager(configuration=config, client=client)

    assert len(manager.matching_issues) == 1
    assert len(manager.matching_pull_requests) == 1
    assert manager.project.name == 'test'
    assert manager.project.get_current_location("56567=") == ("In progress", "56565=")
    assert manager.project.get_current_location("Random text") == (None, None)
    assert manager.project.is_in_column("In progress", "56567=") is True
    assert manager.project.is_in_column("In progress", "Random text") is False

    # assert there're 3 items 'In Progress' column
    manager.project.sort_items_in_columns(client, config)
    items = [card.item.title for card in manager.project.columns['In progress'].cards]
    assert items == ['issue 3', 'issue 2', "pull_request 1"]

    # remove a single issue from the column
    manager.project.columns['In progress'].remove_card("56565=")
    items = [card.item.title for card in manager.project.columns['In progress'].cards]
    assert len(items) == 2
    assert manager.project.is_in_column("In progress", "1234=") is True
    assert manager.project.is_in_column("In progress", "76566=") is True
    assert manager.project.is_in_column("In progress", "56565=") is False

    # remove a single pull request from the column
    manager.project.columns['In progress'].remove_card("76565=")
    items = [card.item.title for card in manager.project.columns['In progress'].cards]
    assert len(items) == 1
    assert manager.project.is_in_column("In progress", "1234=") is True
    assert manager.project.is_in_column("In progress", "76566=") is False

    manager.manage()
    assert manager.project.is_in_column("In progress", "56565=") is False


def test_loading_org_project():
    org_project_layout = {
        "organization": {
            "project": {
                "columns": {
                    "edges": [
                        {
                            "cursor": 1,
                            "node": {
                                "name": "Queue"
                            }
                        },
                        {
                            "cursor": 2,
                            "node": {
                                "name": "Review in progress"
                            }
                        }
                    ]
                }
            }
        }
    }

    column1 = {
        "organization": {
            "project": {
                "name": "test",
                "columns": {
                    "nodes": [
                        {
                            "name": "Queue",
                            "id": "1234",
                            "cards": {
                                "pageInfo": {
                                    "hasNextPage": False,
                                    "endCursor": "MQ"
                                },
                                "edges": [
                                    {
                                        "cursor": "MQ",
                                        "node": {
                                            "note": None,
                                            "state": "CONTENT_ONLY",
                                            "id": "3434=",
                                            "content": {
                                                "__typename": "Issue",
                                                "id": "1234=",
                                                "number": 1,
                                                "title": "issue 1",
                                                "labels": {
                                                    "edges": [
                                                        {
                                                            "node": {
                                                                "name": "High"
                                                            }
                                                        },
                                                        {
                                                            "node": {
                                                                "name": "bug"
                                                            }
                                                        }
                                                    ]
                                                },
                                                "assignees": {
                                                    "edges": []
                                                }
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
    }
    column2 = {
        "organization": {
            "project":
                {
                    "name": "test",
                    "columns": {
                        "nodes": [
                            {
                                "name": "In progress",
                                "id": "5656",
                                "cards": {
                                    "pageInfo": {
                                        "hasNextPage": False,
                                        "endCursor": "MQ"
                                    },
                                    "edges": [
                                        {
                                            "cursor": "MQ",
                                            "node": {
                                                "note": None,
                                                "state": "CONTENT_ONLY",
                                                "id": "56565=",
                                                "content": {
                                                    "__typename": "Issue",
                                                    "id": "56567=",
                                                    "number": 15,
                                                    "title": "issue 2",
                                                    "labels": {
                                                        "edges": [
                                                            {
                                                                "node": {
                                                                    "name": "Medium"
                                                                }
                                                            },
                                                            {
                                                                "node": {
                                                                    "name": "bug"
                                                                }
                                                            }
                                                        ]
                                                    },
                                                    "assignees": {
                                                        "edges": [
                                                            {
                                                                "node": {
                                                                    "id": "234",
                                                                    "login": "Rony Rony"
                                                                }
                                                            }
                                                        ]
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            "cursor": "MB",
                                            "node": {
                                                "note": None,
                                                "state": "CONTENT_ONLY",
                                                "id": "123=",
                                                "content": {
                                                    "__typename": "Issue",
                                                    "id": "1234=",
                                                    "number": 3,
                                                    "title": "issue 3",
                                                    "labels": {
                                                        "edges": [
                                                            {
                                                                "node": {
                                                                    "name": "High"
                                                                }
                                                            },
                                                            {
                                                                "node": {
                                                                    "name": "bug"
                                                                }
                                                            }
                                                        ]
                                                    },
                                                    "assignees": {
                                                        "edges": [
                                                            {
                                                                "node": {
                                                                    "id": "234",
                                                                    "login": "Rony Rony"
                                                                }
                                                            }
                                                        ]
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            "cursor": "HZ",
                                            "node": {
                                                "note": None,
                                                "state": "CONTENT_ONLY",
                                                "id": "76565=",
                                                "content": {
                                                    "__typename": "PullRequest",
                                                    "title": "pull_request 1",
                                                    "id": "76566=",
                                                    "state": "OPEN",
                                                    "number": 20,
                                                    "mergedAt": None,
                                                    "merged": False,
                                                    "reviewDecision": None,
                                                    "reviews": {
                                                        "totalCount": 0
                                                    },
                                                    "reviewRequests": {
                                                        "totalCount": 0
                                                    },
                                                    "labels": {
                                                        "edges": [
                                                            {
                                                                "node": {
                                                                    "name": "Medium"
                                                                }
                                                            },
                                                            {
                                                                "node": {
                                                                    "name": "bug"
                                                                }
                                                            }
                                                        ]
                                                    },
                                                    "assignees": {
                                                        "edges": [
                                                            {
                                                                "node": {
                                                                    "id": "334",
                                                                    "login": "Daud Daud"
                                                                }
                                                            }
                                                        ]
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
        }
    }

    pr_id = "=zxcx=sads="
    pr_title = "pr name"
    labels = ["HighEffort", "Critical", "bug", "test", "Testing"]
    assignee = "daud"

    pull_request = {
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
        "title": pr_title,
        "id": pr_id,
        "number": 1,
        "state": "MERGED",
        "mergedAt": "2021-01-25T15:27:08Z",
        "merged": True,
        "reviewDecision": None,
        "reviews": {
            "totalCount": 0
        },
        "reviewRequests": {
            "totalCount": 1
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
                },
                {
                    "node": {
                        "name": labels[3]
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
    }

    issue_id = "=asdf=sdf="
    issue_title = "issue name"
    issue = {
        "projectCards": {
            "nodes": [
                {
                    "id": "id=",
                    "column": {
                        "name": "Queue"
                    },
                    "project": {
                        "number": 1
                    }
                },
                {
                    "id": "id2=",
                    "column": {
                        "name": "In progress"
                    },
                    "project": {
                        "number": 2
                    }
                }
            ]
        },
        "comments": {
            "nodes": [
                {
                    "author": {
                        "login": "ronykoz"
                    },
                    "body": "comment 1",
                    "createdAt": "2019-03-19T12:24:27Z"
                },
                {
                    "author": {
                        "login": "ronykoz"
                    },
                    "body": "second comment",
                    "createdAt": "2019-03-19T12:27:53Z"
                },
                {
                    "author": {
                        "login": "ronykoz"
                    },
                    "body": "third comment",
                    "createdAt": "2019-03-19T12:52:08Z"
                }
            ]
        },
        "timelineItems": {
            "__typename": "IssueTimelineItemsConnection",
            "nodes": [
                {
                    "__typename": "LabeledEvent",
                    "label": {
                        "name": labels[0]
                    },
                    "createdAt": "2019-03-15T12:40:22Z"
                },
                {
                    "__typename": "LabeledEvent",
                    "label": {
                        "name": labels[1]
                    },
                    "createdAt": "2019-03-17T13:59:27Z"
                },
                {
                    "__typename": "LabeledEvent",
                    "label": {
                        "name": labels[2]
                    },
                    "createdAt": "2019-04-08T10:48:02Z"
                }
            ]
        },
        "title": issue_title,
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
                },
                {
                    "node": {
                        "name": labels[3]
                    }
                },
                {
                    "node": {
                        "name": labels[4]
                    }
                }
            ]
        },
        "assignees": {
            "edges": [
                {
                    "node": {
                        "login": "ronykoz"
                    }
                }
            ]
        }
    }

    items = {
        "repository": {
            "issues": {
                "pageInfo": {
                    "hasNextPage": True,
                    "endCursor": "cursor"
                },
                "edges": [
                    {
                        "node": issue
                    }
                ]
            }
        }
    }
    issues_with_no_after = {
        "repository": {
            "issues": {
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": "cursor"
                },
                "edges": [
                    {
                        "node": issue
                    }
                ]
            }
        }
    }

    config = Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'))
    config.load_properties()
    config.sort = True
    config.is_org_project = True

    class MockClient(object):
        def delete_project_card(*args, **kwargs):
            return

        def add_issues_to_project(self, **kwargs):
            return {
                "addProjectCard": {
                    "cardEdge": {
                        "node": {
                            "id": "id="
                        }
                    }
                }
            }

        def get_project_layout(self, **kwargs):
            return org_project_layout

        def get_first_column_items(self, **kwargs):
            return column1

        def get_column_items(self, **kwargs):
            return column2

        def get_github_issues(self, **kwargs):
            if not kwargs['after']:
                return items

            return issues_with_no_after

        def add_to_column(self, **kwargs):
            return

        def move_to_specific_place_in_column(self, **kwargs):
            return

        def get_github_pull_requests(self, **kwargs):
            return {
              "repository": {
                "pullRequests": {
                  "pageInfo": {
                    "endCursor": "cursor",
                    "hasNextPage": False
                  },
                  "edges": [
                    {
                      "node": pull_request,
                    }
                    ]
                }
              }
            }

    client = MockClient()
    manager = ProjectManager(configuration=config, client=client)

    assert len(manager.matching_issues) == 1
    assert len(manager.matching_pull_requests) == 1
    assert manager.project.name == 'test'
    assert manager.project.get_current_location("56567=") == ("In progress", "56565=")
    assert manager.project.get_current_location("Random text") == (None, None)
    assert manager.project.is_in_column("In progress", "56567=") is True
    assert manager.project.is_in_column("In progress", "Random text") is False

    # assert there're 3 items 'In Progress' column
    manager.project.sort_items_in_columns(client, config)
    items = [card.item.title for card in manager.project.columns['In progress'].cards]
    assert items == ['issue 3', 'issue 2', "pull_request 1"]

    # remove a single issue from the column
    manager.project.columns['In progress'].remove_card("56565=")
    items = [card.item.title for card in manager.project.columns['In progress'].cards]
    assert len(items) == 2
    assert manager.project.is_in_column("In progress", "1234=") is True
    assert manager.project.is_in_column("In progress", "76566=") is True
    assert manager.project.is_in_column("In progress", "56565=") is False

    # remove a single pull request from the column
    manager.project.columns['In progress'].remove_card("76565=")
    items = [card.item.title for card in manager.project.columns['In progress'].cards]
    assert len(items) == 1
    assert manager.project.is_in_column("In progress", "1234=") is True
    assert manager.project.is_in_column("In progress", "76566=") is False

    manager.manage()
    assert manager.project.is_in_column("In progress", "56565=") is False
