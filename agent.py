import pymongo
from pymongo import MongoClient
from database_access import *
#import requests
#import requests.auth
#from uuid import uuid4
import urllib.parse
from datetime import datetime
import multiprocessing
import os
import schedule
import logging
import queue
#from agent_messages import *
import calendar


class Agent(multiprocessing.Process):
    participant_id = ""
    client = None
    db = None
    __database_ip_address = ""
    __database_port_number = None
    socket = ""
    logger = None
    
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    def __init__(self, participant_id, database_ip_address,
                 database_port_number):
        #Spawns a new process for each agent
        multiprocessing.Process.__init__(self)
        self.participant_id = participant_id
        self.__database_ip_address = database_ip_address
        self.__database_port_number = database_port_number
       
   

    def run(self):
        self.logger.debug("%s The name is:", self.participant_id)
        self.logger.debug("%s running ...  process id:", os.getpid())
        self.create_database(self.__database_ip_address,
                             self.__database_port_number)
        self.__save_participant_info()
        self.create_progression_collection()
        self.__job()

    #Used to train model at the end of the day
    def __job(self):
        self.logger.debug("%s I'm working...")
       

        while True:
            schedule.run_pending()
            schedule_t.sleep(1)

    
    #Each agent creates its own database 
    def create_database(self, database_ip_address, database_port_number):
        self.logger.debug("%s inside create database")
        try:
            if self.client is None:
                print(database_ip_address)
                print(database_port_number)
                self.client = MongoClient(database_ip_address,
                                          database_port_number,
                                          connect=False)
                self.db = self.client["participant_database_" +
                                      self.participant_id]

                #self.create_heart_rate_data_collection()
                print(self.client.list_database_names())
                weekly_data = self.get_weekly_data_collection()
        except Exception as error:
            print(error)

    def close_agent_db(self):
        if self.db is not None:
            self.client.close()

    

   
    

   


    
    
   
   
   

    def setup_logger(self, name, log_file, level=logging.DEBUG):
        """Function setup as many loggers as you want"""

        handler = logging.FileHandler(log_file)
        handler.setFormatter(self.formatter)

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)

        return logger
