from flask import render_template, request, redirect, url_for
from backend.models import db, User_Info, ParkingLot, ParkingSpot, Reservation
from datetime import datetime

def init_app(app):

    @app.route("/")
    def home():
        return "<h2>Welcome to Vehicle Parking App</h2>"

    @app.route("/login", methods=["GET", "POST"])
    def user_login():
        msg = ""
        if request.method == "POST":
            uname = request.form.get("uname")
            email = request.form.get("email")
            pwd = request.form.get("pwd")

            usr = User_Info.query.filter_by(user_name=uname, email=email, pwd=pwd).first()

            if usr and usr.role == 0:
                return redirect(url_for('admin_dashboard'))
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
                existing_user = User_Info.query.filter(
                    (User_Info.user_name == uname) | (User_Info.email == email)
                ).first()

                if existing_user:
                    message = "User with this username or email already exists."
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
        lots = ParkingLot.query.all()
        bookings = Reservation.query.all()

        # KPI summary (unused here but kept)
        total_spots     = ParkingSpot.query.count()
        occupied_spots  = ParkingSpot.query.filter_by(status='O').count()
        available_spots = total_spots - occupied_spots
        total_revenue   = sum(b.cost for b in bookings)

        # Attach counts and spot lists to each lot
        for lot in lots:
            lot.occupied_count = ParkingSpot.query.filter_by(
                lot_id=lot.id, status='O'
            ).count()
            lot.spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()

        return render_template(
            "admin_dashboard.html",
            users=users,
            lots=lots,
            bookings=bookings,
            total_spots=total_spots,
            occupied_spots=occupied_spots,
            available_spots=available_spots,
            total_revenue=total_revenue
        )

    @app.route("/add_lot", methods=["GET", "POST"])
    def add_lot():
        if request.method == "POST":
            name = request.form.get("name")
            location = request.form.get("location")
            price = float(request.form.get("price"))
            total_spots = int(request.form.get("total_spots"))

            new_lot = ParkingLot(name=name, location=location, price_per_hour=price, total_spots=total_spots)
            db.session.add(new_lot)
            db.session.commit()

            for _ in range(total_spots):
                spot = ParkingSpot(lot_id=new_lot.id, status="A")
                db.session.add(spot)

            db.session.commit()
            return redirect(url_for('admin_dashboard'))

        return render_template("add_lot.html")

    @app.route("/edit_lot/<int:lot_id>", methods=["GET", "POST"])
    def edit_lot(lot_id):
        lot = ParkingLot.query.get_or_404(lot_id)

        if request.method == "POST":
            lot.name = request.form.get("name")
            lot.location = request.form.get("location")
            lot.price_per_hour = float(request.form.get("price"))
            db.session.commit()
            return redirect(url_for('admin_dashboard'))

        return render_template("edit_lot.html", lot=lot)

    @app.route("/delete_lot/<int:lot_id>")
    def delete_lot(lot_id):
        lot = ParkingLot.query.get_or_404(lot_id)
        occupied_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status="O").count()

        if occupied_spots > 0:
            return "<h4 style='color:red;'>Cannot delete — spots are currently occupied.</h4><a href='/admin_dashboard'>Back to Dashboard</a>"

    # Delete available spots and the lot
        ParkingSpot.query.filter_by(lot_id=lot.id).delete()
        db.session.delete(lot)
        db.session.commit()

        return redirect(url_for('admin_dashboard'))

    @app.route("/spots/<int:lot_id>")
    def view_spots(lot_id):
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        return render_template("admin_view_spots.html", spots=spots, lot_id=lot_id)

    @app.route("/bookings")
    def view_bookings():
        bookings = Reservation.query.all()
        return render_template("admin_bookings.html", bookings=bookings)

    @app.route("/spot/<int:spot_id>")
    def spot_detail(spot_id):
        # Look up the spot itself
        spot = ParkingSpot.query.get_or_404(spot_id)
        # (Optional) fetch its latest reservation if you want to show details
        reservation = Reservation.query \
            .filter_by(spot_id=spot.id) \
            .order_by(Reservation.id.desc()) \
            .first()
        return render_template("spot_detail.html",
                               spot=spot,
                               reservation=reservation)
