import queue
import logging
from datetime import datetime, timedelta
from pymongo import MongoClient
from constants import database_name, database_port, database_ip_address
__client = None

logger = logging.getLogger('database.log')
message_queue = queue.Queue()


def write_participant_data(data):
    if data["participantid"] == "" or data["participantid"] is None:
        logger.error("No participant id")
        return
    collection = get_db()[database_name]['RAW']
    collection.insert_one(data)


def write_participant_processed_data(data, type):
    if data["participantid"] == "" or data["participantid"] is None:
        logger.error("No participant id")
        return
    collection = get_db()[database_name]["PROCESSED"][type]
    collection.insert_one(data)


def write_input_data(data):
    if data["participantid"] == "" or data["participantid"] is None:
        logger.error("No participant id")
        return
    collection = get_db()[database_name]["INPUTDATA"]
    filter = {'participantid': data['participantid']}
    new_data = {"$set": {data['type']: data['data']}}
    collection.update_one(filter, new_data, upsert=True)


def get_participants():
    db = get_db()
    participants = set()
    cursor = db[database_name]['RAW'].find({}, {'_id': 0, 'participantid': 1})

    for doc in cursor:
        participants.add(doc['participantid'])
    return participants


def get_db():
    # ensure there's only one instance of MongoDB running
    global __client
    if __client is None:
        __client = MongoClient(database_ip_address,
                               database_port,
                               connect=False)
    return __client[database_name]


def close_db():
    global __client
    if __client is not None:
        __client.close()


def delete_data():
    db = get_db()
    db.participants.delete_many({})
    db.participant_tokens.delete_many({})


def create_data():
    db = get_db()
    data = db["data"]
    close_db()


def get_dialogue():
    db = get_db()
    if "dialogue" not in db.list_collection_names():
        dialogue = db["dialogue"]
    return db["dialogue"]


def get_participant_info():
    db = get_db()
    if "participant_info" not in db.list_collection_names():
        participant_info = db["participant_info"]
    return db["participant_info"]


def insert_participant_info(nudge_text, participant_id):
    participant_info_collection = get_participant_info()
    participant_info_collection.insert_one({
        "participant_id": participant_id,
        "nudge_text": nudge_text
    })
    close_db()


def get_participant_details(number):
    participant_info_collection = get_participant_info()
    query = {"number": number}
    participant_details = participant_info_collection.find(query)
    for element in participant_details:
        name = element['name']
        number = element['number']
        participant_id = element['participant_id']
        socket = element['socket']
    close_db
    return name, number, participant_id, socket


def request_dashboard_data():
    db = get_db()
    response = {}
    participants = get_participants()
    for participant in participants:
        data = get_start_and_end_dates(participant)
        latest_date = data['most_recent_date']
        latest_collection = db[database_name]['RAW'].find_one(
            {'time': latest_date, 'participantid': participant})
        data['location'] = latest_collection['location']
        response[participant] = data
    return response


def get_processed_data(requested_participant, start_date, end_date, type, offset):
    db = get_db()
    participant_data = []
    num_rows = 0
    start_default, end_default = str(
        datetime(1900, 1, 1)), str(datetime(9999, 12, 31))
    collection = db[database_name]["PROCESSED"][type]
    if requested_participant == 'all':
        starting_id = collection.find({
            'Time': {
                '$gte': start_date if start_date else start_default,
                '$lte': end_date if end_date else end_default
            }
        }).sort('_id', 1)
        list_starting = starting_id
        print(offset)
        last_id = starting_id[offset]['_id']
        query = {
            '_id': {
                '$gte': last_id
            },
            'Time': {
                '$gte': start_date if start_date else start_default,
                '$lte': end_date if end_date else end_default
            }
        }
    else:
        starting_id = collection.find({
            'participantid': requested_participant,
            'Time': {
                '$gte': start_date if start_date else start_default,
                '$lte': end_date if end_date else end_default
            }
        }).sort('_id', 1)
        last_id = starting_id[offset]['_id']
        query = {
            '_id': {
                '$gte': last_id
            },
            'participantid': requested_participant,
            'Time': {
                '$gte': start_date if start_date else start_default,
                '$lte': end_date if end_date else end_default
            }
        }
    if not collection.count_documents({}) == 0:
        all_entries_in_timeframe = list(
            collection.find(query).sort('_id', 1).limit(10))
        num_rows += collection.count_documents(query)
        for entry in all_entries_in_timeframe:
            participant_data.append(entry)
    return participant_data, num_rows


def get_input_data():
    db = get_db()
    collection = db[database_name]["INPUTDATA"]
    participants = get_participants()
    res = {}
    for participant in participants:
        data = next(collection.find({'participantid': participant}, {
                    '_id': 0, 'participantid': 0}), 0)
        if data:
            res[participant] = data
    return res


