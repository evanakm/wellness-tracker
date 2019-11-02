from pymongo import MongoClient, ReturnDocument
import re
import datetime

class DailyRecord:
    def __init__(self):
        self.hourly_tracker = {'00':'', '01':'', '02':'', '03':'',
                               '04':'', '05':'', '06':'', '07':'',
                               '08':'', '09':'', '10':'', '11':'',
                               '12':'', '13':'', '14':'', '15':'',
                               '16':'', '17':'', '18':'', '19':'',
                               '20':'', '21':'', '22':'', '23':''}

    def change_hour(self, hour, new_value):
        if hour not in range(24):
            raise Exception("Not a valid hour")

        self.hourly_tracker[str(hour).zfill(2)] = new_value

    def clear_hour(self, hour):
        if hour not in range(24):
            raise Exception("Not a valid hour")

        self.hourly_tracker[str(hour).zfill(2)] = ''

    def clear_whole_day(self):
        self.hourly_tracker = {'00':'', '01':'', '02':'', '03':'',
                               '04':'', '05':'', '06':'', '07':'',
                               '08':'', '09':'', '10':'', '11':'',
                               '12':'', '13':'', '14':'', '15':'',
                               '16':'', '17':'', '18':'', '19':'',
                               '20':'', '21':'', '22':'', '23':''}




class CalendarModel:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.wellness_tracker
        self.People = self.db.people
        self.Calendar = self.db.calendar
        self.Goals = self.db.goals


