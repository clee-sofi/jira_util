import requests
from requests.auth import HTTPBasicAuth
import json
import sys


def saveCredentials(username, password):
    creds = {}
    creds["username"] = username
    creds["password"] = password
    with open("creds.json", "w+") as f:
        json.dump(creds, f)


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
        url,
        headers=headers,
        auth=auth
    )
    
    return json.loads(response.text)


def getIssueId(key):
    url = 'https://sofiinc.atlassian.net/rest/agile/1.0/issue/{0}?fields=id'.format(key)
    response = request('GET', url)

    return response['id']


def getBranches(issue_id):
    url = 'https://sofiinc.atlassian.net/rest/dev-status/1.0/issue/detail?issueId={0}&applicationType=bitbucket&dataType=pullrequest'.format(issue_id)
    response = request('GET', url)

    branches = []
    for detail in response['detail']:
        for pullRequest in detail['pullRequests']:
            if pullRequest['status'] == 'OPEN' or pullRequest['status'] == 'MERGED':
                branches.append(pullRequest['source']['url'])

    return branches


def getServiceName(repoName):
    if repoName == 'avro-schemas':
        return None
    if repoName == 'apex-client':
        return None
    if repoName == 'coinbase-trading-engine':
        return 'coinbase-trading'
    if repoName == 'instinet-trading-engine':
        return 'instinet-trading'
    if repoName == 'kafka-kastle':
        return 'kafka-kastle-migrate'
    if repoName == 'trading-client':
        return None
    if repoName == 'wealth-advisor':
        return 'advisor'
    if repoName == 'wealth-db':
        return 'wealth-dbmigrate'
    
    return repoName


def main(ticket_id):
    url = 'https://bitbucket.org/sofiinc/'
    issue_id = getIssueId(ticket_id)
    branches = getBranches(issue_id)

    print('services:')

    for branch in branches:
        repositoryName = branch[len(url):branch.find('/branch/')]
        branchName = branch[branch.find('feature%2F') + len('feature%2F'):len(branch)]
        serviceName = getServiceName(repositoryName)

        if serviceName is None:
            continue
        
        print('  ' + serviceName + ':')
        print('    image: registry.sofi.com/' + repositoryName + ':' + branchName)

    print('version: "2.1"')


if __name__ == '__main__':
    if (len(sys.argv) == 2):
        main(sys.argv[1])
    elif (len(sys.argv) == 4):
        if (sys.argv[1] == 'init'):
            saveCredentials(sys.argv[2], sys.argv[3])
    else:
        print('Usage: python3 get_ticket.py [SOFI-#####] | init {username} {api_key}')
