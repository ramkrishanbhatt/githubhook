from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import json
import simplejson as sj
import urllib, urllib2

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('payload')

baseurl = "https://iqhomedev.smartappbeta.com/EnterpriseDesktop/api/v1/"

app = Flask(__name__)


@app.route('/', methods=['POST'])
def foo():
    args = parser.parse_args()
    data = json.loads(args['payload'])
    curruntcommits=data["commits"]
    print "Hook call me"

    for commit in curruntcommits:
        if commit["message"].startswith("Fixed") | commit["message"].startswith("In"):
            id = commit["message"].split()
            itemid = id[0].split(":")
            lastcommit = getlastcommit(itemid[1])
            appended_commit = lastcommit + " # " + format(commit["timestamp"]) + " id = " + format(commit["id"])
            print appended_commit
            updateitem(itemid[1], appended_commit)

        if commit["message"].startswith("Fixed"):

            workflowid = getworkflow(itemid[1])

            dataitems = getworkflowActivity(workflowid)
            print dataitems

            wid = dataitems[0].get('Id')
            activityid = dataitems[0].get('ActivityId')
            globaluserid = dataitems[0]['Participant'].get('GlobalId')

            acknowlege = moveworkflow(wid, activityid, globaluserid)
            print acknowlege

    return "Ok"


def updateitem(itemid, commithash):
    url = baseurl + 'smartitems/update'
    values = {
        "ItemId": itemid,
        "Metadata":
            {
                "mdc5d57e962517a413a968b4145fc4707ec":
                    {
                        "CommitHash": commithash
                    }
            }
    }
    headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "Authorization": "key=30202176A1B8E4AB3A042E3660785A767ABEC2194F538594FD25C7A27FCC905F"
    }

    print  url

    req = urllib2.Request(url, data=sj.dumps(values), headers=headers)
    response = urllib2.urlopen(req)

    the_page = sj.loads(response.read())
    print the_page

    return the_page


def getlastcommit(id):
    url = baseurl + 'smartitems/GetItemsFieldData'
    values = {
        "SmartAppId": "12748436-8128-49a5-a7bb-4f7c1165b515",
        "FilterParams": [{
            "FieldName": "ID",
            "FilterValue": id}],
        "Fields": [{
            "FieldName": "CommitHash",
            "MDCollectionName": "mdc5d57e962517a413a968b4145fc4707ec"}]
    }
    headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "Authorization": "key=30202176A1B8E4AB3A042E3660785A767ABEC2194F538594FD25C7A27FCC905F"
    }
    print url

    req = urllib2.Request(url, data=sj.dumps(values), headers=headers)
    response = urllib2.urlopen(req)

    oldcommit = sj.loads(response.read())

    print oldcommit
    mylist = oldcommit.get('Items')
    print mylist

    commithash = mylist[0]["ItemData"].get('mdc5d57e962517a413a968b4145fc4707ec_CommitHash')
    print  commithash

    return commithash


def getworkflow(itemid):
    print "i am in workflow"
    url = baseurl + 'workflow/getworkflows?itemid=' + itemid
    headers = {
        "Authorization": "key=30202176A1B8E4AB3A042E3660785A767ABEC2194F538594FD25C7A27FCC905F"
    }
    print url
    req = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(req)
    workflow = sj.loads(response.read())
    print workflow
    workflowid = workflow[0]['Activities'][0].get('WorkflowId')
    print workflowid
    return workflowid


def getworkflowActivity(workflowId):
    print "i am in activity"
    url = baseurl + 'workflow/getactivities?workflowId=' + str(workflowId) + '&status=3'
    headers = {
        "Authorization": "key=30202176A1B8E4AB3A042E3660785A767ABEC2194F538594FD25C7A27FCC905F"
    }

    print url

    req = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(req)
    activity = sj.loads(response.read())
    workitems = activity[0].get('WorkItems')
    return workitems



def moveworkflow(workitemid, activityid, userid):
    print " i am move workflow"
    url = baseurl + 'workflow/performaction'
    values = {
        "WorkItemId": workitemid,
        "ActivityId": activityid,
        "Action": "Acknowledge",
        "GlobalUserId": userid

    }
    headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "Authorization": "key=30202176A1B8E4AB3A042E3660785A767ABEC2194F538594FD25C7A27FCC905F"
    }

    print url
    print values

    req = urllib2.Request(url, data=sj.dumps(values), headers=headers)
    response = urllib2.urlopen(req)

    the_page = sj.loads(response.read())
    print the_page
    return the_page


if __name__ == '__main__':
    app.run()
