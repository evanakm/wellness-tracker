from DataModel import DataModel
import datetime as dt
from bson.json_util import dumps

#A higher value means larger reads, but fewer updates
DATA_BUFFER = 10

# TODO: This should take an ObjectID called person_id, not a username, but it takes a username during this refactoring.
class DataCache:
    #def __init__(self, person_id, first_date, last_date):
    def __init__(self, username, first_date, last_date):
        self.dm = DataModel(username) #After integration, this will take person_id, not the other way around.
        self.person_id = self.dm.person_id
        self.first_date = first_date
        self.last_date = last_date

        self.cached_data = None
        self.update_cache()

    def update_cache(self):
        date_array = DataCache.get_date_array(self.first_date, self.last_date)
        self.cached_data = self.dm.get_records_from_dates(self.person_id, date_array)

    def set_dates_and_update_cache_if_necessary(self, new_first_date, new_last_date):
        refresh_data = False

        print('in set dates:')
        print('Type of new_first_date:')
        print(type(new_first_date))
        print('Type of self.first_date:')
        print(type(self.first_date))

        if new_first_date < self.first_date:
            refresh_data = True
            self.first_date = new_first_date - dt.timedelta(days=DATA_BUFFER)

        if new_last_date > self.last_date:
            refresh_data = True
            self.last_date = new_last_date + dt.timedelta(days=DATA_BUFFER)

        if refresh_data:
            self.update_cache()

    def get_serialized_data(self, first_date, last_date):
        dates = DataCache.get_date_array(first_date, last_date)
        relevant_data = [record for record in self.cached_data if dt.date.fromisoformat(record['date']) in dates]

        return dumps(relevant_data)

    def reset(self, first_date, last_date):
        self.first_date = first_date
        self.last_date = last_date
        self.update_cache()

    #TODO: This should maybe go somewhere else, like a utilities folder
    @staticmethod
    def get_date_array(start, end):
        if not (isinstance(start, dt.date) and isinstance(end, dt.date)):
            raise TypeError("start and end must be Dates")

        if start > end:
            raise ValueError("end must come after start.")

        date_del = end - start
        return [start + dt.timedelta(days=i) for i in range(date_del.days + 1)]

