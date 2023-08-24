import database_access
import data_calculations
from pymongo import MongoClient


"""
data = {
    "acceleration":"nil",                   String of x, y, and z data
    "gyro":"nil",                           String of x, y, and z data
    "magnetometer":"nil",                   String of x, y, and z data
    "location":null,                        String
    "activeenergy":0,                       Number
    "restingenergy":0,                      Number
    "battery":-1,                           Number, -1 if unavailable
    "time":"2023-05-05 17:27:03.0000",      String
    "stepcount":1,                          Number
    "heartrate":61,                         Number
    "participantid":""                      String
}
"""
# converts "nil", "", "nan" to None


def is_nullish(thing):
    if thing == "nil" or thing == "" or thing == "nan":
        return None
    return thing

# data is an array of the above data struct


def process_participant_data(data_arr):
    for data in data_arr:
        for key in data:
            data[key] = is_nullish(data[key])
        database_access.write_participant_data(data)


def process_minute_level(data_arr, input_data):
    for data in data_arr:
        processed_data = perform_calculations(data, input_data)
        database_access.write_participant_processed_data(
            processed_data, 'MINUTE')


def perform_calculations(data, input_data=None):
    for key in data:
        data[key] = is_nullish(data[key])

    processed_data = {}
    for key, value in data.items():
        processed_data[key] = value
    processed_data["vectormagnitude"] = data_calculations.calcVM(
        data['acceleration'])
    processed_data['enmo'] = data_calculations.calcENMO(
        processed_data['vectormagnitude'])
    processed_data['totalenergy'] = round(data['restingenergy'] +
                                          data['activeenergy'], 4)
    return processed_data


def process_halfhour_level(data_arr):
    import half_hour_averages
    processed_data_arr = half_hour_averages.calc_halfhour_averages(
        data_arr)
    for data in processed_data_arr:
        if data is not None:
            processed_data = perform_calculations(data)
            processed_data['weather'] = data['weather']
            database_access.write_participant_processed_data(
                processed_data, 'HALFHOUR')
