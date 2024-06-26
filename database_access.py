import queue
import logging
from datetime import datetime
from pymongo import MongoClient
from constants import database_name, database_port, database_ip_address, offset_amount
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


def get_raw_data(requested_participant, start_date, end_date, offset=0):
    db = get_db()
    participant_data = []
    dbTable = "RAW"
    num_rows = 0
    start_default, end_default = str(
        datetime(1900, 1, 1)), str(datetime(9999, 12, 31))
    collection = db[database_name][dbTable]
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
            collection.find(query).sort('_id', 1).skip(offset).limit(offset_amount))
        num_rows += collection.count_documents(query)
        for entry in all_entries_in_timeframe:
            participant_data.append(entry)
    return participant_data, num_rows


def get_processed_data(requested_participant, start_date, end_date, type, offset=0):
    db = get_db()
    participant_data = []
    num_rows = 0
    dbTable = "MINUTE" if type == "minute_level" else "HALFHOUR"
    start_default, end_default = str(
        datetime(1900, 1, 1)), str(datetime(9999, 12, 31))
    collection = db[database_name]["PROCESSED"][dbTable]
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
            collection.find(query).sort('_id', 1).skip(offset).limit(offset_amount))
        num_rows += collection.count_documents(query)
        for entry in all_entries_in_timeframe:
            participant_data.append(entry)
    return participant_data, num_rows


def request_dashboard_data():
    db = get_db()
    response = {}
    participants = get_participants()
    for participant in participants:
        data = get_start_and_end_dates(participant)
        response[participant] = data
        input_data = get_input_data(participant)
        if input_data:
            response[participant].update(input_data)
    return response


def get_input_data(participant):
    db = get_db()
    collection = db[database_name]["INPUTDATA"]
    data = next(collection.find({'participantid': participant}, {
        '_id': 0, 'participantid': 0}), 0)
    return data


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
