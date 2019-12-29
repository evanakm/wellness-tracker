from flask import Flask, render_template, session, url_for, redirect, request, jsonify, Markup
from flask_wtf import FlaskForm
import wtforms
from wtforms.fields.html5 import DateField
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, Subgroup, View, Link, Text, Separator

import datetime as dt
from Models import PersonModel, CalendarModel, LoginModel
import dateutil.parser
from bokeh.client import pull_session
from bokeh.embed import server_session

class UserProfileForm(FlaskForm):
    username = wtforms.StringField('username')
    first_name = wtforms.StringField('first_name')
    last_name = wtforms.StringField('last_name')
    email = wtforms.StringField('email')
    password = wtforms.PasswordField('password')
    confirm_password = wtforms.PasswordField('confirm_password')
    date_of_birth = DateField('date_of_birth',format='%Y-%m-%d')
    occupation = wtforms.StringField('occupation')


class AddDataForm(FlaskForm):
    date = DateField('date',format='%Y-%m-%d')
    first_hour = wtforms.IntegerField('first_hour')
    last_hour = wtforms.IntegerField('last_hour')
    activity = wtforms.StringField('activity') #TODO: Make this a dropdown list


class LoginForm(FlaskForm):
    username = wtforms.StringField('username')
    password = wtforms.PasswordField('password')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'IveGotASecret'

bootstrap = Bootstrap(app)
nav = Nav(app)

nav.register_element('navbar_logged_in',Navbar(
    'Wellness Tracker',
    View('Home', 'entry_point'),
    View('Track my progress','view_plot'),
    View('Logout', 'logout'))
)

nav.register_element('navbar_logged_out',Navbar(
    'Wellness Tracker',
    View('Home', 'entry_point'))
)

def validate_session():
    if 'login_status' not in session:
        session['login_status'] = False

    if 'username' not in session:
        return redirect(url_for('login'))

    return False


def clear_session():
    for key in session.keys():
        session.pop(key)


@app.route('/', methods=['GET'])
def entry_point():
    redir = validate_session()
    if redir:
        return redir

    pm = PersonModel.PersonModel()

    #args = json2html.convert(json=data)
    return render_template("Portal.html", session=session)
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

    return "Success"


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
    return render_template("Login.html", form = LoginForm())

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    session['login_status'] = False
    return redirect(url_for('login'))

@app.route('/check_login', methods=['POST'])
def check_login():
    login = LoginModel.LoginModel()

    isCorrect = login.check_user(request.form)

    if isCorrect:
        print('login accepted')
        session["username"] = isCorrect['username']
        session["first_name"] = isCorrect['first_name']
        session["user_id"] = str(isCorrect["_id"])

        print(str(isCorrect))
        session['login_status'] = True
        return str(isCorrect)

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
        return render_template("Blank.html", content="", script=Markup(script))


@app.route('/register', methods=['GET'])
def register():
    redir = validate_session()
    if redir:
        return redir

    return render_template("Register.html", form=UserProfileForm(), new_user=True, title="Register")

@app.route('/change', methods=['GET'])
def change():
    redir = validate_session()
    if redir:
        return redir

    return render_template("Register.html", form=UserProfileForm(), new_user=False, title="Edit My Profile")


@app.route('/update_profile', methods=['POST'])
def update_profile():
    print("Does it get here?")
    pm = PersonModel.PersonModel()

    data = {}

    if request.form['first_name'] != "":
        data['first_name'] = request.form['first_name']

    if request.form['last_name'] != "":
        data['last_name'] = request.form['last_name']

    if request.form['email'] != "":
        data['email'] = request.form['email']

    if request.form['date_of_birth'] != "":
        data['dob'] = request.form['date_of_birth']

    if request.form['password'] != "":
        if request.form['password'] == request.form['confirm_password']:
            data['password'] = request.form['password']

    if request.form['occupation'] != "":
        data['occupation'] = request.form['occupation']

    pm.update_profile(session['user_id'],data)

    return "Success"



if __name__ == "__main__":
    app.run(host="localhost",port=5000,debug=True)

