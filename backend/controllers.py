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
                return admin_dashboard()  # redirect to admin_dashboard view
            elif usr and usr.role == 1:
                return render_template("user_dashboard.html")
            else:
                msg = "Invalid credentials!!"

        return render_template("login.html", msg=msg)

    @app.route("/register", methods=["GET", "POST"])
    def user_register():
        message = ""

        if request.method == "POST":
            uname = request.form.get("uname")
            email = request.form.get("email")
            pwd = request.form.get("pwd")
            cpwd = request.form.get("cpwd")
            role = int(request.form.get("role"))

            if pwd != cpwd:
                message = "Passwords do not match."
            else:
                existing_user = User_Info.query.filter_by(user_name=uname).first()
                if existing_user:
                    message = "User already exists."
                else:
                    new_user = User_Info(full_name=uname, user_name=uname, email=email, pwd=pwd, role=role)
                    db.session.add(new_user)
                    db.session.commit()
                    message = "You have been registered successfully."
                    return render_template("login.html", msg=message)

        return render_template("register.html", message=message)

    @app.route("/admin_dashboard")
    def admin_dashboard():
        users = User_Info.query.filter_by(role=1).all()
        return render_template("admin_dashboard.html", users=users)

    # @app.route("/list/add/<int:user_id>", methods=["GET", "POST"])
    # def new_list(user_id):
    #     if request.method == "POST":
    #         title = request.form.get("title")
    #         description = request.form.get("description")
    #         list_obj=Lists(title=title, description=description, user_id=user_id)
    #         db.session.add(list_obj)
    #         db.session.commit()
    
    #         return render_template("user_dashboard.html", name=user_info.user_name, lists=user_info.lists)
