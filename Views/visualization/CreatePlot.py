import datetime as dt
from bokeh.io import show, curdoc
from bokeh.models import FactorRange, ColumnDataSource
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models.widgets import CheckboxGroup, DateRangeSlider
from DataCache import DataCache
import json

#---------- HELPER FUNCTIONS ----------#


def get_unique_activities(data):
    activities = set()

    for day in data:
        for i in range(24):
            activities.add(day['hours'][str(i).zfill(2)])

    return activities

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

def reduce_data_set_by_booleans(bools, x_vals, y_vals):
    new_x_vals = [a for (a, b) in zip(x_vals, bools) if b]
    new_y_vals = [a for (a, b) in zip(y_vals, bools) if b]

    return new_x_vals, new_y_vals

def reduce_data_set_by_list(activities, x_vals, y_vals):
    bools = [i[1] in activities for i in x_vals]
    return reduce_data_set_by_booleans(bools, x_vals, y_vals)

def reduce_data_set_by_indices(indices, x_vals, y_vals, activity_list):
    activities = [activity_list[i] for i in indices]
    return reduce_data_set_by_list(activities, x_vals, y_vals)

def unwrap_parameter(parameter_name):
    args = curdoc().session_context.request.arguments
    parameter = args.get(parameter_name)
    return parameter[0].decode("utf-8")


#---------- INCOMING PARAMETERS FROM HTTP REQUEST ----------#

username = unwrap_parameter('username')
start_date = unwrap_parameter('start_date')
end_date = unwrap_parameter('end_date')

#---------- DEFINITION OF STRUCTURES ----------#

date_slider = DateRangeSlider(title="Date Range: ", start=dt.date(2019, 10, 1), end=dt.date.today(),
                              value=(dt.date.fromisoformat(start_date), dt.date.fromisoformat(end_date)), step=1)

dc = DataCache(username,date_slider.value[0],date_slider.value[1])

data_set = json.loads(dc.get_serialized_data(date_slider.value[0],date_slider.value[1]))

#----------#

acts = get_unique_activities(data_set)
sorted_acts = list(acts) #This needs to persist outside of the update() function below.
sorted_acts.sort()

checkbox_group = CheckboxGroup(labels=sorted_acts, active=[1,2])

#----------#

x, y = extract_frequencies(data_set)
new_x, new_y = reduce_data_set_by_indices(checkbox_group.active, x, y, sorted_acts)
source = ColumnDataSource(data=dict(x=new_x, counts=new_y))

#---------- CREATION OF BOKEH STRUCTURES ----------#

p = figure(x_range=FactorRange(*new_x), plot_height=300, toolbar_location=None, tools="", min_border_bottom=80)
p.vbar(x='x', top ='counts', width=0.9, source=source)

p.y_range.start = 0
p.x_range.range_padding = 0.1
p.xaxis.major_label_orientation = 1
p.xgrid.grid_line_color = None

# Controls
def update_checkbox():

    #I'm getting strange behaviour. Sometimes this is returning an int, sometimes a date
    if isinstance(date_slider.value[0], dt.date):
        start_date = date_slider.value[0]
    else:
        start_date = dt.date.fromtimestamp(date_slider.value[0] / 1000)

    if isinstance(date_slider.value[1], dt.date):
        end_date = date_slider.value[1]
    else:
        end_date = dt.date.fromtimestamp(date_slider.value[1] / 1000)


    data_from_cache = json.loads(dc.get_serialized_data(start_date, end_date))
    x, y = extract_frequencies(data_from_cache)

    update_x, update_y = reduce_data_set_by_indices(checkbox_group.active, x, y, checkbox_group.labels)

    # The non-zero is a workaround for strange bokeh behaviour
    if len(update_x) != 0:
        p.x_range.factors = update_x
        source.data = dict(x=update_x, counts=update_y)


def update_slider():
    #I'm getting strange behaviour. Sometimes this is returning an int, sometimes a date
    if isinstance(date_slider.value[0], dt.date):
        start_date = date_slider.value[0]
    else:
        start_date = dt.date.fromtimestamp(date_slider.value[0] / 1000)

    if isinstance(date_slider.value[1], dt.date):
        end_date = date_slider.value[1]
    else:
        end_date = dt.date.fromtimestamp(date_slider.value[1] / 1000)

    dc.set_dates_and_update_cache_if_necessary(start_date, end_date)

    new_data = json.loads(dc.get_serialized_data(start_date, end_date))
    x, y = extract_frequencies(new_data)

    new_acts = get_unique_activities(new_data)
    new_sorted_acts = list(new_acts)
    new_sorted_acts.sort()

    print(new_sorted_acts)

    indices = [i for i in range(len(new_sorted_acts)) if new_sorted_acts[i] in checkbox_group.active]

    checkbox_group.labels = new_sorted_acts
    checkbox_group.active = indices

    update_x, update_y = reduce_data_set_by_indices(checkbox_group.active, x, y, new_sorted_acts)

    # The non-zero is a workaround for strange bokeh behaviour
    if len(update_x) != 0:
        p.x_range.factors = update_x
        source.data = dict(x=update_x, counts=update_y)


checkbox_group.on_change('active',lambda attr, old, new: update_checkbox())
date_slider.on_change('value',lambda attr, old, new: update_slider())


controls = column(checkbox_group,date_slider,width=300)

curdoc().add_root(row(p,controls))

#show(row(p,controls))

