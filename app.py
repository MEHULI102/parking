from flask import Flask
from backend.models import db

def create_app():
    app = Flask(__name__)
    app.debug = True

    # Configurations
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parking.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Secret key for session management
    app.secret_key = 'thisisaverysecretkey123'  # 🔑 required for using `session`

    # Initialize database
    db.init_app(app)

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    # Import and initialize routes/controllers
    import backend.controllers
    backend.controllers.init_app(app)

    print("✅ Parking app started...")
    return app


app = create_app()

if __name__ == "__main__":
    app.run()

