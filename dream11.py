from flask import Flask, render_template, request, url_for, redirect
from flask import jsonify
import requests as rq
from cassandra.cluster import Cluster
import os
from cassandra.query import tuple_factory
import threading 
import sys
import time
import psutil

app = Flask(__name__)

@app.route('/')
def index():
   return render_template('index.html')

@app.route('/register',methods = ['POST', 'GET']) 
def register(): 
    if request.method == 'GET':
        return render_template('register.html')
    else:
        # store credentials of new user
        try:
            clstr=Cluster()
            session=clstr.connect('userdb')
            session.execute("insert into User (username, password, matches) values (%s, %s, %s);", (request.form["username"], request.form["pass"], ''))
        except: 
            print ("Invalid Registration!")
        
        return render_template('login.html')

@app.route('/login',methods = ['POST', 'GET']) 
def login(): 
	if request.method == 'GET':
		return render_template('login.html')
	else:
		# match credentials entered
		username= request.form['username']


        clstr=Cluster()
        session=clstr.connect('userdb')
        query= "select password, matches from User where username='"+username+"';"
        result= session.execute(query)
        password, matches= result.one()[0], result.one()[1]
        print ("$$$$$$$$$", matches, "$$$$$$$$$$")


		if not password :
			return render_template('login.html',Message='Invalid User!!')


        if password == request.form['pass']:
            return render_template('contest.html', username= username, matches= matches)
        else:
             return render_template('login.html',Message='Invalid User!!')


def split_NameType(team1_NameType, team2_NameType):
	team1, team2, team1type, team2type= [], [], [], []
	for player in team1_NameType:
		name, player_type= player.split(':')
		team1.append(name)
		team1type.append(player_type)

	for player in team2_NameType:
		name, player_type= player.split(':')
		team2.append(name)
		team2type.append(player_type)

	return team1, team2, team1type, team2type

@app.route('/team',methods = ['POST', 'GET'])
def team():

    if request.method == 'GET':
        match= request.args.get('match')
        user_n= request.args.get('username')
        team1, team2, team1type, team2type= [], [], [], []

        if match == 'ashes':
            f= open('teams/ashes.txt')
            teams= f.read().split('----')
            team1_NameType, team2_NameType= teams[0].split('\n')[1:12], teams[1].split('\n')[2:13]
            team1, team2, team1type, team2type= split_NameType(team1_NameType, team2_NameType)
            
        elif match == 'wisden':
            f= open('teams/wisden.txt')
            teams= f.read().split('----')
            team1_NameType, team2_NameType= teams[0].split('\n')[1:12], teams[1].split('\n')[2:13]
            team1, team2, team1type, team2type= split_NameType(team1_NameType, team2_NameType)
            
        elif match == 'pataudi':
            f= open('teams/pataudi.txt')
            teams= f.read().split('----')
            team1_NameType, team2_NameType= teams[0].split('\n')[1:12], teams[1].split('\n')[2:13]
            team1, team2, team1type, team2type= split_NameType(team1_NameType, team2_NameType)


        # save the match name corresponding to the user in the database
        clstr=Cluster()
        session=clstr.connect('userdb')
        query = "select matches from User where username='"+user_n+"';"
        curr_matches = session.execute(query).one()[0]
        print ("**********Cur matches****", curr_matches)
        if curr_matches == '':
            updated_matches= match
        else:
            updated_matches = curr_matches+'|'+match

        print('new Matches is .... ',updated_matches)
        query= "update User SET matches = '" +updated_matches+ "' where username='"+user_n+"';"
        session.execute(query)

       

        return render_template('team.html', match= match, team1= team1, team2= team2, team1type= team1type, team2type= team2type, username=user_n)

    else:
        match= request.form['match']
        username= request.form['username']
        
        print('got match .... ',match)
        players= []
        for i in range (1, 23):
            try:
                players.append (request.form[str(i)])
            except:
                pass

        # save the username corresponding to each player in the database
        clstr=Cluster()
        session=clstr.connect('playermapping')
        
       
        for player in players:
            query= "select usernames from "+match+ " where player='"+player+"';"
            result= session.execute(query)
            print ("************************",result)
            if result:
                # enter into DB
                print('got username .... ',username)
                print('got player .... ',player)
                #extract
                query= "select usernames from "+match+ " where player='"+player+"';"
                user_list = session.execute(query)[0][0]
                print("users.......",user_list)
                user_list+="|"+username
                query= "update "+match+ " SET usernames = '" +user_list+ "' where player='"+player+"';"
                print("query..........",query)
                session.execute(query)
            else:
                query= "insert into "+match+ "(player, usernames, score) values (%s, %s, %s);" 
                session.execute(query, (player,username, 0))
        
        #enter username in userScore cluster
        user_session = clstr.connect('userscore')
        print('-----------------------',match)
        print('-----------------------',username)
        query = "insert into "+match+ "(username, score) values (%s, %s);"
        user_session.execute(query,(username,0))

        return redirect(url_for('dashboard',match=match))       
        # return render_template('dashboard.html',all_users=all_users,top_players=top_players)


