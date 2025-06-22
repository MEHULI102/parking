from flask import render_template, request
from backend.models import db, User_Info

def init_app(app):

    @app.route("/")
    def home():
        return "<h2>Welcome to Kanban app</h2>"

    @app.route("/login", methods=["GET", "POST"])
    def user_login():
        msg = ""
        if request.method == "POST":
            uname = request.form.get("uname")
            email = request.form.get("email")
            pwd = request.form.get("pwd")

            usr = User_Info.query.filter_by(user_name=uname, email=email, pwd=pwd).first()

            if usr and usr.role == 0:
                return render_template("admin_dashboard.html")
            elif usr and usr.role == 1:
                return render_template("user_dashboard.html")
            else:
                msg = "Invalid credentials!!"

        return render_template("login.html", msg=msg)

    @app.route("/register", methods=["GET", "POST"])
    def user_register():
        message = ""  # Initialize message at the start

        if request.method == "POST":
            uname = request.form.get("uname")
            email = request.form.get("email")
            pwd = request.form.get("pwd")
            cpwd = request.form.get("cpwd")

            if pwd != cpwd:
                message = "Passwords do not match."
            else:
                existing_user = User_Info.query.filter_by(user_name=uname).first()
                if existing_user:
                    message = "User already exists."
                else:
                    new_user = User_Info(full_name=uname, user_name=uname, email=email, pwd=pwd, role=1)
                    db.session.add(new_user)
                    db.session.commit()
                    message = "You have been registered successfully."
                    return render_template("login.html", msg=message)  # fixed typo

        return render_template("register.html", message=message)