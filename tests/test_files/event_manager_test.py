import json
import os
import sys
from io import StringIO
from copy import deepcopy

from github_automation.core.project_item.issue import Issue
from github_automation.core.project.project import Project, ProjectColumn
from github_automation.management.configuration import Configuration
from github_automation.management.event_manager import EventManager

MOCK_FOLDER_PATH = os.path.join(os.getcwd(), "tests", "mock_data")


def test_loading_event_manager_with_issue():

    issue_id = "=asdf=sdf="
    title = "issue name"
    labels = ["HighEffort", "Low", "bug", "test"]
    assignee = "ronykoz"
    issue = {
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
                },
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

    issue_event = {
        "action": "some action",
        "issue": {
            "number": 1
        }
    }

    class mock_client(object):
        def get_issue(*args, **kwargs):
            return {
                "repository": {
                    "issue": issue
                }
            }

    client = mock_client()
    manager = EventManager(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'), client=client, event=json.dumps(issue_event))

    issue_object = manager.get_project_item_object()
    assert issue_object.number == 1
    assert issue_object.title == title


def test_loading_event_manager_with_pull_request():

    pr_id = "=asdf=sdf="
    title = "pr name"
    labels = ["HighEffort", "Low", "bug", "test"]
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
        "title": title,
        "id": pr_id,
        "number": 1,
        "state": "OPEN",
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

    pr_event = {
        "action": "some action",
        "pull_request": {
            "number": 1
        }
    }

    class mock_client(object):
        def get_pull_request(*args, **kwargs):
            return {
                "repository": {
                    "pullRequest": pull_request
                }
            }

    client = mock_client()
    manager = EventManager(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'), client=client, event=json.dumps(pr_event))

    pr_object = manager.get_project_item_object()
    assert pr_object.number == 1
    assert pr_object.title == title


def test_get_prev_column_repo_project():
    event = {
        "action": "some action",
        "issue": {
            "number": 1
        }
    }

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
                                "name": "In progress"
                            }
                        }
                    ]
                }
            }
        }
    }

    class MockClient(object):
        def get_project_layout(*args, **kwargs):
            return project_layout

    client = MockClient()
    manager = EventManager(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'), client=client,
                           event=json.dumps(event))
    manager.config = Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'))
    manager.config.load_properties()

    assert manager.get_prev_column_cursor("Queue") == ""
    assert manager.get_prev_column_cursor("In progress") == 1


def test_get_prev_column_org_project():
    event = {
        "action": "some action",
        "issue": {
            "number": 1
        }
    }

    project_layout = {
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
                                "name": "In progress"
                            }
                        }
                    ]
                }
            }
        }
    }

    class MockClient(object):
        def get_project_layout(*args, **kwargs):
            return project_layout

    client = MockClient()
    manager = EventManager(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'), client=client,
                           event=json.dumps(event))
    manager.config = Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'))
    manager.config.load_properties()
    manager.config.is_org_project = True

    assert manager.get_prev_column_cursor("Queue") == ""
    assert manager.get_prev_column_cursor("In progress") == 1


