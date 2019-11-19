import pandas as pd
from math import pi
import datetime as dt
from bokeh.io import output_file, show
from bokeh.models import DatetimeTickFormatter, Select, FactorRange, ColumnDataSource
from bokeh.plotting import figure

raw_data = [{"date": "2019-11-04",
             "hours": {"00": "sleep",
                       "01": "sleep",
                       "02": "sleep",
                       "03": "sleep",
                       "04": "sleep",
                       "05": "sleep",
                       "06": "sleep",
                       "07": "goal_1",
                       "08": "goal_1",
                       "09": "exercise",
                       "10": "work",
                       "11": "work",
                       "12": "work",
                       "13": "work",
                       "14": "work",
                       "15": "work",
                       "16": "work",
                       "17": "goal_2",
                       "18": "goal_2",
                       "19": "goal_2",
                       "20": "relationship",
                       "21": "sleep",
                       "22": "sleep",
                       "23": "sleep"}},
            {"date": "2019-11-03",
             "hours": {"00": "sleep",
                       "01": "sleep",
                       "02": "sleep",
                       "03": "sleep",
                       "04": "sleep",
                       "05": "sleep",
                       "06": "sleep",
                       "07": "goal_3",
                       "08": "goal_3",
                       "09": "goal_3",
                       "10": "goal_3",
                       "11": "exercise",
                       "12": "exercise",
                       "13": "exercise",
                       "14": "goal_2",
                       "15": "goal_2",
                       "16": "goal_2",
                       "17": "goal_2",
                       "18": "relationship",
                       "19": "relationship",
                       "20": "relationship",
                       "21": "relationship",
                       "22": "relationship",
                       "23": "sleep"}},
            {"date": "2019-11-05",
             "hours": {"00": "sleep",
                       "01": "sleep",
                       "02": "sleep",
                       "03": "sleep",
                       "04": "sleep",
                       "05": "sleep",
                       "06": "none",
                       "07": "none",
                       "08": "goal_2",
                       "09": "goal_2",
                       "10": "work",
                       "11": "work",
                       "12": "work",
                       "13": "work",
                       "14": "work",
                       "15": "goal_2",
                       "16": "goal_2",
                       "17": "goal_2",
                       "18": "tv",
                       "19": "tv",
                       "20": "tv",
                       "21": "sleep",
                       "22": "sleep",
                       "23": "sleep"}}]

test_dates = [dt.date(2019, 11, 4), dt.date(2019, 11, 5), dt.date(2019, 11, 6)]

get_indexes = lambda dates, data: [i for (y, i) in zip(data, range(len(data))) if dt.date.fromisoformat(y['date']) in dates]
print(get_indexes(test_dates,raw_data))

def get_unique_activities(data):
    activities = set()

    for day in data:
        for i in range(24):
            activities.add(day['hours'][str(i).zfill(2)])

    return activities

acts = get_unique_activities(raw_data)


def extract_frequencies(data):
    activities = list(get_unique_activities(data))

    number_of_days = len(data)
    number_of_activities = len(activities)

    dates = ['' for x in range(number_of_days)]
    freqs = [0 for x in range(len(activities) * len(data))]

    for i in range(number_of_days):
        day = data[i]
        dates[i] = day['date']
        for hour in range(24):
            act = day['hours'][str(hour).zfill(2)]
            ix = i*number_of_activities + activities.index(act)
            freqs[ix] = freqs[ix] + 1

    x = [(a, b) for a in dates for b in activities]

    return x, tuple(freqs)

x, y = extract_frequencies(raw_data)

print(x)
print(y)

source = ColumnDataSource(data=dict(x=x, counts=y))

p = figure(x_range=FactorRange(*x), plot_height=300, toolbar_location=None, tools="")

p.vbar(x='x', top ='counts', width=0.9, source=source)

p.y_range.start = 0
p.x_range.range_padding = 0.1
p.xaxis.major_label_orientation = 1
p.xgrid.grid_line_color = None

show(p)

###################3
'''
fruits = ['Apples', 'Pears', 'Nectarines', 'Plums', 'Grapes', 'Strawberries']
years = ['2015', '2016', '2017']

data = {'fruits' : fruits,
        '2015'   : [2, 1, 4, 3, 2, 4],
        '2016'   : [5, 3, 3, 2, 4, 6],
        '2017'   : [3, 2, 4, 4, 5, 3]}

# this creates [ ("Apples", "2015"), ("Apples", "2016"), ("Apples", "2017"), ("Pears", "2015), ... ]
x = [ (fruit, year) for fruit in fruits for year in years ]
y = sum(zip(data['2015'], data['2016'], data['2017']), ()) # like an hstack

source = ColumnDataSource(data=dict(x=x, counts=y))

p = figure(x_range=FactorRange(*x), plot_height=250, title="Fruit Counts by Year",
           toolbar_location=None, tools="")

p.vbar(x='x', top='counts', width=0.9, source=source)

p.y_range.start = 0
p.x_range.range_padding = 0.1
p.xaxis.major_label_orientation = 1
p.xgrid.grid_line_color = None

show(p)



'''

'''

df = pd.DataFrame(data=[1,2,3],
                  index=[dt(2015, 1, 1), dt(2015, 1, 2), dt(2015, 1, 3)],
                  columns=['foo'])
p = figure(plot_width=400, plot_height=400)
p.line(df.index, df['foo'])
p.xaxis.formatter=DatetimeTickFormatter(
        hours=["%d %B %Y"],
        days=["%d %B %Y"],
        months=["%d %B %Y"],
        years=["%d %B %Y"],
    )
p.xaxis.major_label_orientation = pi/4
output_file('myplot.html')
show(p)

# Controls and callbacks

year = Select(title="Year:", value="2010", options=years)
location = Select(title="Location:", value="World", options=locations)

def update():
    ages.data = df[(df.Location == location.value) & (df.Year == int(year.value))]
    #print(location.value)
    #print(year.value)

    pop = df[df.Location == location.value].groupby(df.Year).Value.sum()
    new_known = pop[pop.index <= 2010]
    new_predicted = pop[pop.index >= 2010]
    known.data = dict(x=new_known.index.map(str), y=new_known.values)
    # predicted.data = dict(x=new_predicted.index.map(str), y=new_predicted.values)

year.on_change('value', lambda attr, old, new: update())
location.on_change('value', lambda attr, old, new: update())

update()

controls = column(year, location, width=300)
'''