# def dashboard():
def updateUser(user_list, match, score):
	clstr = Cluster()
	user_session=clstr.connect('userscore')
	for user in user_list :
		
		query = "select score from "+match+" where username='"+user+"';"
		curr_score = user_session.execute(query).one()[0]
		updated_score = curr_score+score
		print('new Score is .... ',updated_score)
		query = "update "+match+" set score ="+str(updated_score)+" where username = '"+user+"';"
		user_session.execute(query)
	
		

@app.route('/match_updates',methods = ['POST', 'GET']) 
def match_updates():
	print("inside match updates")
	data = request.args
	match = data['match']
	player = data['player']
	score_type = data['score']

	if(score_type == 'six'):
		score = 6
	elif(score_type == 'four'):
		score = 4
	elif(score_type == 'wicket'):
		score = 2
	
	# find all users for the player
	print("player is ",player)
	clstr=Cluster()
	session=clstr.connect('playermapping')
	query= "select usernames from "+match+ " where player='"+player+"';"
	user_list = session.execute(query).one()[0]
	print("users are:    ",user_list)
	user_list = user_list.split('|')
	print("list of users:    ",user_list)

	#update scores
	updateUser(user_list,match,score)
	return jsonify({'status':'done'})
	
@app.route('/dashboard',methods = ['POST', 'GET'])
def dashboard():

    if request.method == 'GET':
        match = request.args.get('match')
        
        #get all user details
        print("inside dashboard..........")
        clstr = Cluster()
        user_session=clstr.connect('userscore')
        user_session.row_factory = tuple_factory
        query = "select * from "+match+";"
        user_details = user_session.execute(query) 
        all_users=[]
        for user in user_details:
            # print(user)
            user_n = user[0]
            user_s = user[1]
            all_users.append([user_n,user_s])
        all_users.sort(key = lambda x: x[1],reverse = True)
        print("all_users...............",all_users)
        top_players = min(3,len(all_users))
        print("Inside dashboard...")
        print("all_users: ",all_users)
        return render_template('dashboard.html',all_users=all_users,top_players=top_players)
     

@app.route('/logout',methods = ['POST', 'GET'])
def logout():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return render_template('logout.html')


@app.route('/getLoad',methods = ['POST', 'GET'])
def getLoad():
	memory = psutil.virtual_memory().percent
	cpu = psutil.cpu_percent()
	req = {'memory':memory,'cpu':cpu}
	return jsonify(req)

def heartBeat(server_id):
	server_url = 'http://127.0.0.1:5003/heartbeat'
	while True:	
		# print('sending heartbeat')
		# print("heartbeat sent -- ", service_id)

        r = {'service_id':str(server_id)}
        rsp = rq.post(server_url, json = r)
        print("hitting again")
        time.sleep(2)



if __name__ == '__main__':
	server_id = sys.argv[1]
	slave_port = sys.argv[2]
	print(server_id)
	thread1 = threading.Thread(target = heartBeat,args=(server_id,))
	thread1.start()    
	thread2 = threading.Thread(target = runServer,args=(slave_port,))
	thread2.start()   
	