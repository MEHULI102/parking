from flask import render_template, request, redirect, url_for, flash, session
from backend.models import db, User_Info, ParkingLot, ParkingSpot, Reservation
from datetime import datetime

def init_app(app):
    # ✅ Default admin creation block
    with app.app_context():
        admin = User_Info.query.filter_by(role=0).first()
        if not admin:
            default_admin = User_Info(
                full_name="Admin",
                user_name="admin",
                email="admin@parking.com",
                pwd="admin123",
                role=0
            )
            db.session.add(default_admin)
            db.session.commit()
            

    @app.route("/")
    def home():
        return "<h2>Welcome to Vehicle Parking App</h2>"

    @app.route("/login", methods=["GET", "POST"])
    def user_login():
        msg = ""
        if request.method == "POST":
          
            email = request.form.get("email")
            pwd = request.form.get("pwd")

            usr = User_Info.query.filter_by( email=email, pwd=pwd).first()

            if usr and usr.role == 0:
                session['admin_id'] = usr.id
                return redirect(url_for('admin_dashboard'))
            elif usr and usr.role == 1:
                session['user_id'] = usr.id
                reservations = Reservation.query.filter_by(user_id=usr.id).all()
                total_bookings = len(reservations)
                active_bookings = sum(1 for r in reservations if r.spot.status == 'O')
                return render_template(
                    "user_dashboard.html",
                    user=usr,
                    reservations=reservations,
                    total_bookings=total_bookings,
                    active_bookings=active_bookings,
                    results=[],
                    query=""
                )
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
        return render_template("admin_spot_detail.html",
                               spot=spot,
                               reservation=reservation)
    
    @app.route("/delete_booking/<int:booking_id>")
    def delete_booking(booking_id):
        booking = Reservation.query.get_or_404(booking_id)
        spot = ParkingSpot.query.get(booking.spot_id)
        spot.status = "A"
        db.session.delete(booking)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    @app.route("/view_spots/<int:lot_id>")
    def view_spots(lot_id):
        lot = ParkingLot.query.get_or_404(lot_id)
        spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        return render_template("view_spots.html", lot=lot, spots=spots)

    @app.route("/view_users")
    def view_users():
        users = User_Info.query.filter_by(role=1).all()
        return render_template("admin_view_users.html", users=users)

    @app.route('/summary')
    def admin_summary():
        lots = ParkingLot.query.all()
        lot_names = []
        revenues = []

        for lot in lots:
        # Get spot IDs for this lot
            spot_ids = [s.id for s in ParkingSpot.query.filter_by(lot_id=lot.id).all()]
        
            if spot_ids:
                lot_revenue = sum(r.cost for r in Reservation.query.filter(Reservation.spot_id.in_(spot_ids)).all())
            else:
                lot_revenue = 0
        
            lot_names.append(lot.name)
            revenues.append(lot_revenue)

        total_spots = ParkingSpot.query.count()
        occupied_count = ParkingSpot.query.filter_by(status='O').count()
        available_count = total_spots - occupied_count

        return render_template(
            'admin_summary.html',
            lot_names=lot_names,
            revenues=revenues,
            occupied_count=occupied_count,
            available_count=available_count
        )

    @app.route("/search", methods=["GET"])
    def admin_search():
        query = request.args.get("q", "")

        users = User_Info.query.filter(User_Info.id.like(f"%{query}%")).all()
        lots_by_name = ParkingLot.query.filter(ParkingLot.name.like(f"%{query}%")).all()
        lots_by_location = ParkingLot.query.filter(ParkingLot.location.like(f"%{query}%")).all()
        spots = ParkingSpot.query.filter(ParkingSpot.id.like(f"%{query}%")).all()

        results = {
            "users": users,
            "lots_by_name": lots_by_name,
            "lots_by_location": lots_by_location,
            "spots": spots
        }

        return render_template("admin_search.html", query=query, results=results)

    @app.route("/get_suggestions")
    def get_suggestions():
        query = request.args.get("q", "")

        suggestions = []

        # Fetch IDs and names for suggestions
        user_ids = [str(u.id) for u in User_Info.query.filter(User_Info.id.like(f"%{query}%")).all()]
        lot_names = [l.name for l in ParkingLot.query.filter(ParkingLot.name.like(f"%{query}%")).all()]
        lot_locations = [l.location for l in ParkingLot.query.filter(ParkingLot.location.like(f"%{query}%")).all()]
        spot_ids = [str(s.id) for s in ParkingSpot.query.filter(ParkingSpot.id.like(f"%{query}%")).all()]

        suggestions.extend(user_ids)
        suggestions.extend(lot_names)
        suggestions.extend(lot_locations)
        suggestions.extend(spot_ids)

        return {"suggestions": suggestions}

    @app.route('/edit_profile', methods=['GET', 'POST'])
    def edit_profile():
        if 'admin_id' not in session:
            return redirect('/login')

        admin = User_Info.query.get(session['admin_id'])

        if request.method == 'POST':
            admin.full_name = request.form['full_name']
            admin.email = request.form['email']
            admin.phone = request.form['phone']
            admin.location = request.form['location']
            admin.address = request.form['address']
            admin.pin_code = request.form['pin_code']

            password = request.form['password']
            if password:
                admin.pwd = password

            db.session.commit()
            flash('Admin profile updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))

        return render_template('admin_edit_profile.html', admin=admin)


    @app.route('/user_summary')
    def user_summary():
        if 'user_id' not in session:
            return redirect('/login')

        user = User_Info.query.get(session['user_id'])

        results = db.session.query(
            ParkingLot.location,
            db.func.count(Reservation.id)
        ).select_from(ParkingLot)\
        .join(ParkingSpot, ParkingSpot.lot_id == ParkingLot.id)\
        .join(Reservation, Reservation.spot_id == ParkingSpot.id)\
        .group_by(ParkingLot.location).all()

        labels = [r[0] for r in results]
        data = [r[1] for r in results]

        return render_template('user_summary.html', user=user, labels=labels, data=data)
    @app.route("/user_dashboard")
    def user_dashboard():
        if 'user_id' not in session:
            return redirect('/login')

        user = User_Info.query.get(session['user_id'])
        reservations = Reservation.query.filter_by(user_id=user.id).all()
        total_bookings = len(reservations)
        active_bookings = sum(1 for r in reservations if r.spot.status == 'O')

        return render_template(
            "user_dashboard.html",
            user=user,
            reservations=reservations,
            total_bookings=total_bookings,
            active_bookings=active_bookings,
            results=[],
            query=""
        )

    @app.route('/user_edit_profile', methods=['GET', 'POST'])
    def user_edit_profile():
        if 'user_id' not in session:
            return redirect('/login')

        user = User_Info.query.get(session['user_id'])

        if request.method == 'POST':
            user.full_name = request.form['full_name']
            user.email = request.form['email']
            user.phone = request.form['phone']
            user.location = request.form['location']
            user.address = request.form['address']
            user.pin_code = request.form['pin_code']

            password = request.form['password']
            if password:
                user.pwd = password

            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('user_dashboard'))

        return render_template('user_edit_profile.html', user=user)


    @app.route('/release/<int:res_id>')
    def release_parking(res_id):
        reservation = Reservation.query.get_or_404(res_id)
        spot = ParkingSpot.query.get(reservation.spot_id)

        if spot.status == 'O':
            spot.status = 'A'
            db.session.commit()
            flash(f'Reservation ID {res_id} has been released!', 'success')
        else:
            flash(f'Reservation ID {res_id} was already free.', 'info')

        return redirect(url_for('user_dashboard'))


    @app.route('/parkedout/<int:res_id>')
    def parked_out(res_id):
        reservation = Reservation.query.get_or_404(res_id)
        spot = ParkingSpot.query.get(reservation.spot_id)

        if spot.status == 'O':
            spot.status = 'A'
            db.session.commit()
            flash(f'Vehicle for Reservation ID {res_id} marked as parked out.', 'success')
        else:
            flash(f'Vehicle for Reservation ID {res_id} was already parked out.', 'info')

        return redirect(url_for('user_dashboard'))

    @app.route("/user_search")
    def user_search():
        if 'user_id' not in session:
            return redirect('/login')

        query = request.args.get("q", "")
        user = User_Info.query.get(session['user_id'])

        results = ParkingLot.query.filter(ParkingLot.location.like(f"%{query}%")) 
            # (ParkingLot.name.like(f"%{query}%"))
        

        reservations = Reservation.query.filter_by(user_id=user.id).all()
        total_bookings = len(reservations)
        active_bookings = sum(1 for r in reservations if r.spot.status == 'O')

        return render_template(
            "user_dashboard.html",
            user=user,
            reservations=reservations,
            total_bookings=total_bookings,
            active_bookings=active_bookings,
            results=results,
            query=query
        )

    @app.route('/book/<int:lot_id>')
    def book_spot(lot_id):
        if 'user_id' not in session:
            return redirect('/login')

        lot = ParkingLot.query.get_or_404(lot_id)

    # Find an available spot
        available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()

        if not available_spot:
            flash('No available spots in this lot.', 'danger')
            return redirect(url_for('user_dashboard'))

    # Reserve the spot
        new_reservation = Reservation(
            user_id=session['user_id'],
            spot_id=available_spot.id,
            vehicle_no='WB00X0000',  # You can later modify to collect from user
            parking_timestamp=datetime.now(),
            cost=lot.price_per_hour  # or calculate cost later on release
        )
        available_spot.status = 'O'
        db.session.add(new_reservation)
        db.session.commit()

        flash(f'Spot {available_spot.id} at {lot.location} booked successfully!', 'success')
        return redirect(url_for('user_dashboard'))

