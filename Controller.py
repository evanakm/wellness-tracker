import web
import datetime as dt
from Models import PersonModel, CalendarModel
from bson.json_util import dumps
from json2html import *
import dateutil.parser

from Views.utilities import CreateTable

web.config.debug = False

urls = (
    '/', 'index',
    '/add_hours','add_hours',
    '/add_data','add_data',
    '/table','tableau'
)

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore("session"), initializer={"user": 'evanakm'})
session_data = session._initializer

render = web.template.render("Views/",base="Main",
                             globals={"session":session_data,"current_user":session_data["user"]})

#render = web.template.render("Views/",base="Main")

class index:
    def GET(self):
        pm = PersonModel.PersonModel()
        user_id = pm.get_id_from_username('evanakm')
        dates = [dt.date(2019, 11, 4), dt.date(2018, 4, 6), dt.date(2016,10,14)]
        data = dumps(pm.get_records_from_dates(user_id,dates))

        return render.Main(json2html.convert(json = data))

class add_hours:
    def POST(self):
        data = web.input()
        pm = PersonModel.PersonModel()
        user_id = pm.get_id_from_username(data.username)
        read_date = dateutil.parser.parse(data.date)
        if not data.first_hour <= data.last_hour:
            for i in range(int(data.first_hour),int(data.last_hour)):
                pm.add_activity_to_hour(user_id,read_date,i,data.activity)

class tableau:
    def GET(self):
        #print(session_data['user'])

        pm = PersonModel.PersonModel()
        user_id = pm.get_id_from_username(session_data['user'])
        dates = [dt.date(2019, 11, 4), dt.date(2018, 4, 6), dt.date(2016,10,14)]
        #data = dumps(pm.get_records_from_dates(user_id,dates))

        data = pm.get_records_from_dates(user_id,dates)

        return render.Main(CreateTable.CreateTable(data))

class add_data:
    def GET(self):
        return render.AddData()


if __name__ == "__main__":
    app.run()

