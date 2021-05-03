from flask import Flask, render_template, request, url_for, redirect
from flask import jsonify
from cassandra.cluster import Cluster
import os
import requests
from cassandra.query import tuple_factory
import threading 
import time


app = Flask(__name__)

urls = ["http://127.0.0.1:5000/getLoad", "http://127.0.0.1:5001/getLoad", "http://127.0.0.1:5002/getLoad"]
indexurl = ["http://127.0.0.1:5000/", "http://127.0.0.1:5001/", "http://127.0.0.1:5002/"]
alive = {}
services_dict = {}


def getLoad():
	global urls
	load = []
	i = 0
	for url in urls:
		updates = {}
		result = requests.get(url, params=updates).json()
		load.append([result['cpu'],result['memory'], indexurl[i]])
		i+=1

	return load

@app.route('/heartbeat',methods = ['POST', 'GET'])
def heartBeat():
	# print('inside heartbeat at master')
	global services_dict
	req = request.json
	service_id = int(req['service_id'])

	# print("received heartbeat from -------", service_id)
	if(service_id in services_dict.keys()):
		services_dict[service_id]+=1
	else:
		services_dict[service_id]=1
		alive[service_id]=1

	# print("updated in map for id ---", service_id)
	return jsonify({'status':'success'})

def identify_services_status():
	while(1):
		global services_dict
		time.sleep(10)
		# print('Service_dict is ',services_dict)
		for s_id in services_dict.keys():
			# print('print s_id ',s_id)
			if services_dict[s_id] == 0 and alive[s_id] == 1:
				print('server ',s_id,' failed ')
				alive[s_id] = 0
				del urls[s_id]
				del indexurl[s_id]

			else:
				services_dict[s_id] = 0


def redirectRequest(url):
	return redirect(url)
	



@app.route('/', methods = ['POST', 'GET'])
def loadBalancer():
	load = getLoad()
	load.sort(key = lambda x: x[0])
	print("Load in sorted order....", load)
	return redirectRequest(load[0][2])

def runServer():
	app.run(port = 5003,debug=False)
	

def runClient():
	pass

if __name__ == '__main__':  
	thread2 = threading.Thread(target = identify_services_status)
	thread2.start()
	thread3 = threading.Thread(target = runServer)
	thread3.start()
	
