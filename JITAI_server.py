from database_access import get_db, request_dashboard_data, write_input_data, get_participants, get_processed_data, database_name, get_raw_data
from constants import COLUMN_ORDER, RAW_COLUMN_ORDER
from flask import Flask, request, render_template, jsonify
import json
import logging
app = Flask(__name__)

database_ip_address = "127.0.0.1"
database_port = 27017
agent_list = []
socket = 49153
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logger = None


def setup_logger(name, log_file, level=logging.DEBUG):
    """Function setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


@app.route('/', methods=['GET', 'POST'])
def home():
    error = None
    if request.method == 'POST':
        # Check if the password is correct
        if request.form['password'] != 'MPAS100':
            error = 'Invalid Credentials. Please try again.'
        else:
            # If the password is correct, redirect to the dashboard
            participants = get_participants()
            return render_template('dashboard.html', participants=participants)
    return render_template('index.html', error=error)


@app.route('/dashboard', methods=['GET', 'POST', 'DELETE'])
def dashboard():
    participants = get_participants()
    if request.method == 'POST':
        return render_template('main_table.html', participants=participants)
    return render_template('dashboard.html', participants=participants)


# fetch data needed to display the dashboard and to write input data
@app.route('/api/dashboard', methods=['GET', 'POST'])
def dashboardData():
    if request.method == "GET":
        try:
            data = request_dashboard_data()
            return jsonify(data)
        except:
            print('error')
    if request.method == 'POST':
        try:
            body = request.json
            write_input_data(body)
            return 'success'
        except:
            print('error', request.data)


# gets participant data from the database to be downloaded as a csv
@app.route('/api/processed_data')
def all_processed_data():
    db = get_db()
    id = request.args['id']
    path = request.args['path']
    paths = {
        'minute_level': 'MINUTE',
        'halfhour_level': 'HALFHOUR'
    }
    collection = db[database_name]['PROCESSED'][paths[path]]
    if id == 'all':
        data_list = list(collection.find({}, {'_id': 0}))
    else:
        data_list = list(collection.find({'participantid': id}, {'_id': 0}))
    data_json = json.dumps(data_list, default=str)
    return data_json


@app.route('/api/raw_data')
def all_raw_data():
    db = get_db()
    id = request.args['id']
    collection = db[database_name]['RAW']
    if id == 'all':
        data_list = list(collection.find({}, {'_id': 0}))
    else:
        data_list = list(collection.find({'participantid': id}, {'_id': 0}))
    data_json = json.dumps(data_list, default=str)
    return data_json


@app.route('/api/data/<data_type>', methods=['POST', 'GET'])
def participantData(data_type):
    participants = get_participants()
    if request.method == 'GET':
        requested_participant = request.args.get('participant')
        start_date = request.args.get('start_date') if request.args.get(
            'start_date') != 'undefined' else None
        end_date = request.args.get('end_date')if request.args.get(
            'end_date') != 'undefined' else None
        offset = int(request.args.get('offset'))
        if data_type == 'raw_data':
            participant_data, num_rows = get_raw_data(
                requested_participant, start_date, end_date, offset)
            column_order = RAW_COLUMN_ORDER
            return render_template('raw_data_table.html', participant_columns=column_order, participant_data=participant_data, num_rows=num_rows)
        else:
            participant_data, num_rows = get_processed_data(
                requested_participant, start_date, end_date, data_type, offset)
            column_order = COLUMN_ORDER
            return render_template('data_table.html', participant_columns=column_order, participant_data=participant_data, num_rows=num_rows)
    return render_template('halfhour_level.html', participants=participants, num_rows=0)


# Fetches the minute level data from the database and renders it in a table
@app.route('/minute_level', methods=['POST', 'GET'])
def minute_level_page():
    participants = get_participants()
    if request.method == 'POST':
        data = request.json
        requested_participant = data.get("participant")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        offset = data.get('offset')
        participant_data, num_rows = get_processed_data(
            requested_participant, start_date, end_date, 'MINUTE', offset)
        return render_template('data_table.html', participant_columns=COLUMN_ORDER, participant_data=participant_data, num_rows=num_rows)
    return render_template('minute_level.html', participants=participants, num_rows=0)

# Fetches the half-hour data from the database and renders it in a table


@app.route('/halfhour_level', methods=['POST', 'GET'])
def halfhour_level_page():
    participants = get_participants()
    if request.method == 'POST':
        data = request.json
        requested_participant = data.get("participant")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        offset = data.get('offset')
        participant_data, num_rows = get_processed_data(
            requested_participant, start_date, end_date, 'HALFHOUR', offset)
        return render_template('data_table.html', participant_columns=COLUMN_ORDER, participant_data=participant_data, num_rows=num_rows)
    return render_template('halfhour_level.html', participants=participants, num_rows=0)

# Fetches the raw data from the database and displays it in a table


@app.route('/raw_data', methods=['POST', 'GET'])
def raw_data_page():
    participants = get_participants()
    if request.method == 'POST':
        data = request.json
        requested_participant = data.get("participant")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        offset = data.get('offset')
        participant_data, num_rows = get_raw_data(
            requested_participant, start_date, end_date, offset)
        return render_template('data_table.html', participant_columns=RAW_COLUMN_ORDER, participant_data=participant_data, num_rows=num_rows)
    return render_template('raw_data.html', participants=participants, num_rows=0)


# Takes in the data from the watch and processes it
@app.route("/api/watch", methods=["POST", "GET"])
def MPAS_page():
    global logger

    if request.method == "POST":
        try:
            content = request.json
            input_data = request_dashboard_data()
            import process_data
            process_data.process_participant_data(content)
            process_data.process_minute_level(content, input_data)
            # process_data.process_halfhour_level(content)
            logger.info("Processed data for participant")
            return "OK"
        except:
            print("Error", request.data)
    else:
        participants = get_participants()
        return render_template("MPAS.html", participants=participants)


# Initialize some stuff before running the app
# message_queue = queue.Queue()
logger = setup_logger('main_server', 'main_server.log')
database_logger = setup_logger("database", "database.log")
get_db()
# create_data()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=9001)
