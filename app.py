from flask import Flask
from backend.models import db

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parking.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Import controllers here and pass the app to them
    import backend.controllers
    backend.controllers.init_app(app)

    print("Parking app started...")
    return app

app = create_app()

if __name__ == "__main__":
    app.run()

