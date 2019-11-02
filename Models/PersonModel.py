from pymongo import MongoClient, ReturnDocument
import bcrypt
import re
import datetime
from CalendarModel import DailyRecord


class PersonModel:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.wellness_tracker
        self.People = self.db.people
        self.Calendar = self.db.calendar
        self.Goals = self.db.goals

    def insert_person(self,data):
        hashed = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt())

        now = datetime.datetime.now()
        start_date = datetime.date(now.year, now.month, now.day).isoformat()

        dr = DailyRecord()
        calendar = {start_date: dr.hourly_tracker}

        id1 = self.People.insert_one({"username": data.username, "password": hashed,
                                "email": data.email, "age": data.age, "occupation": data.occupation,
                                "location": data.location, "goals": data.goals, "calendar": calendar})
        print("uid is", id1)
        id2 = self.Calendar.insert_one({"_id": id1.inserted_id})
        print("uid is", id2)

    def new_goal(self, person_id, goal):
        filter = {'goal':re.compile(goal, re.IGNORECASE)}
        person = self.People.find_one({"_id": person_id})

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
            self.Goals.update({"_id": person_id},{"$set": {"goals": personal_goals}})

        # TODO: personal_goals might not be the best return value, but it's good for debugging for now
        return personal_goals



class TestData:
    def __init__(self):
        self.username = 'evanakm'
        self.password = '123456'
        self.email = 'evanakm@gmail.com'
        self.age = 34
        self.occupation = 'engineer'
        self.location = 'NYC'
        self.goals = []


#data = TestData()
#pm = PersonModel()
#pm.insert_person(data)







