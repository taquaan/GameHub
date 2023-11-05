from flask import (Flask, render_template, request, redirect, session, url_for)
import sqlite3

app = Flask(__name__)
sqldbuser = 'db/userData.db'
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'

@app.route("/")
def index():
  return render_template("product-page.html")

@app.route("/login", methods=["GET","POST"])
def login():
  session['logged_in'] = False
  if request.method == 'POST':
    username = request.form["username"]
    password = request.form["password"]
    if check_exists(username,password):
      session['username'] = username
      session['logged_in'] = True
    return render_template('product-page.html')
  return render_template('login.html')

# Save the information of new user to DB
def check_exists(username, password):
  result = False;
  conn = sqlite3.connect(sqldbuser)
  cursor = conn.cursor()
  sqlcommand="Select * from users where username = '"+username+"' or email = '"+username+"' and password = '"+password+"'"
  cursor.execute(sqlcommand)
  data=cursor.fetchall()
  print(type(data))
  if len(data)>0:
    result=True
  conn.close()
  return result;

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return render_template('login.html') 

if __name__ == '__main__':
  app.run(debug=True)