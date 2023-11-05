from flask import (Flask, render_template, request, redirect, session, url_for)
import sqlite3
import time

app = Flask(__name__)
sqldbuser = 'db/userData.db'

@app.route("/")
def index():
  return render_template("register.html", show_noti=False)

#Create the ID for a new user
def generateID():
  max_id = 0
  conn = sqlite3.connect(sqldbuser)
  cursor = conn.cursor()
  sqlcommand = "Select Max(id) from users"
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
  cursor.execute("Insert into users(id, username, email, password, number_of_games, number_of_badges, number_of_friends) values (?,?,?,?,?,?,?)", (id_max, username, email, password, 0,0,0))
  conn.commit()
  conn.close()
  
@app.route("/register", methods=["POST"])
def register():
  username = request.form["username"]
  email = request.form["email"]
  password = request.form["password"]
  
  # Add user to DB
  newid = saveToDB(username, email, password)
  return render_template("register.html", show_noti=True)


# @app.route("/main")
# def main():
#   return render_template("product-page.html")

if __name__ == '__main__':
  app.run(debug=True)