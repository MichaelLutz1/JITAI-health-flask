import queue
import logging
from datetime import datetime
from pymongo import MongoClient
from constants import database_name, database_port, database_ip_address
import json
from bson import ObjectId
__client = None

logger = logging.getLogger('database.log')
message_queue = queue.Queue()


def write_participant_data(data):
    if data["participantid"] == "" or data["participantid"] == None:
        logger.error("No participant id")
        return
    collection = get_db()[database_name][data["participantid"]]
    collection.insert_one(data)

def write_participant_processed_data(data):
    if data["participantid"] == "" or data["participantid"] == None:
        logger.error("No participant id")
        return
    collection = get_db()[database_name]["Processed"][data["participantid"]]
    collection.insert_one(data)

def write_input_data(data):
    if data["participantid"] == "" or data["participantid"] == None:
        logger.error("No participant id")
        return
    collection = get_db()[database_name]["INPUTDATA"]
    filter = {'participantid': data['participantid']}
    new_data = {"$set": {data['type']: data['data']}}
    collection.update_one(filter, new_data, upsert=True)

def get_participants():
    db = get_db()
    collections = db.list_collection_names()
    participants = set()
    for c in collections:
        name = c.split('.')[-1]
        if name != 'INPUTDATA':
            participants.add(name)
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
        collection = db[database_name][participant]
        pipeline = [
        {
            "$group": {
                "_id": None,
                "most_recent_date": { "$max": "$time" },
                "earliest_date": { "$min": "$time" },
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
        data = next(collection.aggregate(pipeline),None)
        latest_date = data['most_recent_date'] 
        latest_collection = collection.find_one({'time':latest_date})
        data['location'] = latest_collection['location']
        response[participant] = data
    return response


def minute_level_data(requested_participants, start_date, end_date):
    db = get_db()
    participant_columns = set()
    participant_data = []
    start_default, end_default = str(datetime(1900,1,1)),str(datetime(9999,12,31))
    query = {
        'Time': {
            '$gte': start_date if start_date else start_default,
            '$lte': end_date if end_date else end_default
        }
    }
    for requested_participant in requested_participants:
        collection = db[database_name]["Processed"][requested_participant]
        if not collection.count_documents({}) == 0:
            first_entry = list(collection.find_one({}, {'_id':0}))
            for key in first_entry:
                participant_columns.add(key)
            all_entries_in_timeframe = list(collection.find(query,{'_id':0}))
            for entry in all_entries_in_timeframe:
                participant_data.append(entry)
    return participant_columns,participant_data
    
def get_input_data():
    db = get_db()
    collection = db[database_name]["INPUTDATA"]
    participants = get_participants()
    res = {}
    for participant in participants:
        data = next(collection.find({'participantid': participant}, {'_id':0, 'participantid':0}),0)
        if data:
            res[participant] = data
    return res





def weekly_data(participants, start_date, end_date, week):

    return


def dialogue_data(participants, start_date, end_date):

    return


def participant_details_data(participants, start_date, end_date):

    return
