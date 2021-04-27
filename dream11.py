from flask import Flask, render_template, request, url_for, redirect
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
        return render_template('login.html')

@app.route('/login',methods = ['POST', 'GET']) 
def login(): 
    if request.method == 'GET':
        return render_template('login.html')
    else:
        # match credentials entered
        return render_template('contest.html')

@app.route('/team')
def team():
   return render_template('team.html')

if __name__ == '__main__':
   app.run()