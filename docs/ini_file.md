## Configuration file
This file will help you determine the set of rules you want to apply on your project.

As an example you can take a look at:
```buildoutcfg
[General]
closed_issues_column = Done
project_owner = ronykoz
repository_name = test
is_org_project = false
project_number = 1
priority_list = Critical,High,Medium,Low
filter_labels=bug
must_have_labels=test
cant_have_labels=not test
column_names = Queue,In progress,Review in progress,Waiting for Docs
column_rule_desc_order = Queue,Waiting for Docs,Review in progress,In progress

[Actions]
remove
add
move

[Queue]
issue.assignees = false

[In progress]
issue.assignees = true

[Review in progress]
issue.assignees = true
issue.pull_request = true
issue.pull_request.review_requested = true

[Waiting for Docs]
issue.assignees = true
issue.pull_request = true
issue.pull_request.review_requested = true
issue.pull_request.review_completed = true
issue.pull_request.assignees = ronykoz

```

#### General section
This section will help you set the basic rules for the project. All the fields there are mandatory and are used to automate your project board.
Here is a quick explanation about their meaning:

- closed_issues_column - The column name of the closed issues.
- closed_pull_requests_column - The column name of the closed pull requests.
- merged_pull_requests_column - The column name of the merged pull requests.
- project_owner - The project owner or organization the repository is in.
- repository_name - The name of the repository containing the project.
- is_org_project - Whether the managed project is an organization level project linked to a repository - optional values are true/false.
- project_number - The project number you will want to manage
- priority_list - The list of priorities you want to order your issues by, descending order.(The default is Critical,High,Medium,Low - for labels with the same power use `||` - i.e. `priority1||priority2`)
- filter_labels - The labels you want to filter the issues that get into the project by.(In case of multiple labels we support CSV format and the condition is or between the labels, Please choose a strict filter to reduce API usage)
- must_have_label - The labels that the issue must have in-order to be in the project board.(CSV supported, with an AND condition)
- cant_have_labels - The labels that the issue cannot have in-order to be in the project board.(CSV supported, with an AND condition)
- column_names - The list of column names.
- column_rule_desc_order - The list of column names by descending power, meaning that the leftmost column will be taken into consideration before the one after him.


#### Actions section
This will determine the list of actions you want to apply on your board.
The supported options are:

- add - Adds issues to the project board
- remove - Removes issues from the project board if none of the criterias are met
- move - Move issues within the board(From one column to another)
- sort - Sort issues within each column - by the priorities.

#### Column sections
The column section is the place you will determine the rules for that column. The optional keys are:

- issue.assignees - Could be the names of the assignees(CSV will be AND condition, and `||` will be OR condition, True for any assignee, False for no assignees)
- issue.labels - Could be the names of the labels (CSV will be AND condition, and `||` will be OR condition, True for any labels, False for no labels)
- issue.pull_request - Whether there is a Pull request or not - optional values true/false
- issue.pull_request.review_requested - Whether a review was requested for the Pull request- optional values true/false
- issue.pull_request.review_completed - Whether the Pull request review is completed - optional values true/false
- issue.pull_request.review_requested_changes - Whether the Pull request review requested for changes - optional values true/false
- issue.pull_request.assignees - Could be the names of the assignees(CSV will be AND condition, and `||` will be OR condition, True for any assignee, False for no assignees)
- issue.pull_request.labels - Could be the names of the labels (CSV will be AND condition, and `||` will be OR condition, True for any labels, False for no labels)
- pull_request.assignees - Could be the names of the assignees(CSV will be AND condition, and `||` will be OR condition, True for any assignee, False for no assignees)
- pull_request.review_requested - Whether a review was requested for the Pull request- optional values true/false
- pull_request.labels - Could be the names of the labels (CSV will be AND condition, and `||` will be OR condition, True for any labels, False for no labels)
- pull_request.review_completed - Whether the Pull request review is completed - optional values true/false
- pull_request.review_requested_changes - Whether the Pull request review requested for changes - optional values true/false


