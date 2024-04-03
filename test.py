# connect to mongodb and read data

import pymongo

database_ip_address = "127.0.0.1"
database_port = 27017


def main():
    # connect to mongodb
    client = pymongo.MongoClient(database_ip_address,
                                 database_port,
                                 connect=False)
    db = client['JITAI_MPAS']
    collection = db['JITAI_MPAS']['RAW']
    print('connect to mongodb success')

    # read data
    for item in collection.find({'participantid': 'Cora2'}).limit(10):
        print(item)

    # close connection
    client.close()
    print('close connection')


main()
