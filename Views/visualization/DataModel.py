from pymongo import MongoClient, ReturnDocument
import datetime as dt
from bson.json_util import dumps

class UserNotFoundError(Exception):
    pass

class DataModel:
    def __init__(self, username):
        self.client = MongoClient()
        self.db = self.client.wellness_tracker
        self.People = self.db.people
        self.Calendar = self.db.calendar
        self.Goals = self.db.goals

        # TODO: Make this fail gracefully
        self.person_id = self.get_id_from_username(username)

    def get_record_from_date(self, person_id, date):
        find_date = dt.date(date.year, date.month, date.day).isoformat()

        person_filter = {'_id': person_id}
        date_filter = {'calendar': {'$elemMatch': {'date': find_date}}}

        if self.People.count_documents({'_id': person_id,'calendar': {'$elemMatch': {'date': find_date}}}) == 0:
            return
        else:
            res = self.People.find_one(person_filter, date_filter)['calendar'][0]
            return res

    def get_records_from_dates(self, person_id, dates):
        res = []

        for date in dates:
            temp = self.get_record_from_date(person_id, date)
            if temp is not None:
                res.append(temp)

        return res

    def get_id_from_username(self, username):

        if self.People.count_documents({"username": username}) == 0:
            raise UserNotFoundError(username + " not found in database")

        person = self.People.find_one({"username": username})
        return person['_id']

    def get_id_from_goal_name(self, goal_name):

        if self.Goals.count_documents({"goal": goal_name}) == 0:
            return "Not Found"

        goal = self.Goals.find_one({"username": goal_name})
        return goal['_id']

    def get_goal_name_from_id(self, id):

        if self.Goals.count_documents({"_id": id}) == 0:
            return "Not Found"

        goal = self.Goals.find_one({"_id": id})
        return goal['goal']
