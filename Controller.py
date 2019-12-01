import web
import datetime as dt
from Models import PersonModel, CalendarModel
from bson.json_util import dumps
from json2html import *
import dateutil.parser
import json
from bokeh.client import pull_session
from bokeh.embed import server_session

from Views.utilities import CreateTable

web.config.debug = False

urls = (
    '/', 'index',
    '/add_hours','add_hours',
    '/add_data','add_data',
    '/table','tableau',
    '/view_plot','view_plot'
)

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore("session"), initializer={
    "user": 'evanakm', "dates": [dt.date.today()]})
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

class view_plot:
    def GET(self):
        with pull_session(url="http://localhost:5006/CreatePlot") as session:
            # update or customize that session
            # session.document.roots[0].children[1].title.text = "Special Sliders For A Specific User!"

            # generate a script to load the customized session
            script = server_session(session_id=session.id, url='http://localhost:5006/CreatePlot')

            print("Does it get here?")
            print(script)

            # use the script in the rendered page
            return render.Main(script)


if __name__ == "__main__":
    app.run()

