import pymongo, bcrypt
from pymongo import MongoClient

class LoginModel:

    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.wellness_tracker
        self.People = self.db.people

    def check_user(self,data):
        user = self.People.find_one({"username":data.username})

        if user:
            if bcrypt.checkpw(data.password.encode(),user["password"]):
                return user
            else:
                return False

        else:
            return False
