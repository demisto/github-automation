from __future__ import absolute_import

import pytest
from github_automation.common.constants import OR
from github_automation.common.utils import is_matching_project_item


@pytest.mark.parametrize('issue_labels, must_have_labels, cant_have_labels, filter_labels, result',
                         [
                             [['test', '1'], ['test'], ['2'], ['1'], True],
                             [['test', '1', '3'], ['test'], ['2'], ['1'], True],
                             [['test', '1', '3'], ['1'], ['2'], ['test'], True],
                             [['test', '1', '3'], ['1'], ['3'], ['test'], False],
                             [['test', '1', '3'], ['1'], ['3', '4'], ['test'], False],
                             [['test', '1', '3'], ['12'], ['3', '4'], ['test1'], False],
                             [['test', '1', '3'], ['1'], ['3', '4'], ['test1'], False],
                             [['test', '1', '3'], ['12'], ['3', '4'], ['test'], False],
                             [['test', '1', '3'], [f'some{OR}text'], ['3'], ['test'], False]
                         ])
def test_is_matching_project_item(issue_labels, must_have_labels, cant_have_labels, filter_labels, result):
    assert is_matching_project_item(issue_labels, must_have_labels, cant_have_labels, filter_labels) is result
