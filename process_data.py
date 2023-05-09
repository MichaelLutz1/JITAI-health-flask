
"""
data = {
    "acceleration":"nil",                   String of x, y, and z data
    "gyro":"nil",                           String of x, y, and z data
    "magnetometer":"nil",                   String of x, y, and z data
    "location":null,                        String
    "activeenergy":0,                       Number
    "restingenergy":0,                      Number
    "battery":-1,                           Number, -1 if unavailable
    "time":"2023-05-05 17:27:03 +0000",     String
    "stepcount":1,                          Number
    "heartrate":61,                         Number
    "participantid":""                      String
}
"""


#data is an array of the above data struct
def process_participant_data(data_arr):
    for d in data_arr:
        print(d["heartrate"])