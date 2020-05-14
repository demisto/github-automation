import json
import os
from copy import deepcopy

from GitHubProjectManager.core.issue.issue import Issue
from GitHubProjectManager.core.project.project import Project, ProjectColumn
from GitHubProjectManager.management.configuration import Configuration
from GitHubProjectManager.management.event_manager import EventManager

MOCK_FOLDER_PATH = os.path.join(os.getcwd(), "tests", "mock_data")


def test_loading_event_manager():

    issue_id = "=asdf=sdf="
    title = "issue name"
    labels = ["HighEffort", "Low", "bug", "test"]
    assignee = "ronykoz"
    issue = {
        "projectCards": {
            "nodes": [
                {
                    "id": "id=",
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
                },
                {
                    "willCloseTarget": True,
                    "source": {
                        "__typename": "PullRequest",
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
    manager = EventManager(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'), client=client, event=json.dumps(event))

    issue_object = manager.get_issue_object()
    assert issue_object.number == 1
    assert issue_object.title == title


def test_matching_issue_filter():
    config = Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'))
    config.load_properties()

    assert EventManager.is_matching_issue(['test'], config.must_have_labels, config.cant_have_labels) is True
    assert EventManager.is_matching_issue(['not test'], config.must_have_labels, config.cant_have_labels) is False
    assert EventManager.is_matching_issue(['not test', 'test'],
                                          config.must_have_labels, config.cant_have_labels) is False


def test_get_prev_column():
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


def test_load_project_column():
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
        def add_issues_to_project(self, **kwargs):
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

        def get_first_column_issues(*args, **kwargs):
            if 'start_cards_cursor' in kwargs:
                return project_column1_no_after

            return project_column1

        def get_column_issues(*args, **kwargs):
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
    assert project1.columns["Queue"].cards[0].issue.title == "title"
    assert project1.columns["Queue"].cards[0].id == "id="

    project2 = manager.load_project_column("In progress")
    assert project2.columns["In progress"].name == "In progress"
    assert len(project2.columns["In progress"].cards) == 2
    assert project2.columns["In progress"].cards[0].issue.title == "title2"
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
    mocker.patch.object(EventManager, "get_issue_object", return_value=Issue(
        id="1",
        title="this is a test title",
        number=1,
        assignees=["ronykoz"],
        labels=['test', 'Testing']
    ))
    mocker.patch.object(EventManager, "load_project_column",
                        return_value=project_object
                        )

    class MockClient(object):
        def add_issues_to_project(*args, **kwargs):
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
    assert len(project_object.get_all_issue_ids()) == 1
