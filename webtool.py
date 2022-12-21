import json
import urllib2
from datetime import datetime
import re

import simplejson as sj
from flask import Flask
from flask_restful import reqparse, Api

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('payload')

baseurl = 
accessToken = 

app.route('/', methods=['POST'])
def foo():
    args = parser.parse_args()
    data = json.loads(args['payload'])
    curruntcommits = data["commits"]
    print "Hook call me"

    for commit in curruntcommits:
        if commit["message"].startswith("Fixed") | commit["message"].startswith("In"):
            message = commit["message"]
            guid = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.I).findall(message)
            itemguid = guid[0].encode('ascii', 'ignore')

            print itemguid

            lastcommit = getlastcommit(itemguid)
            timecommit = commit['timestamp']
            stringtime = timecommit.encode('ascii', 'ignore')
            mtimes = datetime.strptime(stringtime, '%Y-%m-%dT%H:%M:%S+00:00')
            commiturl = commit['url']
            appended_commit = lastcommit + mtimes.strftime('  %d/%m/%Y %I:%M %p ') + "<a  href=" + commiturl + ">" + \
                              commit['id'] + "</a>"
            print appended_commit

            print commiturl
            updateitem(itemguid, appended_commit)

        if commit["message"].startswith("Fixed"):
            workflowid = getworkflow(itemguid)

            dataitems = getworkflowActivity(workflowid)
            print dataitems

            wid = dataitems[0].get('Id')
            activityid = dataitems[0].get('ActivityId')
            globaluserid = dataitems[0]['Participant'].get('GlobalId')

            acknowlege = moveworkflow(wid, activityid, globaluserid)
            print acknowlege

    return "Ok"


def updateitem(itemguid, appended_commit):
    url = baseurl + 'smartitems/update'
    values = {
        "ItemId": itemguid,
        "Metadata":
            {
                "mdc5d57e962517a413a968b4145fc4707ec":
                    {
                        "flddc327ebe": appended_commit
                    }
            }
    }
    headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "Authorization": accessToken
    }

    print  url

    req = urllib2.Request(url, data=sj.dumps(values), headers=headers)
    response = urllib2.urlopen(req)

    the_page = sj.loads(response.read())
    print the_page

    return the_page


def getlastcommit(itemguid):
    url = baseurl + 'smartitems/GetItemsFieldData'
    values = {
        "SmartAppId": "12748436-8128-49a5-a7bb-4f7c1165b515",
        "FilterParams": [{
            "FieldName": "ID",
            "FilterValue": itemguid}],
        "Fields": [{
            "FieldName": "flddc327ebe",
            "MDCollectionName": "mdc5d57e962517a413a968b4145fc4707ec"}]
    }
    headers = {
        "content-type": "application/json",
        "accept": "application/json",
        "Authorization": accessToken
    }
    print url

    req = urllib2.Request(url, data=sj.dumps(values), headers=headers)
    response = urllib2.urlopen(req)

    oldcommit = sj.loads(response.read())

    print oldcommit
    mylist = oldcommit.get('Items')
    print mylist

    commithash = mylist[0]['ItemData'].get('mdc5d57e962517a413a968b4145fc4707ec_ResolutionNotes')
    if not commithash:
        commithash = " "
        return commithash
    else:
        return commithash


def getworkflow(itemguid):
    print "i am in workflow"
    url = baseurl + 'workflow/getworkflows?itemid=' + itemguid
    headers = {
        "Authorization": accessToken
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
        "Authorization": accessToken
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
        "Authorization": accessToken
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

    
    @app.before_request
def before_req():
    """
    To log the request for each and every transaction
    :return: Noting
    """
    root.warning('****--------------- %s ----------------****', str(time.asctime(time.localtime(time.time()))))
    root.warning('------------------Request--------------------')
    root.info(request.json)


@app.after_request
def after_request(response):
    """
    To log response of each and every request
    :param response: Response of the request
    :return: Response of the request
    """
    if request.method == 'OPTIONS' or request.method == 'GET' or request.method == 'POST' or request.method == 'PUT' or request.method == 'DELETE':
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, GET, POST, PUT, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authentication'
    root.info(response.json)
    root.warning('------------------Response--------------------')
    root.warning('****--------------- %s ----------------****', str(time.asctime(time.localtime(time.time()))))
    return response
