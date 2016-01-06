#!/usr/bin/env python
import requests
import sys, base64, urllib2, time
import simplejson as json
from requests.auth import HTTPBasicAuth
from optparse import OptionParser


options = OptionParser()
options.add_option("-c", "--cpcode",dest="cpcode",help="CPCODE to flush", 
		   default=None, type=str)
options.add_option("-u", "--url",dest="url",help="URL to Flush",
		   default=None)
options.add_option("-d", "--debug",dest="debug",help="set in debug mode",
		   default=False,action="store_true")
options.add_option("-U", "--username",dest="user",help="username")
options.add_option("-P", "--password",dest="password",help="password")
(options, args) = options.parse_args()

BASE_URL = 'https://api.ccu.akamai.com/'
USER = options.user 
PASS = options.password
url_to_flush = options.url
debug = options.debug

def purge_url(url):
	data = {'objects' : [ url ]}
	data = json.dumps(data)
	if debug : print data
	headers = {'Content-Type' : 'application/json'}
	u = requests.post(BASE_URL + "ccu/v2/queues/default",
					  auth=HTTPBasicAuth(USER,PASS), data=data, headers=headers)
	if debug: print u , u.status_code
	return u.json()

def purge_cpcode(code):
	data = {'type' : 'cpcode' , 'objects' : code}
	data = json.dumps(data)
	if debug : print data
	headers = {'Content-Type' : 'application/json'}
	u = requests.post(BASE_URL + "ccu/v2/queues/default", 
					  auth=HTTPBasicAuth(USER,PASS), data=data, headers=headers)
	if debug: print u , u.status_code
	return u.json()

if __name__ == "__main__":

	if url_to_flush != None : 
		
		purgestatus = purge_url(url_to_flush)
	
	elif options.cpcode != None:
	
		purgestatus = purge_cpcode(options.cpcode)
	
	else :
		print debug
		print "Please provide a url o cpcode"
		sys.exit(2)

	if debug : print purgestatus 
	if purgestatus['httpStatus'] == 201:
		print "Purge Satus = " , purgestatus['detail'] , "| Estimated Time : ", purgestatus['estimatedSeconds']
	else:
		print "Purge aStus = " , purgestatus['title'] , "| Status Code : "  , purgestatus['httpStatus']

	base64string = base64.encodestring('%s:%s' % (USER,PASS)).replace('\n', '')

	progress = purgestatus["progressUri"]

	if purgestatus["httpStatus"] == 201:
		while True:
			req2 = urllib2.Request("https://api.ccu.akamai.com" + progress)
			req2.add_header("Authorization", "Basic %s" % base64string)
			tmp = urllib2.urlopen(req2).read()
			status = eval(tmp.replace("null","None"))
			if status["purgeStatus"] == "Done":
			  print "purge complete"
			  sys.exit(0)
			else:
			  print time.ctime() + '\tpurge still running...'
			  time.sleep(30)