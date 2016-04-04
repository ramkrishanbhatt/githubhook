from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import json
import simplejson as sj
import urllib, urllib2


app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('payload')

baseurl="https://iqhomedev.smartappbeta.com/EnterpriseDesktop/api/v1/"


app = Flask(__name__)

@app.route('/',methods=['POST'])
def foo():
   args = parser.parse_args()
   data = json.loads(args['payload'])
   print "Hook call me"
     
   message=format(data["head_commit"]["message"])
   print message 
   timestamp=format(data["head_commit"]["timestamp"])
   print timestamp  
   id=message.split()
   itemid=id[0].split(":")
   print itemid

   lastcommit=getlastcommit(itemid[1])
   appended_commit=lastcommit+"^"+timestamp+"^"+data["after"]
   print appended_commit

   updateitem(itemid[1],appended_commit)

   if message.startswith("Fixed"):
      itemworkflow = getworkflow(itemid[1])
      print itemworkflow
      workItem=getworkflowActivity(workflowid)
      print workItem
      
      acknowlege = moveworkflow("17811")
      print acknowlege

   return test


def updateitem(itemid,commithash):
   url = baseurl +'smartitems/update'
   values = {
            "ItemId":itemid,
            "Metadata":
                {
                 "mdc5d57e962517a413a968b4145fc4707ec":
                  { 
                    "CommitHash":commithash
                  }
                }
         }
   headers = {
            "content-type" : "application/json",
            "accept": "application/json",
             "Authorization" : "key=30202176A1B8E4AB3A042E3660785A767ABEC2194F538594FD25C7A27FCC905F"
           }

   print  url
   req = urllib2.Request(url,data=sj.dumps(values), headers=headers)
   response = urllib2.urlopen(req)

   the_page = sj.loads(response.read())
   print the_page
   return the_page
  
def getlastcommit(id):

   url = baseurl + 'smartitems/GetItemsFieldData'
   values = {             
 		"SmartAppId":"12748436-8128-49a5-a7bb-4f7c1165b515",
 		 "FilterParams":[{
                                  	 "FieldName":"ID",
					 "FilterValue":id}],
		  "Fields":[{
				"FieldName":"CommitHash",
				 "MDCollectionName":"mdc5d57e962517a413a968b4145fc4707ec"}]
	}
   headers = {
            "content-type" : "application/json",
            "accept": "application/json",
             "Authorization" : "key=30202176A1B8E4AB3A042E3660785A767ABEC2194F538594FD25C7A27FCC905F"
           }
   print url
   req = urllib2.Request(url, data=sj.dumps(values), headers=headers)
   response = urllib2.urlopen(req)

   oldcommit = sj.loads(response.read())
   print oldcommit
   mylist = oldcommit.get('Items')
   print mylist
   commithash=mylist[0]["ItemData"].get('mdc5d57e962517a413a968b4145fc4707ec_CommitHash')
   print  commithash

   return commithash

def getworkflow(itemid):
   print "i am in workflow"
   url = baseurl + 'workflow/getworkflows?itemid=' + itemid
   headers = {
                "Authorization" : "key=30202176A1B8E4AB3A042E3660785A767ABEC2194F538594FD25C7A27FCC905F"
           }
   print url
   req = urllib2.Request(url, headers=headers)
   response = urllib2.urlopen(req)
   workflow = sj.loads(response.read())
   print workflow
   return "ok"




def getworflowActivity(workflowId):
   print "i am in activity"
   url = baseurl + 'workflow/getactivities?workflowId=' + workflowId + '&status=4'
   headers = {
                "Authorization" : "key=30202176A1B8E4AB3A042E3660785A767ABEC2194F538594FD25C7A27FCC905F"
           }
   print url
   req = urllib2.Request(url, headers=headers)
   response = urllib2.urlopen(req)
   activity = sj.loads(response.read())
   print activity
   return "ok"

#data need to confirm with prasanna
def moveworkflow(data):
   print " i am move workflow"
   url = baseurl + 'workflow/performaction'
   values = {"WorkItemId":data}
   headers = {
            "content-type" : "application/json",
            "accept": "application/json",
             "Authorization" : "key=30202176A1B8E4AB3A042E3660785A767ABEC2194F538594FD25C7A27FCC905F"
           }
   print url
   req = urllib2.Request(url,data=sj.dumps(values), headers=headers)
   response = urllib2.urlopen(req)

   the_page = sj.loads(response.read())
   print the_page
   return the_page

if __name__ == '__main__':
    app.run(host="10.49.0.249")




