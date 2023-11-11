from flask import Flask, render_template, request, session, url_for, redirect
import sqlite3
app = Flask(__name__)
app.secret_key = "FelixPham"
sqldbname = "db/game-db.db"

@app.route('/')
def index():
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    cursor.execute("Select * from GameDB")
    data = cursor.fetchall()
    conn.close()
    return render_template(
        'cart.html',
)



if __name__ == '__main__':
    app.run(debug=True)



