## GitHub action usage

To get started you will need to configure an `.ini` file which will serve as your configuration file for the project - this file should be in your repository.
More detailed explanation can be found [here](https://github.com/demisto/github-automation/blob/master/docs/ini_file.md).
You will also need to add a secret to your repository configuration called `GITHUB_TOKEN`.

To use the action in case of an event you can set create the following yml in your repo.
``` buildoutcfg
on:
  issues:
    ypes: [opened, deleted, closed, reopened, assigned, unassigned, labeled, unlabeled, milestoned, demilestoned]
  project_card:
    types: [created, moved, deleted]

jobs:
  manage_project_board:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python 3.7
        uses: actions/setup-python@v1
        with:
          python-version: '3.7'
      - name: Get project manager
        run: |
          pip install github-automation
      - name: Manage project
        run: |
          github-automation webhook-manage -c <The path to your configuration file>
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

In case you want to schedule a command to re-organize your whole board you can use:
``` buildoutcfg
on:
  schedule:
    - cron:  '* */1 * * *'

jobs:
  manage_project_board:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python 3.7
        uses: actions/setup-python@v1
        with:
          python-version: '3.7'
      - name: Get project manager
        run: |
          pip install github-automation
      - name: Manage project
        run: |
          github-automation manage -c <The path to your configuration file>
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
