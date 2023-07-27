
from database_access import *
from flask import Flask, abort, request, render_template, redirect, jsonify
import json
# import HTML
import queue
import logging
app = Flask(__name__)

database_ip_address = "127.0.0.1"
database_port = 27017
agent_list = []
socket = 49153
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logger = None
participant_id_list = []


def setup_logger(name, log_file, level=logging.DEBUG):
    """Function setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    participants = get_participants()
    if request.method == 'POST':
        return render_template('main_table.html', participants = participants)
    return render_template('dashboard.html', participants=participants)

@app.route('/inputdata', methods=['GET', 'POST'])
def inputdata():
    if request.method == "GET":
        try:
            inputdata_list = get_input_data()
            return inputdata_list
        except:
            print('error')
    if request.method == 'POST':
        try:
            body = request.json
            write_input_data(body)
            return 'success'
        except:
            print('error', request.data)



@app.route('/dashboardapi', methods=['GET', 'POST'])
def dashboardapi():
    if request.method == 'GET':
        data = request_dashboard_data()
        json_data = jsonify(data)
        return json_data


# @app.route('/dashboard', methods=['POST', 'GET'])
# def stats_summ():
#     participants = get_participants()
#     if request.method == "POST":

#         requested_id = request.form["participants"]
#         start_date = request.form["start_date"]
#         end_date = request.form["end_date"]

#         participant_data = request_dashboard_data(
#             requested_id, start_date, end_date)
#         return render_template('dashboard_results.html', data=participants, participant_data=participant_data)
#     else:
#         return render_template('dashboard_results.html', data=participants)



@app.route('/minute_level', methods=['POST', 'GET'])
def minute_level_page():
    participants = get_participants()
    if request.method == 'POST':
        column_order = ['participantid', 'Time', 'Heartrate','Accelerometery','Vector Magnitude', 'ENMO', 'Gyroscope', 'Magnetometer', 'Step Count', 'Active Energy', 'Resting Energy', 'Total Energy', 'Sitting Time']
        data = request.json
        requested_participants = data.get("participant")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        if requested_participants == 'all':
            requested_participants = [participant for participant in participants]
        else:
            requested_participants = [requested_participants]
        
        participant_columns, participant_data = minute_level_data(
            requested_participants, start_date, end_date)
        participant_columns = column_order
        return render_template('minute_table.html', participant_columns=participant_columns, participant_data=participant_data)
    return render_template('minute_level.html', participants=participants)


@app.route("/MPAS", methods=["POST", "GET"])
def MPAS_page():
    global logger

    if request.method == "POST":
        try:
            content = request.json
            input_data = get_input_data()
            import process_data
            process_data.process_participant_data(content)
            process_data.process_minute_level(content, input_data)
            return "OK"
        except:
            print("Error", request.data)
    else:
        participants = get_participants()
        print("participants: ", participants)
        return render_template("MPAS.html", participants=participants)


# Initialize some stuff before running the app
# message_queue = queue.Queue()
logger = setup_logger('main_server', 'main_server.log')
database_logger = setup_logger("database", "database.log")
get_db()
# create_data()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=9001)


"""
@app.route("/message", methods=['GET', 'POST'])
def incoming_message():
    # Respond to incoming messages with a friendly SMS.
    # Start our response
    global logger
    logger.debug("%s inside post message")
    content = request.json
    
    print(content['nudge_text'])
    insert_participant_info(content['particiapnt_id'], content['nudge_text'])
    

    return 'OK'


def get_dashboard_cell_color(color_scheme, data):
    # color_scheme [(start,end, color)...]
    for color_range in color_scheme:
        start, end, color = color_range
        if type(data) is not str:
            if start <= float(data) and data <= end:
                return color
    return "white"


"""

# Registers the participants and creates a new agent for each user

"""


@app.route('/register', methods=['POST', 'GET'])
def register():
    agent = None
    global participant_counter, database_ip_address, database_port, agent_list,socket, logger
    # Code to create an agent object and pass the port number and Id
    #participant_id = "P" + str(participant_counter)
    
    participant_id_list.append(p_id)

    
    logger.debug("pa_barriers %s", pa_barriers)
    participant_id = p_id

    agent = Agent(participant_id, database_ip_address, database_port,)
    agent.start()
    agent_list.append(agent)
    insert_participant_info(name, number, participant_id, socket)
    close_db()
    participant_counter = participant_counter + 1
    socket = socket + 1
    #database_port = database_port + 1
    return "Congratulations! You are now a registered user"


@app.route('/dashboard')
def dashboard():

    return render_template('dashboard.html', data = participant_id_list)


@app.route('/dialogue')
def dialogue():

    return render_template('dialogue.html', data = participant_id_list)


@app.route('/participant_details')
def participant_details():

    return render_template('participant_details.html')


@app.route('/weekly_stats')
def weekly_stats():

    return render_template('weekly_stats.html')


@app.route('/dashboard', methods=['POST', 'GET'])
def stats_summ():
    participants = request.form["participants"]
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]

    html_text = "<par>Dashboard</par><br><par>Summaries</par><br>"
    participant_columns, participant_data, participant_colors = all_dashboard_data(
        participants, start_date, end_date)
    close_db()

    return render_template('dashboard_results.html', participant_columns=participant_columns, participant_data=participant_data)


@app.route('/weekly_stats', methods=['POST', 'GET'])
def weekly_summ():
    participants = request.form["participants"]
    week = request.form["weeks"]
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]

    html_text = "<par>Dashboard</par><br><par>Summaries</par><br>"
    participant_columns, participant_data, participant_colors = weekly_data(
        participants, start_date, end_date, week)
    close_db()

    return render_template('weekly_results.html', participant_columns=participant_columns, participant_data=participant_data)


@app.route('/dia_summ', methods=['POST', 'GET'])
def dia_summ():
    participants = request.form["dia_participants"]
    start_date = request.form["dia_start_date"]
    end_date = request.form["dia_end_date"]

    #html_text = "<par>Dashboard</par><br><par>Summaries</par><br>"
    participant_columns, participant_data = dialogue_data(
        participants, start_date, end_date)

    html_text = "<par>Participant Messages</par><br>"
    participant_table = HTML.Table(header_row=participant_columns)
    for participant_stats in participant_data:
        participant_row_cells = []
        participant_table.rows.append(participant_stats)
    html_text += str(participant_table)
    close_db()
    return html_text


@app.route('/participant_details', methods=['POST', 'GET'])
def stats():
    participants = request.form["participants"]
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]

    html_text = "<par>Dashboard</par><br><par>Summaries</par><br>"
    participant_details = participant_details_data(
        participants, start_date, end_date)
    return render_template('participant_results.html', participant_details=participant_details)


"""
