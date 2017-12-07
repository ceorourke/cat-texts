#########################Helper functions for Cat Texts#########################

from datetime import datetime
from pytz import timezone
import pytz

def parse_time(time):
    """Parse hours and minutes from time"""
    
    index = 0
    for char in time:
        if char == ":":
            break
        index += 1

    hour = int(time[:index])
    minutes = int(time[index+1:])
    times = []
    times.append(hour)
    times.append(minutes)

    return times

# def make_hour(hour):
#     """Formats hour for proper time display"""

#     if len(str(hour)) < 2:
#         new_hour = "0"
#         new_hour += str(hour)
#     else:
#         new_hour = str(hour)

#     return new_hour

def make_minutes(minutes):
    """Formats minutes for proper time display"""

    if len(str(minutes)) < 2:
        new_minutes = "0"
        new_minutes += str(minutes) 
    else:
        new_minutes = str(minutes)

    return new_minutes

def make_24_hour_time(ampm, hour):
    """Convert 12 hour time to 24 hour time"""

    if ampm == "pm":
        if hour == 12:
            hour == 0
        else:
            hour += 12

    return hour

def am_or_pm(hour):
    """Return whether the time is am or pm based on 24 hour time formatting"""

    if hour > 12:
        return "pm"
    return "am"

def make_12_hour_time(hour):
    """Convert 24 hour time from db to 12 hour time for display"""

    if hour == 0:
        hour = 12
    if hour > 12:
        hour -= 12

    return hour

def convert_to_utc(hour, minutes, user_timezone):
    """Take in user inputted time and create a UTC datetime object"""

    date = datetime.now() # create a datetime object (in UTC time by default)
    utc = pytz.utc 
    date = date.replace(tzinfo=utc) # add utc timezone info
    this_timezone = timezone(user_timezone)
    date = date.astimezone(this_timezone)

    # change the hours and minutes to user input, clear seconds and microseconds
    date = date.replace(hour=hour, minute=minutes, second=0, microsecond=0)

    # change back to UTC to store in database
    date = date.astimezone(utc)

    return date



