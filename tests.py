import server
import unittest
from server import *
from helper_functions import *
from model import *
import os
from datetime import datetime
from pytz import timezone
import pytz
################################################################################

class ServerTestsWithSession(unittest.TestCase):
    """Tests for the cat texts site that require session"""

    def setUp(self):
        """Code to run before every test."""

        self.client = server.app.test_client()
        server.app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        connect_to_db(app, "postgresql:///testdb")
        db.create_all()

        example_data()
        with self.client as c:
          with c.session_transaction() as sess:
              sess['user_id'] = 1

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_logout(self):
        """Can we log out a user that's been logged in?"""

        result = self.client.get("/logout", follow_redirects=True)
        self.assertIn("Goodbye!", result.data)

    def test_main_page(self):
        """Can we log in and reach the main page?"""

        result = self.client.get("/main")
        self.assertIn("Your cat's current info:", result.data)
        self.assertIn('Hellboy', result.data)
        self.assertIn('tuna', result.data)
        self.assertIn('meowing', result.data)

    def test_login_fail_pw(self):
        """Can we reject a user with the wrong password?"""

        result = self.client.post("/login", data={"email": "hellboy@hellboy.com",
                                                  "password": "jfsghjkdfhgh"},
                                                  follow_redirects=True)
        self.assertIn("Incorrect password.", result.data)


    def test_login_fail_email(self):
        """Can we reject a user with the wrong email?"""

        result = self.client.post("/login", data={"email": "stuff@stuff.com",
                                                  "password": "jfsghjkdfhgh"},
                                                  follow_redirects=True)
        self.assertIn("Incorrect email.", result.data)


class ServerTestsWithoutSession(unittest.TestCase):
    """Tests for the cat texts site"""

    def setUp(self):
        """Code to run before every test."""
        
        connect_to_db(app, "postgresql:///testdb")
        self.client = server.app.test_client()
        server.app.config['TESTING'] = True
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_welcome_page(self):
        """Can we reach the welcome page?"""

        result = self.client.get("/")
        self.assertIn('Login or <a href="/register">Register</a>', result.data)

    def test_registration_page(self):
        """Can we reach the registration page?"""

        result = self.client.get("/register")
        self.assertIn('Register for Cat Texts!', result.data)

    # def test_registration(self):
    #     """Can we register a new user"""

    #     import bcrypt
    #     time = "7:00"
    #     password='imcute'
    #     password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    #     result = self.client.post("/register", data={"phone": "413-329-3198",
    #                                                  "email": "hellboy@cute.com", 
    #                                                  "password": password,
    #                                                  "user_id": "1",
    #                                                  "name": "Hellboy",
    #                                                  "time": time,
    #                                                  "timezone": "US/Pacific",
    #                                                  "ampm": "pm",
    #                                                  "snack": "tuna",
    #                                                  "activity1": "meowing",
    #                                                  "activity2": "sleeping",
    #                                                  "toy1": "space ball",
    #                                                  "toy2": "catnip carrot"
    #                                                  }, follow_redirects=True)
    #     self.assertIn("/main", result.data)


    # def test_login_success(self):
    #     """Can we log in a registered user?"""

    #     result = self.client.post("/login", data={"email": "hellboy@hellboy.com", 
    #                                               "password": "hellboy",
    #                                               }, follow_redirects=True)
    #     self.assertIn("/login", result.data)
    #     self.assertIn("Successfully logged in!", result.data)

class HelperFunctionTexts(unittest.TestCase):
    """Tests all helper functions"""


    def test_parse_time(self):
        """Can we parse time correctly?"""

        time = "7:00"
        assert parse_time(time) == [7, 0]

    def test_make_minutes(self):
        """Can we format minutes properly for display?"""

        minutes = "4"
        assert make_minutes(minutes) == "04"

    def test_make_24_hour_time(self):
        """Can we format the time correctly?"""

        ampm = "pm"
        hour = 7
        assert make_24_hour_time(ampm, hour) == 19

    def test_am_or_pm(self):
        """Is the time am or pm?"""

        hour = 17
        assert am_or_pm(hour) == "pm"

        hour = 7
        assert am_or_pm(hour) == "am"

    def test_make_12_hour_time(self):
        """Can we convert 24 hour time to 12 hour time?"""

        hour = 23
        assert make_12_hour_time(hour) == 11

    def test_convert_to_utc(self):
        """Can we convert user's local time to a datetime object in UTC?"""

        hour = 3
        minutes = 4
        user_timezone = "US/Pacific"

        # this is kind of a dubious test as I copied much of the code from the
        # function itself. However, it needs to be a datetime object to verify
        # that it's working, so I'm not sure if there is a better way to get
        # around this

        date = datetime.now()
        date = date.replace(tzinfo=pytz.utc)
        this_timezone = timezone(user_timezone)
        date = date.astimezone(this_timezone)
        date = date.replace(hour=hour, minute=minutes, second=0, microsecond=0)
        date = date.astimezone(pytz.utc)

        assert convert_to_utc(hour, minutes, user_timezone) == date


if __name__ == "__main__":
    unittest.main()



