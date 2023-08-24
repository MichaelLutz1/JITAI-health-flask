import queue
import logging
from datetime import datetime
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


def request_dashboard_data():
    db = get_db()
    response = {}
    participants = get_participants()
    for participant in participants:
        data = get_start_and_end_dates(participant)
        latest_date = data['most_recent_date']
        query = {'time': latest_date, 'participantid': participant}
        latest_collection = db[database_name]['RAW'].find_one(query)
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
        query = {
            'time': {
                '$gte': start_date if start_date else start_default,
                '$lte': end_date if end_date else end_default
            }
        }
    else:
        query = {
            'participantid': requested_participant,
            'time': {
                '$gte': start_date if start_date else start_default,
                '$lte': end_date if end_date else end_default
            }
        }
    if not collection.count_documents({}) == 0:
        all_entries_in_timeframe = list(
            collection.find(query).sort('_id', 1).skip(offset).limit(10))
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
