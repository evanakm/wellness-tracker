from pymongo import MongoClient, ReturnDocument
import bcrypt
import re
import datetime as dt
from Models.CalendarModel import DailyRecord
from bson.json_util import dumps
from bson import ObjectId
#from Views.utilities import CreateTable


class IncompleteData(Exception):
    pass

class PersonModel:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.wellness_tracker
        self.People = self.db.people
        self.Calendar = self.db.calendar
        self.Goals = self.db.goals

    def register_new_account(self,data):

        if self.People.count_documents({"username": data.username}) != 0:
            return "username exists"

    def insert_person(self,data):

        if self.People.count_documents({"username": data.username}) != 0:
            return "username exists"

        hashed = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt())

        now = dt.datetime.now()
        start_date = dt.date(now.year, now.month, now.day).isoformat()

        dr = DailyRecord()
        calendar = [{'date':start_date, 'hours': dr.hourly_tracker}]

        if type(data.dob) is dt.date:
            date = data.dob.isoformat()
        else:
            date = data.dob

        id1 = self.People.insert_one({"username": data.username, "password": hashed,
                                "first_name": data.first_name, "last_name": data.last_name,
                                "email": data.email, "dob": date, "occupation": data.occupation,
                                "location": data.location, "goals": data.goals, "calendar": calendar})
        print("uid is", id1)

    def update_profile(self,person_id,data):

        person_id = self.object_id(person_id)

        if 'password' in data:
            hashed = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt())
            self.People.update_one({"_id": person_id},{"$set": {"password": hashed}})

        if 'first_name' in data:
            self.People.update_one({"_id": person_id},{"$set": {"first_name": data['first_name']}})

        if 'last_name' in data:
            self.People.update_one({"_id": person_id},{"$set": {"last_name": data['last_name']}})

        if 'email' in data:
            self.People.update_one({"_id": person_id},{"$set": {"email": data['email']}})

        if 'dob' in data:
            self.People.update_one({"_id": person_id},{"$set": {"dob": data['dob'].isoformat()}})

        if 'occupation' in data:
            self.People.update_one({"_id": person_id},{"$set": {"occupation": data['occupation']}})

        if 'location' in data:
            self.People.update_one({"_id": person_id},{"$set": {"occupation": data['location']}})

        if 'goals' in data:
            self.People.update_one({"_id": person_id},{"$set": {"occupation": data['goals']}})



    def get_id_from_username(self, username):

        if self.People.count_documents({"username": username}) == 0:
            return

        person = self.People.find_one({"username": username})
        return person['_id']


    def new_goal(self, person_id, goal):
        person_id = self.object_id(person_id)

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
        person_id = self.object_id(person_id)

        person = self.People.find_one({"_id": person_id})
        return person['calendar']


    def new_day_in_calendar(self, person_id, date):
        person_id = self.object_id(person_id)

        new_date = dt.date(date.year, date.month, date.day).isoformat()

        filter = {'_id':person_id, 'calendar':{'$elemMatch':{'date':new_date}}}

        if self.People.count_documents(filter) == 0:
            dr = DailyRecord()
            self.People.update_one({'_id': person_id}, {'$push': {'calendar': {'date': new_date, 'hours': dr.hourly_tracker}}})
        else:
            return


    def add_activity_to_hour(self, person_id, date, hour, activity):
        person_id = self.object_id(person_id)

        find_date = dt.date(date.year, date.month, date.day).isoformat()

        filter = {'_id':person_id, 'calendar':{'$elemMatch':{'date':find_date}}}

        hour_label = str(hour).zfill(2)
        field = 'calendar.$.hours.' + hour_label

        if self.People.count_documents(filter) == 0:
            self.new_day_in_calendar(person_id, date)

        hour_filter = {'_id': person_id, 'calendar': {'$elemMatch': {'date': find_date}}}
        self.People.update(hour_filter,{'$set': {field: activity}})


    def get_record_from_date(self, person_id, date):
        person_id = self.object_id(person_id)

        find_date = dt.date(date.year, date.month, date.day).isoformat()

        person_filter = {'_id': person_id}
        date_filter = {'calendar': {'$elemMatch': {'date': find_date}}}

        if self.People.count_documents({'_id': person_id,'calendar': {'$elemMatch': {'date': find_date}}}) == 0:
            return
        else:
            res = self.People.find_one(person_filter, date_filter)['calendar'][0]
            return res


    def get_records_from_dates(self, person_id, dates):
        person_id = self.object_id(person_id)

        res = []

        for date in dates:
            temp = self.get_record_from_date(person_id, date)
            if temp is not None:
                res.append(temp)

        return res

    def object_id(self, oid):
        if type(oid) != ObjectId:
            return ObjectId(oid)

        return oid