# def calc_halfhour_averages(id):
#     data = get_start_and_end_dates(id)
#     curr = data['earliest_date']
#     end = data['most_recent_date']
#     averaged_data = []
#     while compare_date(curr, end):
#         averaged_data.append(average_data(id, curr, add_thirty_minutes(curr)))
#         curr = add_thirty_minutes(curr)
#     return []
#
#
# def average_data(id, curr, end):
#     db = get_db()
#     query = {
#         'participantid': id,
#         'Time': {
#             '$gte': curr,
#             '$lte': end,
#         }
#     }
#     average_cursor = db[database_name]['PROCESSED']['MINUTE'].find(query, {
#         '_id': 0})
#     halfhour_average = {}
#     count = 0
#     for data in average_cursor:
#         print(average_cursor)
#         if data['Heartrate'] != 0:
#             for key, value in data.items():
#                 if key in halfhour_average:
#                     match key:
#                         case 'Accelerometery':
#                             halfhour_average[key] = sum_xyz(
#                                 halfhour_average[key], value)
#                             continue
#                         case 'participantid':
#                             continue
#                         case 'Time':
#                             continue
#                         case _:
#                             continue
#                             halfhour_average[key] += int(value)
#                     count += 1
#                 else:
#                     if key == 'Accelerometery':
#                         halfhour_average[key] = sum_xyz(
#                             None, value)
#                     else:
#                         halfhour_average[key] = value
#                     count = 1
#     # if count < 28:
#     #     return None
#     # else:
#     return divide_by_count(id, halfhour_average, count, curr, end)
#
#
# def divide_by_count(id, halfhour_average, count, curr, end):
#     processed_averages = {}
#     for key, val in halfhour_average.items():
#         match key:
#             case 'Accelerometery':
#                 processed_averages[key] = rebuild_xyz(val, count)
#                 continue
#             case 'participantid':
#                 processed_averages[key] = id
#                 continue
#             case 'Time':
#                 processed_averages[key] = format_time(curr, end)
#                 continue
#             case _:
#                 continue
#     return processed_averages
#
# def format_time(curr, end):
#     # print(curr, end)
#     return curr
#
#
#
# def rebuild_xyz(val, count):
#     for idx in range(len(val)):
#         average = round((val[idx] / count), 3)
#         if average == 0.0:
#             val[idx] = 0
#         else:
#             val[idx] = average
#     x_str = f'x:{val[0]} '
#     y_str = f'y:{val[1]} '
#     z_str = f'z:{val[2]}'
#     return x_str + y_str + z_str
#
#
# def sum_xyz(initial_val, new_val):
#     new_x, new_y, new_z = split_xyz(new_val)
#     if initial_val is None:
#         return [new_x, new_y, new_z]
#     initial_x = initial_val[0]
#     initial_y = initial_val[1]
#     initial_z = initial_val[2]
#     sum_x = initial_x + new_x
#     sum_y = initial_y + new_y
#     sum_z = initial_z + new_z
#     return [sum_x, sum_y, sum_z]
#
#
# def split_xyz(st):
#     xyz_arr = st.split(' ')
#     for idx, val in enumerate(xyz_arr):
#         xyz_arr[idx] = val.split(':')[1]
#     return float(xyz_arr[0]), float(xyz_arr[1]), float(xyz_arr[2])
#
#
# def add_thirty_minutes(time):
#     date_format = "%Y-%m-%d %H:%M:%S.%f"
#     dt = datetime.strptime(time, date_format)
#     dt_30_minutes_later = dt + timedelta(minutes=30)
#     output_string = dt_30_minutes_later.strftime(date_format)
#     return output_string
#
#
# def compare_date(first, second):
#     first_date = datetime.strptime(first, "%Y-%m-%d %H:%M:%S.%f")
#     second_date = datetime.strptime(second, "%Y-%m-%d %H:%M:%S.%f")
#     return first_date < second_date


def get_start_and_end_dates(id):
    db = get_db()
    collection = db[database_name]['RAW']
    pipeline = [
        {
            '$match': {'participantid': id},
        },
        {
            "$group": {
                "_id": None,
                "most_recent_date": {"$max": "$time"},
                "earliest_date": {"$min": "$time"},
            }
        },
        {
            "$project": {
                "_id": 0,
                "most_recent_date": 1,
                "earliest_date": 1,
            }
        }
    ]
    data = next(collection.aggregate(pipeline), None)
    return data


def weekly_data(participants, start_date, end_date, week):

    return


def dialogue_data(participants, start_date, end_date):

    return


def participant_details_data(participants, start_date, end_date):

    return
