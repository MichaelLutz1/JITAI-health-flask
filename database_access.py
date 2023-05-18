from pymongo import MongoClient
from constants import database_name, database_port, database_ip_address
import json
from bson import ObjectId
__client = None
from datetime import *
import logging
import queue

logger = logging.getLogger('database.log')
message_queue = queue.Queue()

def write_participant_data(data):
    if data["participantid"] == "" or data["participantid"] == None:
        logger.error("No participant id")
        return
    collection = get_db()[database_name][data["participantid"]]
    collection.insert_one(data)
    
    
def get_participants():
    db = get_db()
    collections = db.list_collection_names()
    return [c.split('.', 1)[1] for c in collections]


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
    if "dialogue" not in db.collection_names():
        dialogue = db["dialogue"]
    return db["dialogue"]


def get_participant_info():
    db = get_db()
    if "participant_info" not in db.collection_names():
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


def all_dashboard_data(participants, start_date, end_date):
    
    return 


def weekly_data(participants, start_date, end_date, week):


    return 

def dialogue_data(participants, start_date, end_date):
    
    return 


def participant_details_data(participants, start_date, end_date):

    return 
