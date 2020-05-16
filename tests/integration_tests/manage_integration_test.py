from __future__ import absolute_import

import os

import pytest
from click.testing import CliRunner
from github_automation.cli.main import main
from github_automation.common.constants import (MANAGE_COMMAND_NAME,
                                                WEBHOOK_MANAGER_COMMAND_NAME)

MOCK_FOLDER_PATH = os.path.join(os.getcwd(), "tests", "mock_data")


@pytest.mark.skip(reason="Not ready yet")
def test_manage_positive_scenario(mocker):
    runner = CliRunner()
    result = runner.invoke(main, [MANAGE_COMMAND_NAME, '-c', os.path.join(MOCK_FOLDER_PATH, 'conf.ini')])  # noqa: F841

    mocker.patch()


@pytest.mark.skip(reason="Not ready yet")
def test_event_manager_positive_scenario(mocker):
    runner = CliRunner()
    result = runner.invoke(main, [WEBHOOK_MANAGER_COMMAND_NAME, '-c',  # noqa: F841
                                  os.path.join(MOCK_FOLDER_PATH, 'conf.ini'), '-e', '{\'issue\': 1}'])  # noqa: F841

    mocker.patch()


def test_get_version():
    runner = CliRunner()
    result = runner.invoke(main, ['-v'])

    assert result.exit_code == 0
    assert 'github-automation' in result.stdout
