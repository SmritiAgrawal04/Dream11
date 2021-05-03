from flask import Flask, render_template, request, url_for, redirect
from flask import jsonify
from cassandra.cluster import Cluster
import os
from cassandra.query import tuple_factory
import threading 


app = Flask(__name__)

urls = ["http://127.0.0.1:5000/getLoad", "http://127.0.0.1:5001/getLoad", "http://127.0.0.1:5002/getLoad"]
indexurl = ["http://127.0.0.1:5000/", "http://127.0.0.1:5001/", "http://127.0.0.1:5002/"]

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


def redirectRequest(url):
    return redirect(url)

@app.route('/', methods = ['POST', 'GET'])
def loadBalancer():
    load = getLoad()
    load.sort(key = lambda x: x[0])
    print("Load in sorted order....", load)
    return redirectRequest(load[0][2])

def runServer():
    pass

def runClient():
    pass

if __name__ == '__main__':  
    app.run(port = 5003)