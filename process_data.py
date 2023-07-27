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
#converts "nil", "", "nan" to None
def is_nullish(thing):
    if thing=="nil" or thing=="" or thing=="nan":
        return None
    return thing

#data is an array of the above data struct
def process_participant_data(data_arr):
    for data in data_arr:
        for key in data:
            data[key] = is_nullish(data[key])
        database_access.write_participant_data(data)

def process_minute_level(data_arr, input_data):
    for data in data_arr:
        processed_data = perform_calculations(data, input_data)
        database_access.write_participant_processed_data(processed_data)
    
def perform_calculations(data, input_data):
    for key in data:
        data[key] = is_nullish(data[key])

    print(input_data)
    processed_data = {}
    processed_data['participantid'] = data['participantid']
    processed_data['Time'] = data['time']
    processed_data["Vector Magnitude"] = data_calculations.calcVM(data['acceleration'])
    processed_data['ENMO'] = data_calculations.calcENMO(processed_data['Vector Magnitude'])
    processed_data['Accelerometery'] = data['acceleration']
    processed_data['Heartrate'] = data['heartrate']
    processed_data['Gyroscope'] = data['gyro']
    processed_data['Magnetometer'] = data['magnetometer']
    processed_data['Step Count'] = data['stepcount']
    processed_data['Active Energy'] = data['activeenergy']
    processed_data['Resting Energy'] = data['restingenergy']
    processed_data['Total Energy'] = data['restingenergy'] + data['activeenergy']
    processed_data['Sitting Time'] = data['sittingtime']
    return processed_data



