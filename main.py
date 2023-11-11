from flask import (Flask, render_template, request, redirect, session, url_for)
import sqlite3

app = Flask(__name__)
sqldbuser = 'db/userData.db'
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'

@app.route("/")
def index():
  return render_template("product-page.html")



# LOGIN PAGE FUNCTION
@app.route("/login", methods=["GET","POST"])
def login():
  if request.method == 'POST':
    username = request.form["username"]
    password = request.form["password"]
    if check_exists(username,password):
      session['username'] = username
      session['logged_in'] = True
    return render_template('product-page.html')
  return render_template('login.html')

# Check if the input data is correct
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
  return result

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return render_template('login.html') 



# REGISTER FUNCTION
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
  
@app.route("/register", methods=["GET","POST"])
def register():
  session['logged_in'] == False
  if request.method == "POST":
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"] 
    # Add user to DB
    newid = saveToDB(username, email, password)
    # Set the header to logged_in
    session['logged_in'] = True
    # Show successfully register notification
    return render_template("register.html", success=True)
  return render_template("register.html", success=False)



# FUNCTION FOR ADMIN PAGE
# Load data form UserDB
def load_data_from_user(username):
  if username != "":
    # Trỏ tới UserDB
    conn = sqlite3.connect(sqldbuser)
    cursor = conn.cursor()
    sqlcommand = ("Select * from users where username like '%" + username + "%' or username like '%" + username + "%'")
    cursor.execute(sqlcommand)
    data = cursor.fetchall()
    conn.close()
    # Kiểm tra xem user có tồn tại không và trả lại dữ liệu
    if len(data) == 0:
      no_user_message = "No user name '" + username + "'"
      return data, no_user_message
    else:
      return data, None
  
# admin page
@app.route("/admin")
def admin():
  logged_in = session.get('logged_in', False)
  return render_template("admin.html")

# admin search user funtion
@app.route("/searchUser", methods=['POST'])
def searchUser():
  delete_success = False
  search_user = request.form['SearchUser']
  user_table, output_message = load_data_from_user(search_user)
  return render_template("admin.html", delete_success=delete_success, 
        search_user=search_user,
        table=user_table,
        output_message=output_message if search_user else None
        )

# Delete User from UserDB
def delete_user_from_db(user_id):
  if user_id != "":
    # Trỏ tới UserDB
    conn = sqlite3.connect(sqldbuser)
    cursor = conn.cursor()
    sqlcommand = ("delete from users where id = " + user_id)
    cursor.execute(sqlcommand)
    data = cursor.fetchall()
    conn.commit()
    conn.close()
    return "User deleted successfully"

# Load page delete user
@app.route('/deleteUser', methods=['POST'])
def delete_user():
  user_id = request.form['user_id']
  delete_result = delete_user_from_db(user_id)
  delete_success = True
  return render_template("admin.html", delete_success = delete_success)

if __name__ == '__main__':
  app.run(debug=True)