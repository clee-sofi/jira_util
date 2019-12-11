# JIRA Utils #

This repo contains some pretty hacky scripts that use the JIRA REST APIs.

Documentation for the APIs used in these scripts:

* https://developer.atlassian.com/cloud/jira/software/rest
* https://docs.atlassian.com/software/jira/docs/api/REST/8.1.0


# Requirements #
* python 3
* requests module

## Installing dependencies ##
```
pip3 install -r requirements.txt
```

# Overview of Functions #

## Initialization ##

The user name and API key needs to be saved to file for use by the python scripts.

An API key can be generated here: https://confluence.atlassian.com/cloud/api-tokens-938839638.html

```
python parse_jira.py init [username] [api key]

```

## Set Pod to your pod ##
If you don't set your pod it will default to IPY
```
python parse_jira.py setPod [podId]
```

## Burndown Snapshot ##

This displays the basic metrics (completed story points / total story points, etc) per Pod for the current sprint.

```
python parse_jira.py active
```

## Tasking ##

Easily create multiple subtasks for use with tasking.

Create tasks for a single ticket:

```
python tasking.py --ticket SOFI-1234 "Task 1" "Task 2" ...
```

To create the same task for every ticket in a sprint,
first find the sprint id:

```
python tasking.py --list-sprints
```

Then use that sprint id in the following command:

```
python tasking.py --sprint {sprintId} "Developing" "Testing"
```
