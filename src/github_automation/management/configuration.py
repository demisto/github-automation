import logging
import os
from configparser import ConfigParser


class Configuration(object):
    DELIMITER = ','
    LIST_ATTRIBUTES = [
        'priority_list',
        'filter_labels',
        'must_have_labels',
        'cant_have_labels',
        'column_names',
        'column_rule_desc_order'
    ]
    CONDITIONAL_LIST_ATTRIBUTES = [
        'issue.assignees',
        'issue.labels',
        'issue.pull_request.assignees',
        'issue.pull_request.labels',
        'pull_request.assignees',
        'pull_request.labels',
    ]
    PERMITTED_QUERIES = [
        'issue.assignees',
        'issue.pull_request',
        'issue.pull_request.review_requested',
        'issue.labels',
        'issue.pull_request.review_completed',
        'issue.pull_request.assignees',
        'issue.pull_request.labels',
        'issue.pull_request.review_requested_changes',
        'pull_request.assignees',
        'pull_request.review_requested',
        'pull_request.labels',
        'pull_request.review_completed',
        'pull_request.review_requested_changes',
    ]  # TODO: load this list dynamically from the project
    GENERAL_SECTIONS = [
        'General',
        'Actions'
    ]
    OPTIONAL_ACTIONS = [
        'remove',
        'add',
        'move',
        'sort'
    ]

    SECTION_NAME_ERROR = 'You have either added a section which is not in the column_names key in the ' \
                         'General section, or miss-spelled. The section name is {}'
    ILLEGAL_QUERY = "You have entered an illegal query - {}, the possible options are:\n" + '\n'.join(PERMITTED_QUERIES)

    def __init__(self, conf_file_path, verbose=2, quiet=False, log_path=''):
        self.config = ConfigParser(allow_no_value=True)
        self.config.read(conf_file_path)

        # General
        self.closed_issues_column = ''
        self.closed_pull_requests_column = ''
        self.merged_pull_requests_column = ''
        self.project_owner = ''
        self.repository_name = ''
        self.project_number = None
        self.priority_list = []
        self.filter_labels = []
        self.filter_milestone = ''
        self.must_have_labels = []
        self.cant_have_labels = []
        self.column_names = []
        self.column_rule_desc_order = []
        self.is_org_project = False

        # Actions
        self.remove = False
        self.add = False
        self.move = False
        self.sort = False

        # Conditional
        self.column_to_rules = {}

        self.logger = self.logging_setup(verbose, quiet, log_path, conf_file_path)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def custom_set_attr(self, key, value):
        if self.DELIMITER in value:
            value = value.split(self.DELIMITER)

        elif value.isdigit():
            value = int(value)

        if key in self.LIST_ATTRIBUTES and not isinstance(value, list):
            value = [value]

        self.__setattr__(key, value)

    def load_general_properties(self):
        for key in self.config['General']:
            if key not in self.__dict__:
                raise ValueError(f'Provided illegal key - {key} in General section')

            self.custom_set_attr(key, self.config['General'][key])

    def load_actions(self):
        for key in self.config['Actions']:
            if key not in self.OPTIONAL_ACTIONS:
                raise ValueError(f'Provided illegal key - {key} in Actions section')

            self.__setattr__(key, True)

    def load_column_rules(self):
        for section in self.config.sections():
            if section in self.GENERAL_SECTIONS:
                continue

            if section not in self.column_names:
                raise ValueError(self.SECTION_NAME_ERROR.format(section))

            self.column_to_rules[section] = {}
            for key in self.config[section]:
                if key not in self.PERMITTED_QUERIES:
                    raise ValueError(self.ILLEGAL_QUERY.format(key))
                value = self.config[section][key]

                if value in ['true', 'True']:
                    value = True

                if value in ['false', 'False']:
                    value = False

                if key in self.CONDITIONAL_LIST_ATTRIBUTES and not isinstance(value, bool):
                    value = value.split(self.DELIMITER)

                self.column_to_rules[section][key] = value

    def load_properties(self):
        self.load_general_properties()
        self.load_actions()
        self.load_column_rules()

    def get_closed_columns(self):
        return self.closed_issues_column, self.closed_pull_requests_column, self.merged_pull_requests_column

    @staticmethod
    def logging_setup(verbose, quiet, log_path, conf_file_path):
        if quiet:
            verbose = 0

        logger: logging.Logger = logging.getLogger('github-automation')
        logger.setLevel(logging.DEBUG)
        log_level = logging.getLevelName((6 - 2 * verbose) * 10)
        fmt = logging.Formatter('%(message)s')

        if verbose:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(fmt)
            logger.addHandler(console_handler)

        if log_path:
            log_file_name = os.path.basename(conf_file_path)
            file_handler = logging.FileHandler(filename=os.path.join(log_path, f'{log_file_name}.log'))
            file_handler.setFormatter(fmt)
            file_handler.setLevel(level=logging.DEBUG)
            logger.addHandler(file_handler)

        logger.propagate = False

        return logger
