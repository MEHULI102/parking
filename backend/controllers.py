from flask import Flask 
from flask import current_app as app
from flask import render_template


@app.route("/")
def home():
  return "<h2>Welcome to Kanban app</h2>"

@app.route("/login")
def user_login():
  return render_template("login.html")

@app.route("/register")
def user_register():
  return render_template("register.html")
