import requests
import json

url = "http://127.0.0.1:5000/match_updates"

def getUpdates():
	print("-----------------------------------------------------------------------")
	match = input("Enter Match Name: ")
	player = input("Enter Player Name: ")
	score = input("Enter score to be added: ")
	sendUpdates(match, player, score)

def sendUpdates(match, player, score):
	updates = {'match':match, 'player':player, 'score':score}
	result = requests.get(url, params=updates).json()
	return result

if '__name__ == __main__':
	while(1):
		getUpdates()