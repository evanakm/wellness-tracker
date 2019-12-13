import web
import datetime as dt
from Models import PersonModel, CalendarModel, LoginModel
from bson.json_util import dumps
from json2html import *
import dateutil.parser
import json
from bokeh.client import pull_session
from bokeh.embed import server_session
import requests

from Views.utilities import CreateTable

web.config.debug = False

urls = (
    '/', 'entry_point',
    '/add_hours','add_hours',
    '/add_data','add_data',
    '/table','tableau',
    '/view_plot','view_plot',
    '/login','login',
    '/check_login','check_login'
)

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore("session"), initializer={
    "user": None, "dates": [dt.date.today()]})
session_data = session._initializer

render = web.template.render("Views/",base="Main",
                             globals={"session":session_data,"current_user":session_data["user"]})

#render = web.template.render("Views/",base="Main")

class entry_point:
    def GET(self):
        if not session_data["user"]:
            raise web.seeother('/login')
        else:
            print(session_data["user"])
            pm = PersonModel.PersonModel()
            user_id = pm.get_id_from_username(session_data["user"])
            print(user_id)
            dates = [dt.date(2019, 11, 27), dt.date(2019, 11, 28)]
            data = dumps(pm.get_records_from_dates(user_id, dates))

            print(data)

            return render.Portal()

            #return render.Blank(json2html.convert(json=data))


class index:
    def GET(self):
        pm = PersonModel.PersonModel()
        user_id = pm.get_id_from_username('evanakm')
        dates = [dt.date(2019, 11, 27), dt.date(2019, 11, 28)]
        data = dumps(pm.get_records_from_dates(user_id,dates))

        return render.Main(json2html.convert(json = data))

class add_hours:
    def POST(self):
        data = web.input()
        pm = PersonModel.PersonModel()
        user_id = pm.get_id_from_username(session_data["user"])
        read_date = dateutil.parser.parse(data.date)
        if data.first_hour <= data.last_hour:
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

class set_dates:
    def POST(self):
        data = json.loads(web.data())
        d1 = dt.date.fromisoformat(data['start_date'])
        d2 = dt.date.fromisoformat(data['end_date'])
        dates = [d1 + dt.timedelta(days=x) for x in range((d2 - d1).days + 1)]

        session_data['dates'] = dates

class retrieve_data:
    def GET(self):
        pm = PersonModel.PersonModel()
        user_id = pm.get_id_from_username(session_data['user'])
        dates = session_data['dates']

        return pm.get_records_from_dates(user_id,dates)

class login:
    def GET(self):
        return render.Login()

class check_login:
    def POST(self):
        data = web.input()
        print(data)
        login = LoginModel.LoginModel()
        isCorrect = login.check_user(data)

        if isCorrect:
            print('login accepted')
            session_data["user"] = isCorrect
            return isCorrect

        print('login not accepted')
        return "Error"

class view_plot:
    def GET(self):
        with pull_session(url="http://localhost:5006/CreatePlot", arguments=dict(username='evanakm',
                                                    start_date='2019-11-01', end_date='2019-12-01')) as bokeh_session:
            #print(bokeh_session.document.to_json_string())  # uncomment when debugging

            script = server_session(session_id=bokeh_session.id, url='http://localhost:5006/CreatePlot')

            # use the script in the rendered page
            return render.Blank(script)


if __name__ == "__main__":
    app.run()

