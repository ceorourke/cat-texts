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

def make_24_hour_time(ampm, hour):
    """Convert 12 hour time to 24 hour time"""

    if ampm == "pm":
        if hour == 12:
            hour == 0
        else:
            hour += 12

    return hour

def convert_to_utc(hour, minutes):
    """Take in user inputted time and create a UTC datetime object"""

    date = datetime.now() # create a datetime object (in UTC time by default)
    utc = pytz.utc 
    date = date.replace(tzinfo=utc) # add utc timezone info

    # TODO get the users' timezone rather than hardcoding PST conversion
    this_timezone = timezone('US/Pacific')
    date = date.astimezone(this_timezone)
    # change the hours and minutes to user input, clear seconds and microseconds
    date = date.replace(hour=hour, minute=minutes, second=0, microsecond=0)

    # change back to UTC to store in database
    date = date.astimezone(utc)

    return date