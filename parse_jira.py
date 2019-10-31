import requests
from requests.auth import HTTPBasicAuth
import json
import sys

''' Old way
def getStoryPoints(issue):
    if 'value' in issue['estimateStatistic']['statFieldValue']:
        return issue['estimateStatistic']['statFieldValue']['value']
    else:
        return 0.0


json_data = open('jira_dump.json').read()
data = json.loads(json_data)

swimlanes = data['swimlanesData']['customSwimlanesData']['swimlanes']
issues = dict((issue['id'], issue) for issue in data['issuesData']['issues'])

for swimlane in swimlanes:
    print('Pod name: {0}'.format(swimlane['name']))

    issueIds = swimlane['issueIds']

    completedIssues = 0
    totalStoryPoints = 0.0
    completedStoryPoints = 0.0
    for issueId in issueIds:
        issue = issues[issueId]
        status = issue['statusName']
        storyPoints = getStoryPoints(issue)
        
        if status == 'Closed' or status == 'Deployed to Prod' or status == 'Ready to Deploy':
            completedIssues = completedIssues + 1
            completedStoryPoints = completedStoryPoints + storyPoints
            
        totalStoryPoints = totalStoryPoints + storyPoints

    print('Completed issues: {0}'.format(completedIssues))
    print('Total issues: {0}'.format(len(issueIds)))
    print('Completed story points: {0}'.format(completedStoryPoints))
    print('Total story points: {0}'.format(totalStoryPoints))
    print('')
'''

class Pod:
    totalIssues = 0
    totalStoryPoints = 0.0
    completedIssues = 0
    completedStoryPoints = 0.0

    def __init__(self, name):
        self.name = name

    def trackIssue(self, issue):
        self.totalIssues = self.totalIssues + 1

        status = issue['fields']['status']['name']
        isDone = status == 'Ready to Deploy' or status == 'Deployed to Prod' or status == 'Closed'

        #print(issue['fields']['issuetype'])
        
        if 'customfield_10004' in issue['fields'] and issue['fields']['customfield_10004'] != None and issue['fields']['issuetype']['subtask'] == False:
            issueStoryPoints = issue['fields']['customfield_10004']
            self.totalStoryPoints = self.totalStoryPoints + issueStoryPoints
            if isDone:
                self.completedStoryPoints = self.completedStoryPoints + issueStoryPoints 
                
        if isDone:
            self.completedIssues = self.completedIssues + 1

    
    def printSummary(self):
        print('{0}:'.format(self.name))
        print('  completed issues: {0}/{1}'.format(self.completedIssues, self.totalIssues))
        print('  completed story points: {0}/{1}'.format(self.completedStoryPoints, self.totalStoryPoints))
        print('')


def saveCredentials(username, password):
    creds = {}
    creds["username"] = username
    creds["password"] = password
    with open("creds.json", "w+") as f:
        json.dump(creds, f)

