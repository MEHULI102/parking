from flask import Flask
from backend.models import db
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.debug = True

  
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parking.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    
    app.secret_key = 'thisisaverysecretkey123'

    
    db.init_app(app)

    
    with app.app_context():
        db.create_all()

   
    import backend.controllers
    backend.controllers.init_app(app)

    def timeago(value):
        if not isinstance(value, datetime):
            return value
        now = datetime.now()
        diff = now - value

        seconds = diff.total_seconds()
        minutes = seconds // 60
        hours = minutes // 60
        days = hours // 24

        if days >= 365:
            return f"{int(days // 365)}y ago"
        elif days >= 30:
            return f"{int(days // 30)}mo ago"
        elif days > 0:
            return f"{int(days)}d ago"
        elif hours > 0:
            return f"{int(hours)}h ago"
        elif minutes > 0:
            return f"{int(minutes)}m ago"
        else:
            return "Just now"

    app.jinja_env.filters['timeago'] = timeago

    print("✅ Parking app started...")
    return app


app = create_app()

if __name__ == "__main__":
    app.run()
