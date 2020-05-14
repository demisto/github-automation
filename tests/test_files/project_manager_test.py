import os

from GitHubProjectManager.management.configuration import Configuration
from GitHubProjectManager.management.project_manager import ProjectManager

MOCK_FOLDER_PATH = os.path.join(os.getcwd(), "tests", "mock_data")


def test_loading():
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
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
        }
    }

    issue_id = "=asdf=sdf="
    title = "issue name"
    labels = ["HighEffort", "Critical", "bug", "test", "Testing"]
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

    issues = {
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

        def get_first_column_issues(self, **kwargs):
            return column1

        def get_column_issues(self, **kwargs):
            return column2

        def get_github_issues(self, **kwargs):
            if not kwargs['after']:
                return issues

            return issues_with_no_after

        def add_to_column(self, **kwargs):
            return

        def move_to_specific_place_in_column(self, **kwargs):
            return

    client = MockClient()
    manager = ProjectManager(configuration=config, client=client)

    assert len(manager.matching_issues) == 1
    assert manager.project.name == 'test'
    assert manager.project.get_current_location("56567=") == ("In progress", "56565=")
    assert manager.project.get_current_location("Random text") == (None, None)
    assert manager.project.is_in_column("In progress", "56567=") is True
    assert manager.project.is_in_column("In progress", "Random text") is False

    manager.project.sort_issues_in_columns(client, config)
    issues = [card.issue.title for card in manager.project.columns['In progress'].cards]
    assert issues == ['issue 3', 'issue 2']

    manager.project.columns['In progress'].remove_card("56565=")
    assert manager.project.is_in_column("In progress", "56567=") is False

    manager.manage()
    assert manager.project.is_in_column("In progress", issue_id) is True
    assert manager.project.columns["In progress"].cards[0].issue.id == issue_id


def test_matching_issue_filter():
    config = Configuration(os.path.join(MOCK_FOLDER_PATH, 'conf.ini'))
    config.load_properties()

    assert ProjectManager.is_matching_issue(['test'], config.must_have_labels, config.cant_have_labels) is True
    assert ProjectManager.is_matching_issue(['not test'], config.must_have_labels, config.cant_have_labels) is False
    assert ProjectManager.is_matching_issue(['not test', 'test'],
                                            config.must_have_labels, config.cant_have_labels) is False