def changePod(podId):
    try:
        with open("creds.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print('You must configure credentails first!')
    data['podId'] = podId
    try: 
        with open("creds.json", "w+") as w:
            json.dump(data, w)
    except: 
        print('failed to update pod')

def getPod():
    try:
        with open("creds.json", "r") as f:
            settings = json.load(f)
            try:
                return settings['podId']
            except KeyError:
                return 'IPY'
    except FileNotFoundError:
        return 'IPY'

def getCredentials():
    try:
        with open("creds.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def request(method, url):
    creds = getCredentials()
    auth = HTTPBasicAuth(creds["username"], creds["password"])
    
    headers = {
        "Accept": "application/json"
    }
    
    response = requests.request(
        "GET",
        url=url,
        headers=headers,
        auth=auth
    )
    
    return json.loads(response.text)


def get(url):
    creds = getCredentials()
    auth = HTTPBasicAuth(creds["username"], creds["password"])
    
    headers = {
        "Accept": "application/json"
    }
    
    response = requests.request(
        "GET",
        url=url,
        headers=headers,
        auth=auth
    )
    
    return json.loads(response.text)



def post(url, data={}):
    creds = getCredentials()
    auth = HTTPBasicAuth(creds["username"], creds["password"])
    
    headers = {
        "Accepts": "application/json",
        "Content-Type": "application/json"
    }
    
    response = requests.request(
        method="POST",
        url=url,
        json=data,
        headers=headers,
        auth=auth
    )

    print(response)
    
    return json.loads(response.text)


def delete(url):
    creds = getCredentials()
    auth = HTTPBasicAuth(creds["username"], creds["password"])
    
    headers = {
        "Accepts": "application/json",
        "Content-Type": "application/json"
    }
    
    response = requests.request(
        method="DELETE",
        url=url,
        headers=headers,
        auth=auth
    )

    print(response)
    
    return json.loads(response.text)



def getSprints(boardId='470'):
    url = 'https://sofiinc.atlassian.net/rest/agile/1.0/board/{0}/sprint'.format(boardId)
    sprints = request('GET', url)['values']

    for sprint in sprints:
        #if sprint['state'] == 'closed':
        #    continue
        print('{0} - {1} - {2}'.format(sprint['id'], sprint['name'], sprint['state']))


def getSprint(sprintId):
    url = 'https://sofiinc.atlassian.net/rest/agile/1.0/sprint/{0}'.format(sprintId)
    return request('GET', url)

    
def getActiveSprint(boardId):
    url = 'https://sofiinc.atlassian.net/rest/agile/1.0/board/{0}/sprint?state=active'.format(boardId)
    values = request('GET', url)['values']

    if len(values) > 0:
        return values[0]
    else:
        return None
    

def getFutureSprint(boardId):
    url = 'https://sofiinc.atlassian.net/rest/agile/1.0/board/{0}/sprint?state=future'.format(boardId)
    values = request('GET', url)['values']

    if len(values) > 0:
        return values[0]
    else:
        return None


def getIssuesFromBoard(boardId, sprintId):
    url = 'https://sofiinc.atlassian.net/rest/agile/1.0/board/{0}/issue?maxResults=1000&fields=labels&fields=sprint&fields=status&fields=customfield_10004&fields=issuetype&fields=subtasks&jql=sprint%3D{1}'.format(boardId, sprintId)
    #url = 'https://sofiinc.atlassian.net/rest/agile/1.0/board/{0}/issue?maxResults=1000&jql=sprint%3D{1}'.format(boardId, sprintId)
    return request('GET', url)['issues']

    
def main(sprintType):
    
    boardId = '318'
    if sprintType == 'list-sprints':
        getSprints(boardId)
        return
    
    if sprintType == 'active':
        sprint = getActiveSprint(boardId)
    elif sprintType == 'future':
        sprint = getFutureSprint(boardId)
    else:
        sprint = getSprint(sprintType)

    sprintId = sprint['id']

    ipy = Pod('Yixins boba kids')
    ipd = Pod('Dirty Bytes')
    ipv = Pod('Sketchy Pod')
    ipc = Pod('Crypto Pod')

    issues = getIssuesFromBoard(boardId, sprintId)
    for issue in issues:
        if issue['fields']['sprint'] == None:
            continue
        #if issue['fields']['sprint']['state'] != 'active':
        #    continue
        
        labels = issue['fields']['labels']
        
        for label in labels:
            if label == 'IPY':
                ipy.trackIssue(issue)
            if label == 'IPV':
                ipv.trackIssue(issue)
            if label == 'IPD':
                ipd.trackIssue(issue)
            if label == 'IPC':
                ipc.trackIssue(issue)
                
    print(sprint['name'])
    ipy.printSummary()
    ipd.printSummary()
    ipv.printSummary()
    ipc.printSummary()

    #print(len(issues))
    #print(json.dumps(issues[0], sort_keys=True, indent=4, separators=(",", ": ")))


if __name__ == '__main__':
    if (len(sys.argv) > 1 and sys.argv[1] == 'setPod'):
        changePod(sys.argv[2])
    elif (len(sys.argv) == 2):
        main(sys.argv[1])
    elif (len(sys.argv) == 4):
        if (sys.argv[1] == 'init'):
            saveCredentials(sys.argv[2], sys.argv[3])
    else:
        print('Usage: python3 parse_jira.py [active|future|list-sprints|{sprintId}] | init {username} {password} | setPod {podId}')
