from flask import (Flask, render_template, request, redirect, session, url_for)
import sqlite3

app = Flask(__name__)
sqldbuser = './db/userData.db'

@app.route("/")
def index():
  return render_template("register.html")

#Create the ID for a new user
def generateID():
  max_id = 0
  conn = sqlite3.connect(sqldbuser)
  cursor = conn.cursor()
  sqlcommand = "Select Max(id) from user"
  cursor.execute(sqlcommand)
  max_id = cursor.fetchone()[0]
  return max_id

# Save the information of new user to DB
def saveToDB(username, email, password):
  id_max = generateID()
  if id_max > 0:
    id_max = id_max + 1
  else: id_max = 1
  print(id_max)
  conn = sqlite3.connect(sqldbuser)
  cursor = conn.cursor()
  # Insert information into DB
  cursor.execute("Insert into user(id, name, email, password) values (?,?,?,?)", (id_max, username, email, password))
  conn.commit()
  conn.close()
  
@app.route("/register", methods=["POST"])
def register():
  username = request.form["username"]
  email = request.form["email"]
  password = request.form["password"]
  
  # Server-side validation
  if not username: username_error = "Username is required"
  if not password: password_error = "Password is required"
  if username_error or password_error:
    return render_template("app_register.html", username_error = username_error, password_error = password_error, registration_success = "")
  
  # Add user to DB
  newid = saveToDB(username, email, password)
  strouput = f'Registered: Username - {username}, Password - {password}'
  registration_success = "Registration Successful! with id = " + str(newid)
  success = registration_success+ ", " + strouput
  return render_template("app_register.html", username_error = "", password_error = "", registration_success = success)



if __name__ == '__main__':
  app.run(debug=True)