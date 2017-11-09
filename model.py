"""Models and database functions for pettextsdb."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#*****************************************************************************#

class Cat(db.Model):
    """Cat model"""

    __tablename__ = "cats"

    cat_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    dinner_time = db.Column(db.String(5), nullable=False)
    snack = db.Column(db.String(20), nullable=False)
    activity1 = db.Column(db.String(20), nullable=False)
    activity2 = db.Column(db.String(20), nullable=False)
    toy1 = db.Column(db.String(20), nullable=False)
    toy2 = db.Column(db.String(20), nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)
    # phone number won't be used until I launch app and purchase Twilio plan, 
    # but I guess I could store my own number instead of sourcing from environ
    # to get it started

    def __repr__(self):
        """Provide useful info when printed to console"""

        s = "<cat cat_id=%s name=%s>"

        return s % (self.cat_id, self.name)

#*****************************************************************************#

# def init_app():

#     from flask import Flask
#     app = Flask(__name__)

#     connect_to_db(app)
#     print "Connected to DB"

# def connect_to_db(app):
#     """Connect the database to our Flask app."""

#     # Configure to use our PostgreSQL database
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///cattexts'
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     db.app = app
#     db.init_app(app)


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our Postgres database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///cattexts'
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app
    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."

    db.create_all()