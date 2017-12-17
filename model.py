"""Models and database functions for cattexts."""

from flask_sqlalchemy import SQLAlchemy

from helper_functions import *
import bcrypt
db = SQLAlchemy()

#*****************************************************************************#

class User(db.Model):
    """User model"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    timezone = db.Column(db.String(100), nullable=False)    
    phone_number = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    verification_code = db.Column(db.String(6), nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        """Provide useful info when printed to console"""

        s = "<User user_id=%s email=%s timezone=%s>"

        return s % (self.user_id, self.email, self.timezone)

class Cat(db.Model):
    """Cat model"""

    __tablename__ = "cats"

    cat_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False) # foreign key to users
    name = db.Column(db.String(20), nullable=False)
    dinner_time = db.Column(db.DateTime, nullable=False)
    snack = db.Column(db.String(20), nullable=False)
    activity1 = db.Column(db.String(20), nullable=False)
    activity2 = db.Column(db.String(20), nullable=False)
    toy1 = db.Column(db.String(20), nullable=False)
    toy2 = db.Column(db.String(20), nullable=False)

    user = db.relationship("User", backref=db.backref("cats"))

    def __repr__(self):
        """Provide useful info when printed to console"""

        s = "<cat cat_id=%s name=%s>"

        return s % (self.cat_id, self.name)

#*****************************************************************************#

def connect_to_db(app, location="postgres:///cattexts"):
    """Connect the database to our Flask app."""

    # Configure to use our Postgres database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///cattexts'
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

def example_data():
    """Load fake db with data for testing."""

    password='hellboy'
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    new_user = User(email="hellboy@hellboy.com", password=password,
                    phone_number="413-123-4567", timezone="US/Pacific")
    db.session.add(new_user)

    dinner_time="7:00"
    ampm="pm"
    timezone="US/Pacific"

    time = parse_time(dinner_time)
    hour, minutes = time
    hour = make_24_hour_time(ampm, hour)
    date = convert_to_utc(hour, minutes, timezone)

    new_cat = Cat(user_id=1, name="Hellboy", dinner_time=date, 
                  snack="tuna", activity1="sleeping", activity2="meowing", 
                  toy1="space ball", toy2="catnip carrot")
    db.session.add(new_cat)
    db.session.commit()


if __name__ == "__main__":

    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."

    db.create_all()
