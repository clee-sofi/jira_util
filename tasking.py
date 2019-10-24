import json
import sys
from parse_jira import get, delete, post
from parse_jira import getIssuesFromBoard, getSprints, saveCredentials


def deleteIssue(key):
    url = 'https://sofiinc.atlassian.net/rest/api/2/issue/{0}'.format(key)
    return delete(url)


def getIssueId(key):
    url = 'https://sofiinc.atlassian.net/rest/agile/1.0/issue/{0}?fields=id'.format(key)
    response = get(url)

    return response['id']


def getCreateMeta():
    url = 'https://sofiinc.atlassian.net/rest/api/2/issue/createmeta?projectKeys=INV&issuetypeNames=Sub-task&expand=projects.issuetypes.fields'
    response = get(url)

    print(response)

    '''
    for project in response['projects']:
        #print(project['key'])
        if project['key'] == 'SOFI':
            print(project)
           '''

    return ''


def createSubtaskInput(parentKey, summary):
    return {
        'fields': {
            'project': {
                'key': 'INV'
            },
            'issuetype': {
                'name': 'Sub-task'
            },
            'parent': {
                'key': parentKey
            },
#            'customfield_12600': { # Product Team
#                'value': 'Invest'
#            },
            'customfield_15634': { # Pod
                'value': 'IPY' 
            },
            'summary': summary
        }
    }


def createSubtask(parentKey, summary):
    return post('https://sofiinc.atlassian.net/rest/api/2/issue', issue)


def createSubtasks(parentKey, summaries):
    issueUpdates = []
    for summary in summaries:
        issueUpdates.append(createSubtaskInput(parentKey, summary))

    return post('https://sofiinc.atlassian.net/rest/api/2/issue/bulk', {'issueUpdates': issueUpdates})


def handleTicket(parentKey, summaries):
    return createSubtasks(parentKey, summaries)


def handleSprint(sprintId, summaries):
    boardId = '318'
    issueUpdates = []
    
    # get all IPY issues from the sprint
    issues = filter(lambda i: 'labels' in i['fields'] and 'IPY' in i['fields']['labels'], getIssuesFromBoard(boardId=boardId, sprintId=sprintId))

    '''
    for issue in issues:
        print(issue['key'])
    '''

    

    # for each issue, if the issue does not already have subtasks, create subtask json and append to issueUpdates array
    for issue in issues:
        if len(issue['fields']['subtasks']) == 0:
            # if there are no subtasks
            for summary in summaries:
                issueUpdates.append(createSubtaskInput(issue['key'], summary))

    # bulk create subtasks
    return post('https://sofiinc.atlassian.net/rest/api/2/issue/bulk', {'issueUpdates': issueUpdates})


if __name__ == '__main__':
    if (len(sys.argv) == 4):
        if (sys.argv[1] == 'init'):
            saveCredentials(sys.argv[2], sys.argv[3])
            exit()
    '''
    if len(sys.argv) == 3:
        if sys.argv[1] == '--delete':
            deleteIssue(sys.argv[2])
            exit()
    '''
        
    if (len(sys.argv) > 3):
        
        if sys.argv[1] == '--ticket':
            handleTicket(sys.argv[2], sys.argv[3:])
            exit()

        if sys.argv[1] == '--sprint':
            handleSprint(sys.argv[2], sys.argv[3:])
            exit()

    if (len(sys.argv) == 2):
        if sys.argv[1] == '--list-sprints':
            getSprints()
            exit()

    
    print('Usage: python3 tasking.py [init {username} {password}] | [--ticket SOFI-XXXX "Task 1" "Task 2" ...] | [--sprint {sprintId} "Task 1" "Task 2" ...]')
