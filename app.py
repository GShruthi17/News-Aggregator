from flask import Flask,request,render_template,url_for,session,redirect,flash
from flask_session import Session
import mysql.connector
import secrets


secret_key = secrets.token_hex(16)

app=Flask(__name__)
app.config['SESSION_TYPE']='filesystem'
app.config['SECRET_KEY'] = secret_key
mydb=mysql.connector.connect(user='root',
                             password='Vanka@143',
                             port=3306,
                             db='internship')
Session(app)
from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key='343a34c324de4f32892c6a8a0085bad8')

@app.route('/',methods=['GET','POST'])
def register():
    if session.get('users'):
        return redirect(url_for('login'))
    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        email=request.form['email']
        cursor=mydb.cursor(buffered=True)
        query="insert into users (username,email,password) values(%s,%s,%s)"
        cursor.execute(query,[username,email,password])
        mydb.commit()
        cursor.close()
        flash("Registered Successfully")
        return redirect(url_for('login'))
    return render_template('registration.html')
@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('users'):
        return redirect(url_for('index'))
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        cursor=mydb.cursor(buffered=True)
        query='select count(*) from users where username=%s'
        cursor.execute(query,(username,))
        user_count=cursor.fetchone()[0]
        if user_count==0:
            flash("User doesn't exist")
            return render_template('login.html')
        else:
            cursor=mydb.cursor(buffered=True)
            query="select count(*) from users where username=%s and password=%s"
            cursor.execute(query,(username,password))
            p_count=cursor.fetchone()[0]
            if p_count==0:
                flash('Invalid password')
                return render_template('login.html')
            else:
                session['users']=username
                return redirect(url_for('index'))
    return render_template('login.html')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_query = request.form['query']
        top_headlines = newsapi.get_top_headlines(q=user_query,
                                                  language='en',
                                                  country='us')
        top_headlines = top_headlines['articles'][:10]
        all_articles = newsapi.get_everything(q=user_query,
                                              language='en',
                                              sort_by='relevancy')
        all_articles = all_articles['articles'][:10]
        return render_template('index.html', user_query=user_query, top_headlines=top_headlines, all_articles=all_articles)
    
    return render_template('index.html')
@app.route('/logout')
def logout():
    if session.get('users'):
        session.pop('users')
        return redirect(url_for('login'))
    else:
        flash('Already logged out')
        return redirect(url_for('login'))

app.run(use_reloader=True,debug=True)

