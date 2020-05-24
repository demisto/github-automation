from __future__ import absolute_import

import sys

from pkg_resources import get_distribution

import click
from github_automation.common.constants import (MANAGE_COMMAND_NAME,
                                                WEBHOOK_MANAGER_COMMAND_NAME)
from github_automation.management.configuration import Configuration
from github_automation.management.event_manager import EventManager
from github_automation.management.project_manager import ProjectManager


@click.group(invoke_without_command=True, no_args_is_help=True, context_settings=dict(max_content_width=100), )
@click.help_option(
    '-h', '--help'
)
@click.option(
    '-v', '--version', help='Get the github-automation version.',
    is_flag=True, default=False, show_default=True
)
def main(version):
    if version:
        version = get_distribution('github-automation').version
        print(f'github-automation {version}')


@main.command(name=f"{MANAGE_COMMAND_NAME}",
              short_help="Manage a GitHub project board")
@click.help_option(
    '-h', '--help'
)
@click.option(
    '-c', '--conf', help='The path to the conf.ini file, In case of multiple projects use CSV format.', required=True
)
@click.option(
    '-v', "--verbose", count=True, help="Verbosity level -v / -vv / .. / -vvv",
    type=click.IntRange(0, 3, clamp=True), default=2, show_default=True
)
@click.option(
    '-q', "--quiet", is_flag=True, help="Quiet output, only output results in the end"
)
@click.option(
    "--log-path", help="Path to store all levels of logs", type=click.Path(exists=True, resolve_path=True)
)
def manage(**kwargs):
    """Manage a GitHub project board"""
    for conf_path in kwargs['conf'].split(','):
        configuration = Configuration(conf_file_path=conf_path,
                                      verbose=kwargs['verbose'],
                                      quiet=kwargs['quiet'],
                                      log_path=kwargs['log_path'])
        configuration.load_properties()
        configuration.logger.info(f'Starting going over the board {conf_path}')
        manager = ProjectManager(configuration=configuration)
        manager.manage()


@main.command(name=f"{WEBHOOK_MANAGER_COMMAND_NAME}",
              short_help="Manage a GitHub project board using Web-hooks and github actions")
@click.help_option(
    '-h', '--help'
)
@click.option(
    '-c', '--conf', help='The path to the conf.ini file, In case of multiple projects use CSV format.', required=True
)
@click.option(
    '-e', '--event', help='The event object received from the GitHub Action', required=True
)
@click.option(
    '-v', "--verbose", count=True, help="Verbosity level -v / -vv / .. / -vvv",
    type=click.IntRange(0, 3, clamp=True), default=2, show_default=True
)
@click.option(
    '-q', "--quiet", is_flag=True, help="Quiet output, only output results in the end"
)
@click.option(
    "--log-path", help="Path to store all levels of logs", type=click.Path(exists=True, resolve_path=True)
)
def event_manager(**kwargs):
    """Manage a GitHub project board using events and GitHub actions."""
    manager = EventManager(**kwargs)
    return manager.run()


@main.resultcallback()
def exit_from_program(result=0, **kwargs):
    sys.exit(result)


if __name__ == '__main__':
    main()
