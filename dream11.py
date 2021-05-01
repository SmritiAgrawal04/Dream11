from flask import Flask, render_template, request, url_for, redirect
from cassandra.cluster import Cluster
import os

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
            session.execute("insert into User (username, password) values (%s, %s);", (request.form["username"], request.form["pass"]))
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
        query= "select password from User where username='"+username+"';"
        password= session.execute(query)[0][0]

        if password == request.form['pass']:
            return render_template('contest.html', username= username)
        else:
             return "Invalid Login"

@app.route('/team',methods = ['POST', 'GET'])
def team():
    if request.method == 'GET':
        match= request.args.get('match')
        # username= request.args.get('username')
        team1, team2= [], []

        if match == 'ashes':
            f= open('teams/ashes.txt')
            teams= f.read().split('----')
            team1, team2= teams[0].split('\n')[1:12], teams[1].split('\n')[2:13]
            
        elif match == 'wisden':
            f= open('teams/wisden.txt')
            teams= f.read().split('----')
            team1, team2= teams[0].split('\n')[1:12], teams[1].split('\n')[2:13]
            
        elif match == 'pataudi':
            f= open('teams/pataudi.txt')
            teams= f.read().split('----')
            team1, team2= teams[0].split('\n')[1:12], teams[1].split('\n')[2:13]

        
        return render_template('team.html', match= match, team1= team1, team2= team2)

    else:
        match= request.form['match']
        username= request.form['username']
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
                query= "update "+match+ " set usernames= usernames + [" +username+ "] where player='"+player+"';"
                session.execute(query)
            else:
                query= "insert into "+match+ "(player, usernames, score) values (%s, %s, %s);" 
                session.execute(query, (player, [], 0))
        return render_template('dashboard.html')

# def dashboard():


if __name__ == '__main__':
   app.run()