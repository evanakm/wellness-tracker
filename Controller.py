import web
import datetime as dt
from Models import PersonModel
from bson.json_util import dumps
from json2html import *

web.config.debug = False

urls = (
  '/', 'index'
)

app = web.application(urls, globals())

render = web.template.render("Views/",base="Main")

class index:
    def GET(self):
        pm = PersonModel.PersonModel()
        user_id = pm.get_id_from_username('evanakm')
        dates = [dt.date(2019, 11, 4), dt.date(2018, 4, 6)]
        data = dumps(pm.get_records_from_dates(user_id,dates))

        return render.Main(json2html.convert(json = data))


if __name__ == "__main__":
    app.run()

