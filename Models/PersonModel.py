from pymongo import MongoClient, ReturnDocument
import bcrypt
import re
import datetime as dt
from Models.CalendarModel import DailyRecord
from bson.json_util import dumps


class PersonModel:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.wellness_tracker
        self.People = self.db.people
        self.Calendar = self.db.calendar
        self.Goals = self.db.goals

    def insert_person(self,data):
        hashed = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt())

        now = dt.datetime.now()
        start_date = dt.date(now.year, now.month, now.day).isoformat()

        dr = DailyRecord()
        calendar = [{'date':start_date, 'hours': dr.hourly_tracker}]

        id1 = self.People.insert_one({"username": data.username, "password": hashed,
                                "email": data.email, "age": data.age, "occupation": data.occupation,
                                "location": data.location, "goals": data.goals, "calendar": calendar})
        print("uid is", id1)

    def get_id_from_username(self, username):

        if self.People.count_documents({"username": username}) == 0:
            return

        person = self.People.find_one({"username": username})
        return person['_id']

    def new_goal(self, person_id, goal):
        filter = {'goal':re.compile(goal, re.IGNORECASE)}
        person = self.People.find_one({"_id": person_id})

        if self.People.count_documents({"_id": person_id}) == 0:
            return

        personal_goals = person['goals']

        # This is going to be linked by id so that there is no ambiguity, and so that spelling
        # errors don't mess up the process. The database is less human readable, so it needs to be
        # translated on the front end.

        if self.Goals.count_documents(filter) == 0:
            id = self.Goals.insert_one({'goal': goal.lower()})
            id = id.inserted_id
        else:
            gl = self.Goals.find_one(filter)
            id = gl['_id']

        if id not in personal_goals:
            personal_goals.append(id)
            self.People.update_one({"_id": person_id},{"$set": {"goals": personal_goals}})

        # TODO: personal_goals might not be the best return value, but it's good for debugging for now
        return personal_goals

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

    def retrieve_calendar(self, person_id):
        person = self.People.find_one({"_id": person_id})
        return person['calendar']

    def new_day_in_calendar(self, person_id, date):
        new_date = dt.date(date.year, date.month, date.day).isoformat()

        filter = {'_id':person_id, 'calendar':{'$elemMatch':{'date':new_date}}}

        if self.People.count_documents(filter) == 0:
            dr = DailyRecord()
            self.People.update_one({'_id': person_id}, {'$push': {'calendar': {'date': new_date, 'hours': dr.hourly_tracker}}})
        else:
            return

    def add_activity_to_hour(self, person_id, date, hour, activity):
        find_date = dt.date(date.year, date.month, date.day).isoformat()

        filter = {'_id':person_id, 'calendar':{'$elemMatch':{'date':find_date}}}

        hour_label = str(hour).zfill(2)
        field = 'calendar.$.hours.' + hour_label

        if self.People.count_documents(filter) == 0:
            return
        else:
            hour_filter = {'_id': person_id, 'calendar': {'$elemMatch': {'date': find_date}}}
            self.People.update(hour_filter,{'$set': {field: activity}})

        return

    def get_record_from_date(self, person_id, date):
        find_date = dt.date(date.year, date.month, date.day).isoformat()

        person_filter = {'_id': person_id}
        date_filter = {'calendar': {'$elemMatch': {'date': find_date}}}

        if self.People.count_documents({'_id': person_id,'calendar': {'$elemMatch': {'date': find_date}}}) == 0:
            return
        else:
            return self.People.find_one(person_filter, date_filter)['calendar'][0]

    def get_records_from_dates(self, person_id, dates):
        res = []

        for date in dates:
            res.append(self.get_record_from_date(person_id, date))

        return res


class TestData:
    def __init__(self):
        self.username = 'evanakm'
        self.password = '123456'
        self.email = 'evanakm@gmail.com'
        self.age = 24
        self.occupation = 'engineer'
        self.location = 'NYC'
        self.goals = []


data = TestData()
pm = PersonModel()
#pm.insert_person(data)
user_id = pm.get_id_from_username('evanakm')
pm.new_goal(user_id,'Exercise')
pm.new_goal(user_id,'Michelle')
pm.new_goal(user_id,'Improve Coding')
pm.new_goal(user_id,'Read more')

pm.new_day_in_calendar(user_id,dt.date(2019,11,4))
pm.new_day_in_calendar(user_id,dt.date(2018,4,6))
pm.new_day_in_calendar(user_id,dt.date(2016,10,14))

pm.add_activity_to_hour(user_id,dt.date(2019,11,4),4,'exercise')

print(dumps(pm.get_record_from_date(user_id,dt.date(2019,11,4))))
print(dumps(pm.get_record_from_date(user_id,dt.date(2018,4,6))))

dates = [dt.date(2019,11,4), dt.date(2018,4,6)]
cals = pm.get_records_from_dates(user_id,dates)
for cal in cals:
    print(dumps(cal))

print(dumps(cals))