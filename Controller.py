#import web
from flask import Flask, render_template, session, url_for, redirect, request
from flask_wtf import Form
import wtforms
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, Subgroup, View, Link, Text, Separator

from types import SimpleNamespace as SNS
import datetime as dt
from Models import PersonModel, CalendarModel, LoginModel
from bson.json_util import dumps
from json2html import *
import dateutil.parser
import json
from bokeh.client import pull_session
from bokeh.embed import server_session
import requests

#web.config.debug = False

class UserProfileForm(Form):
    username = wtforms.StringField('username')
    first_name = wtforms.StringField('first_name')
    last_name = wtforms.StringField('last_name')
    email = wtforms.StringField('email')
    password = wtforms.PasswordField('password')
    confirm_password = wtforms.PasswordField('confirm_password')
    date_of_birth = wtforms.DateField('date_of_birth')
    occupation = wtforms.StringField('occupation')

class AddDataForm(Form):
    date = wtforms.DateField('date')
    first_hour = wtforms.IntegerField('first_hour')
    last_hour = wtforms.IntegerField('last_hour')
    activity = wtforms.StringField('activity') #TODO: Make this a dropdown list


app = Flask(__name__)
app.config['SECRET_KEY'] = 'IveGotASecret'

bootstrap = Bootstrap(app)
nav = Nav(app)

nav.register_element('navbar',Navbar(
    'test_bar',
    View('Home', 'entry_point'),
    View('Track my progress','view_plot'))
)

def validate_session():
    if 'username' not in session:
        #return redirect(url_for('login'))
        return redirect('/login')

    return False


def render(template, content = None):
    body = render_template("Views/" + template, content=content)
    return render_template("Views/Main.html", body=body)


@app.route('/', methods=['GET'])
def entry_point():
    redir = validate_session()
    if redir:
        return redir

    #args = json2html.convert(json=data)
    return render_template("Portal.html")
    #return render_template("Main.html")


@app.route('/add_hours', methods=['POST'])
def add_hours():
    user_id = session['user_id']
    read_date = dateutil.parser.parse(request.form.get('date'))

    pm = PersonModel.PersonModel()

    first_hour = request.form.get('first_hour')
    last_hour = request.form.get('last_hour')
    if int(first_hour) <= int(last_hour):
        for i in range(int(first_hour),int(last_hour)):
            pm.add_activity_to_hour(user_id,read_date,i,request.form.get('activity'))


# This is for testing only.
#@app.route('/debug_tableau', methods=['GET'])
#def tableau():
#    user_id = session['user_id']
#    pm = PersonModel.PersonModel()
#
#    dates = [dt.date(2019, 11, 4), dt.date(2018, 4, 6), dt.date(2016,10,14)]
#    #data = dumps(pm.get_records_from_dates(user_id,dates))
#
#    data = pm.get_records_from_dates(user_id,dates)
#
#    return render("Blank.html",CreateTable.CreateTable(data))


@app.route('/add_data', methods=['GET'])
def add_data():
    redir = validate_session()
    if redir:
        return redir

    return render_template("AddData.html", form=AddDataForm())


@app.route('/login', methods=['GET'])
def login():
    redir = validate_session()
    if redir:
        return redir

    return render("Login.html")


@app.route('/check_login', methods=['POST'])
def check_login():
    login = LoginModel.LoginModel()

    data = SNS()

    data.username = request.form.get("username")
    data.password = request.form.get("password")

    isCorrect = login.check_user(data)

    if isCorrect:
        print('login accepted')
        session["username"] = isCorrect
        return isCorrect

    print('login not accepted')
    return "Error"


@app.route('/view_plot', methods=['GET'])
def view_plot():
    redir = validate_session()
    if redir:
        return redir

    with pull_session(url="http://localhost:5006/CreatePlot", arguments=dict(username=session['username'],
                                                start_date='2019-11-01', end_date=dt.date.today().isoformat()))\
                                                as bokeh_session:
        #print(bokeh_session.document.to_json_string())  # uncomment when debugging

        script = server_session(session_id=bokeh_session.id, url='http://localhost:5006/CreatePlot')

        # use the script in the rendered page
        return render("Blank.html",script)


@app.route('/register', methods=['GET'])
def register():
    redir = validate_session()
    if redir:
        return redir

    return render("Register.html", UserProfileForm())


@app.route('/update_profile', methods=['POST'])
class new_user:
    pass



if __name__ == "__main__":
    app.run(host="localhost",port=5000,debug=True)