def test_load_repo_project_column():
    event = {
        "action": "some action",
        "issue": {
            "number": 1
        }
    }

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
                                "name": "In progress"
                            }
                        }
                    ]
                }
            }
        }
    }

    project_column1 = {
        "repository": {
            "project": {
                "columns": {
                    "nodes": [
                        {
                            "name": "Queue",
                            "id": "id",
                            "cards": {
                                "pageInfo": {
                                    "endCursor": "A",
                                    "hasNextPage": True
                                },
                                "edges": [
                                    {
                                        "cursor": "A",
                                        "node": {
                                            "note": None,
                                            "state": "CONTENT_ONLY",
                                            "id": "id=",
                                            "content": {
                                                "__typename": "Issue",
                                                "id": "id=",
                                                "number": 1,
                                                "title": "title",
                                                "labels": {
                                                    "edges": [
                                                        {
                                                            "node": {
                                                                "name": "one"
                                                            }
                                                        },
                                                        {
                                                            "node": {
                                                                "name": "two"
                                                            }
                                                        },
                                                        {
                                                            "node": {
                                                                "name": "three"
                                                            }
                                                        }
                                                    ]
                                                }
                                            }
                                        }
                                    }
                                ]
                            },
                        }
                    ]
                }
            }
        }
    }
    project_column1_no_after = deepcopy(project_column1)
    project_column1_no_after['repository']['project']['columns']['nodes'][0]['cards']['pageInfo']['hasNextPage'] = False

    project_column2 = {
        "repository": {
            "project": {
                "columns": {
                    "nodes": [
                        {
                            "name": "In progress",
                            "id": "id",
                            "cards": {
                                "pageInfo": {
                                    "endCursor": "B",
                                    "hasNextPage": True
                                },
                                "edges": [
                                    {
                                        "cursor": "B",
                                        "node": {
                                            "note": None,
                                            "state": "CONTENT_ONLY",
                                            "id": "cardid2=",
                                            "content": {
                                                "__typename": 'Issue',
                                                "id": "id2=",
                                                "number": 2,
                                                "title": "title2",
                                                "labels": {
                                                    "edges": [
                                                        {
                                                            "node": {
                                                                "name": "one"
                                                            }
                                                        },
                                                        {
                                                            "node": {
                                                                "name": "two"
                                                            }
                                                        },
                                                        {
                                                            "node": {
                                                                "name": "three"
                                                            }
                                                        }
                                                    ]
                                                }
                                            }
                                        }
                                    }
                                ]
                            },
                        }
                    ]
                }
            }
        }
    }

    project_column2_no_after = deepcopy(project_column2)
    project_column2_no_after['repository']['project']['columns']['nodes'][0]['cards']['pageInfo']['hasNextPage'] = False

    issue_id = "=asdf=sdf="
    title = "issue name"
    labels = ["test", "Low", "bug", "Testing"]
    assignee = "ronykoz"

    issue = {
        "repository": {
            "issue": {
                "projectCards": {
                    "nodes": [
                        {
                            "id": "idadded=",
                            "project": {
                                "number": 1,
                                "columns": {
                                    "nodes": [
                                        {
                                            "name": "testing"
                                        }
                                    ]
                                }
                            }
                        },
                        {
                            "id": "id2=",
                            "project": {
                                "number": 2,
                                "columns": {
                                    "nodes": [
                                        {
                                            "name": "Queue"
                                        }
                                    ]
                                }
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
        }
    }

    class MockClient(object):
        def add_items_to_project(self, **kwargs):
            return {
                "addProjectCard": {
                    "cardEdge": {
                        "node": {
                            "id": "idadded="
                        }
                    }
                }
            }

        def add_to_column(self, **kwargs):
            return

        def move_to_specific_place_in_column(self, **kwargs):
            return

        def get_issue(*args, **kwargs):
            return issue

        def delete_project_card(*args, **kwargs):
            return

        def get_project_layout(*args, **kwargs):
            return project_layout

        def get_first_column_items(*args, **kwargs):
            if 'start_cards_cursor' in kwargs:
                return project_column1_no_after

            return project_column1

        def get_column_items(*args, **kwargs):
            if 'start_cards_cursor' in kwargs:
                return project_column2_no_after

            return project_column2

    client = MockClient()
    manager = EventManager(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'), client=client, event=json.dumps(event))
    manager.config = Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'))
    manager.config.load_properties()

    project1 = manager.load_project_column("Queue")
    assert project1.columns["Queue"].name == "Queue"
    assert len(project1.columns["Queue"].cards) == 2
    assert project1.columns["Queue"].cards[0].item.title == "title"
    assert project1.columns["Queue"].cards[0].id == "id="

    project2 = manager.load_project_column("In progress")
    assert project2.columns["In progress"].name == "In progress"
    assert len(project2.columns["In progress"].cards) == 2
    assert project2.columns["In progress"].cards[0].item.title == "title2"
    assert project2.columns["In progress"].get_card_id("id2=") == "cardid2="


def test_load_org_project_column():
    event = {
        "action": "some action",
        "issue": {
            "number": 1
        }
    }

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
                                "name": "In progress"
                            }
                        }
                    ]
                }
            }
        }
    }

    org_project_column1 = {
        "organization": {
            "project": {
                "columns": {
                    "nodes": [
                        {
                            "name": "Queue",
                            "id": "id",
                            "cards": {
                                "pageInfo": {
                                    "endCursor": "A",
                                    "hasNextPage": True
                                },
                                "edges": [
                                    {
                                        "cursor": "A",
                                        "node": {
                                            "note": None,
                                            "state": "CONTENT_ONLY",
                                            "id": "id=",
                                            "content": {
                                                "__typename": "Issue",
                                                "id": "id=",
                                                "number": 1,
                                                "title": "title",
                                                "labels": {
                                                    "edges": [
                                                        {
                                                            "node": {
                                                                "name": "one"
                                                            }
                                                        },
                                                        {
                                                            "node": {
                                                                "name": "two"
                                                            }
                                                        },
                                                        {
                                                            "node": {
                                                                "name": "three"
                                                            }
                                                        }
                                                    ]
                                                }
                                            }
                                        }
                                    }
                                ]
                            },
                        }
                    ]
                }
            }
        }
    }
    project_column1_no_after = deepcopy(org_project_column1)
    project_column1_no_after['organization']['project']['columns']['nodes'][0]['cards']['pageInfo'][
        'hasNextPage'] = False

    org_project_column2 = {
        "organization": {
            "project": {
                "columns": {
                    "nodes": [
                        {
                            "name": "In progress",
                            "id": "id",
                            "cards": {
                                "pageInfo": {
                                    "endCursor": "B",
                                    "hasNextPage": True
                                },
                                "edges": [
                                    {
                                        "cursor": "B",
                                        "node": {
                                            "note": None,
                                            "state": "CONTENT_ONLY",
                                            "id": "cardid2=",
                                            "content": {
                                                "__typename": 'Issue',
                                                "id": "id2=",
                                                "number": 2,
                                                "title": "title2",
                                                "labels": {
                                                    "edges": [
                                                        {
                                                            "node": {
                                                                "name": "one"
                                                            }
                                                        },
                                                        {
                                                            "node": {
                                                                "name": "two"
                                                            }
                                                        },
                                                        {
                                                            "node": {
                                                                "name": "three"
                                                            }
                                                        }
                                                    ]
                                                }
                                            }
                                        }
                                    }
                                ]
                            },
                        }
                    ]
                }
            }
        }
    }

    project_column2_no_after = deepcopy(org_project_column2)
    project_column2_no_after['organization']['project']['columns']['nodes'][0]['cards']['pageInfo'][
        'hasNextPage'] = False

    issue_id = "=asdf=sdf="
    title = "issue name"
    labels = ["test", "Low", "bug", "Testing"]
    assignee = "ronykoz"

    issue = {
        "repository": {
            "issue": {
                "projectCards": {
                    "nodes": [
                        {
                            "id": "idadded=",
                            "project": {
                                "number": 1,
                                "columns": {
                                    "nodes": [
                                        {
                                            "name": "testing"
                                        }
                                    ]
                                }
                            }
                        },
                        {
                            "id": "id2=",
                            "project": {
                                "number": 2,
                                "columns": {
                                    "nodes": [
                                        {
                                            "name": "Queue"
                                        }
                                    ]
                                }
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
        }
    }

    class MockClient(object):
        def add_items_to_project(self, **kwargs):
            return {
                "addProjectCard": {
                    "cardEdge": {
                        "node": {
                            "id": "idadded="
                        }
                    }
                }
            }

        def add_to_column(self, **kwargs):
            return

        def move_to_specific_place_in_column(self, **kwargs):
            return

        def get_issue(*args, **kwargs):
            return issue

        def delete_project_card(*args, **kwargs):
            return

        def get_project_layout(*args, **kwargs):
            return org_project_layout

        def get_first_column_items(*args, **kwargs):
            if 'start_cards_cursor' in kwargs:
                return project_column1_no_after

            return org_project_column1

        def get_column_items(*args, **kwargs):
            if 'start_cards_cursor' in kwargs:
                return project_column2_no_after

            return org_project_column2

    client = MockClient()
    manager = EventManager(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'), client=client, event=json.dumps(event))
    manager.config = Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'))
    manager.config.load_properties()
    manager.config.is_org_project = True

    project1 = manager.load_project_column("Queue")
    assert project1.columns["Queue"].name == "Queue"
    assert len(project1.columns["Queue"].cards) == 2
    assert project1.columns["Queue"].cards[0].item.title == "title"
    assert project1.columns["Queue"].cards[0].id == "id="

    project2 = manager.load_project_column("In progress")
    assert project2.columns["In progress"].name == "In progress"
    assert len(project2.columns["In progress"].cards) == 2
    assert project2.columns["In progress"].cards[0].item.title == "title2"
    assert project2.columns["In progress"].get_card_id("id2=") == "cardid2="


def test_event_manager_flow(mocker):
    config = Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'))
    config.load_properties()

    project_object = Project(name="project_name",
                             columns={
                                  "In progress": ProjectColumn(id="some id", name='In progress', cards=[])
                             },
                             config=config
                             )
    mocker.patch.object(EventManager, "get_project_item_object", return_value=Issue(
        id="1",
        title="this is a test title",
        number=1,
        assignees=["ronykoz"],
        labels=['test', 'Testing', 'bug']
    ))
    mocker.patch.object(EventManager, "load_project_column",
                        return_value=project_object
                        )

    class MockClient(object):
        def add_items_to_project(*args, **kwargs):
            return {
                "addProjectCard": {
                    "cardEdge": {
                        "node": {
                            "id": "1"
                        }
                    }
                }
            }

        def add_to_column(self, **kwargs):
            return

        def move_to_specific_place_in_column(self, **kwargs):
            return

    client = MockClient()
    manager = EventManager(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'), client=client,
                           event=json.dumps({"text": "text"}))
    manager.run()
    assert len(project_object.get_all_item_ids()) == 1


def test_loading_event_manager_without_an_item():
    event = {
        "action": "some action"
    }

    class mock_client(object):
        def get_issue(*args, **kwargs):
            return

    client = mock_client()
    manager = EventManager(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'), client=client, event=json.dumps(event))

    issue_object = manager.get_project_item_object()
    assert issue_object is None
    assert manager.run() is None


def test_loading_event_manager_with_closed_issue():
    issue_id = "=asdf=sdf="
    title = "issue name"
    labels = ["HighEffort", "Low", "bug", "test"]
    assignee = "ronykoz"
    issue = {
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
                },
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
        "state": "CLOSED",
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

    event = {
        "action": "some action",
        "issue": {
            "number": 1
        }
    }

    class mock_client(object):
        def get_issue(*args, **kwargs):
            return {
                "repository": {
                    "issue": issue
                }
            }

    client = mock_client()
    saved_stdout = sys.stdout
    manager = EventManager(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'), client=client, event=json.dumps(event))

    out = StringIO()
    sys.stdout = out

    assert manager.run() is None
    assert 'The item is closed' in out.getvalue()
    sys.stdout = saved_stdout


def test_loading_event_manager_with_merged_pull_request():
    pr_id = "=asdf=sdf="
    title = "pr name"
    labels = ["HighEffort", "Low", "bug", "test"]
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
        "title": title,
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
            "totalCount": 0
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

    event = {
        "action": "some action",
        "pull_request": {
            "number": 1
        }
    }

    class mock_client(object):
        def get_pull_request(*args, **kwargs):
            return {
                "repository": {
                    "pullRequest": pull_request
                }
            }

    client = mock_client()
    saved_stdout = sys.stdout
    manager = EventManager(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'), client=client, event=json.dumps(event))

    out = StringIO()
    sys.stdout = out

    assert manager.run() is None
    assert 'The item is merged' in out.getvalue()
    sys.stdout = saved_stdout