class TestData:
    def __init__(self):
        self.username = 'evanakm'
        self.first_name = 'Evan'
        self.last_name = 'Meikleham'
        self.password = '123456'
        self.email = 'evanakm@gmail.com'
        self.dob = dt.date(1985,10,14).isoformat()
        self.occupation = 'engineer'
        self.location = 'NYC'
        self.goals = []

'''
data = TestData()
pm = PersonModel()
#pm.insert_person(data)
user_id = pm.get_id_from_username('evanakm')
pm.new_goal(user_id,'Exercise')
pm.new_goal(user_id,'Michelle')
pm.new_goal(user_id,'Improve Coding')
pm.new_goal(user_id,'Read more')

pm.new_day_in_calendar(user_id,dt.date(2019,11,29))
pm.new_day_in_calendar(user_id,dt.date(2019,11,28))
pm.new_day_in_calendar(user_id,dt.date(2019,11,27))

pm.add_activity_to_hour(user_id,dt.date(2019,11,27),0,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),1,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),2,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),3,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),4,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),5,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),6,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),7,'Goal_1')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),8,'Goal_1')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),9,'Exercise')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),10,'Work')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),11,'Work')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),12,'Work')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),13,'Work')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),14,'Work')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),15,'Work')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),16,'Work')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),17,'Goal_2')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),18,'Goal_2')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),19,'Goal_2')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),20,'Relationship')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),21,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),22,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,27),23,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),0,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),1,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),2,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),3,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),4,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),5,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),6,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),7,'Goal_3')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),8,'Goal_3')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),9,'Goal_3')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),10,'Goal_3')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),11,'Exercise')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),12,'Exercise')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),13,'Exercise')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),14,'Goal_2')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),15,'Goal_2')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),16,'Goal_2')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),17,'Goal_2')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),18,'Relationship')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),19,'Relationship')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),20,'Relationship')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),21,'Relationship')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),22,'Relationship')
pm.add_activity_to_hour(user_id,dt.date(2019,11,28),23,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),0,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),1,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),2,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),3,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),4,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),5,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),6,'None')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),7,'None')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),8,'Goal_2')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),9,'Goal_2')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),10,'Work')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),11,'Work')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),12,'Work')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),13,'Work')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),14,'Work')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),15,'Goal_2')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),16,'Goal_2')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),17,'Goal_2')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),18,'TV')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),19,'TV')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),20,'TV')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),21,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),22,'Sleep')
pm.add_activity_to_hour(user_id,dt.date(2019,11,29),23,'Sleep')

print(dumps(pm.get_record_from_date(user_id,dt.date(2019,11,29))))
print(dumps(pm.get_record_from_date(user_id,dt.date(2018,11,28))))

dates = [dt.date(2019,11,27), dt.date(2019,11,29)]
cals = pm.get_records_from_dates(user_id,dates)
for cal in cals:
    print(dumps(cal))

print(dumps(cals))

#print(CreateTable.CreateTable(cals))

newdata = {'email': 'evanakm@protonmail.com'}
pm.update_profile(user_id,newdata)
'''

