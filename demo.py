from flask import (Flask, render_template, request, redirect, session, url_for)
app:Flask = Flask(__name__)
sqldbname = ''

@app.route("/")
def demo():
  return render_template("demo.html")

if __name__ == '__main__':
  app.run(debug=True)