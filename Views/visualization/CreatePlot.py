import pandas as pd
from math import pi
import datetime as dt
from bokeh.io import output_file, show, curdoc
from bokeh.models import DatetimeTickFormatter, Select, FactorRange, ColumnDataSource
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models.widgets import CheckboxGroup, DateRangeSlider
import requests

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

sorted_acts = list(acts)
sorted_acts.sort()
print(sorted_acts)

checkbox_group = CheckboxGroup(labels=sorted_acts, active=[1,2])
date_slider = DateRangeSlider(title="Date Range: ", start=dt.date(2018, 1, 1), end=dt.date.today(), value=(dt.date(2019, 11, 1), dt.date.today()), step=1)

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


def reduce_data_set_by_booleans(bools, dates):
    new_x = [a for (a, b) in zip(x, bools) if b]
    new_y = [a for (a, b) in zip(y, bools) if b]

    return new_x, new_y

def reduce_data_set_by_list(activities, dates):
    bools = [i[1] in activities for i in x]
    return reduce_data_set_by_booleans(bools, dates)

def reduce_data_set_by_indices(indices, dates):
    activities = [sorted_acts[i] for i in indices]
    return reduce_data_set_by_list(activities, dates)

def get_new_data_set():
    url = 'localhost:5400/set_dates'
    data = {'first_date': date_slider.value[0],
            'last_date': date_slider.value[1]}


new_x, new_y = reduce_data_set_by_indices(checkbox_group.active, test_dates)

red_acts = ['goal_3','sleep','tv']

sublist = [i for i in x if i[1] in red_acts]

#print(indices)
#print(sublist)

#new_x = [a for (a, b) in zip(x, indices) if b]
#new_y = [a for (a, b) in zip(y, indices) if b]

source = ColumnDataSource(data=dict(x=new_x, counts=new_y))

p = figure(x_range=FactorRange(*new_x), plot_height=300, toolbar_location=None, tools="")

p.vbar(x='x', top ='counts', width=0.9, source=source)

p.y_range.start = 0
p.x_range.range_padding = 0.1
p.xaxis.major_label_orientation = 1
p.xgrid.grid_line_color = None

#show(p)

# Controls
def update():
    print(checkbox_group.active)
    print(date_slider.value)

    update_x, update_y = reduce_data_set_by_indices(checkbox_group.active, test_dates)

    p.x_range.factors = update_x
    source.data = dict(x=update_x, counts=update_y)

    '''source.data = df[(df.Location == location.value) & (df.Year == int(year.value))]
    #print(location.value)
    #print(year.value)

    pop = df[df.Location == location.value].groupby(df.Year).Value.sum()
    new_known = pop[pop.index <= 2010]
    new_predicted = pop[pop.index >= 2010]
    known.data = dict(x=new_known.index.map(str), y=new_known.values)
    # predicted.data = dict(x=new_predicted.index.map(str), y=new_predicted.values)
    '''

checkbox_group.on_change('active',lambda attr, old, new: update())


controls = column(checkbox_group,date_slider,width=300)

curdoc().add_root(row(p,controls))
#show(row(p,controls))

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