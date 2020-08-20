
from database_access import *
from agent import *
from flask import Flask, abort, request, render_template, redirect
import json
import HTML
import queue
import logging
app = Flask(__name__)

database_ip_address = "127.0.0.1"
database_port = 27017
agent_list = []
socket = 49153
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
message_queue = queue.Queue()
logger = None
participant_id_list = []

@app.before_first_request
def declareStuff():
    global message_queue, logger
    message_queue = queue.Queue()
    logger = setup_logger('main_server', 'main_server.log')
    logger.debug("main id %s", id(message_queue))
    get_db()
    create_data()


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


def get_dashboard_cell_color(color_scheme, data):
    # color_scheme [(start,end, color)...]
    for color_range in color_scheme:
        start, end, color = color_range
        if type(data) is not str:
            if start <= float(data) and data <= end:
                return color
    return "white"


"""

Registers the participants and creates a new agent for each user

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




if __name__ == '__main__':

    app.run(host='127.0.0.1', debug=True, port=9001)
