import requests
from datetime import datetime, timedelta


def calc_halfhour_averages(data_arr):
    curr, end = get_start_and_end_dates(data_arr)
    averaged_data = []
    while is_first_date_earlier(curr, end):
        averaged_data.append(average_data(
            data_arr, curr, add_thirty_minutes(curr)))
        curr = add_thirty_minutes(curr)
    return averaged_data


def get_start_and_end_dates(data_arr):
    earliest = None
    latest = None
    for data in data_arr:
        if data is not None:
            if earliest is None and latest is None:
                earliest = data['time']
                latest = data['time']
            else:
                if is_first_date_earlier(data['time'], earliest):
                    earliest = data['time']
                if is_first_date_earlier(latest, data['time']):
                    latest = data['time']
    return earliest, latest


def average_data(data_arr, curr, end):
    data_within_range = get_data_within_range(data_arr, curr, end)

    id = data_arr[0]['participantid']
    halfhour_average = {}
    count = 0
    for data in data_within_range:
        if data['heartrate'] != 0:
            for key, value in data.items():
                if key in halfhour_average:
                    match key:
                        case '_id':
                            continue
                        case 'acceleration':
                            halfhour_average[key] = sum_xyz(
                                halfhour_average[key], value)
                            continue
                        case 'participantid':
                            continue
                        case 'time':
                            continue
                        case 'location':
                            halfhour_average[key] = sum_long_lat(
                                halfhour_average[key], value)
                        case _:
                            halfhour_average[key] += int(value)
                            continue
                    count += 1
                else:
                    if key == 'acceleration':
                        halfhour_average[key] = sum_xyz(
                            None, value)
                    elif key == 'location':
                        halfhour_average[key] = sum_long_lat(None, value)
                    else:
                        halfhour_average[key] = value
                    count = 1
    if count < 28:
        return None
    averaged_data = divide_by_count(id, halfhour_average, count, curr, end)
    averaged_data['weather'] = get_weather(averaged_data['location'])

    return averaged_data


def get_weather(location):
    long, lat = location.split(' ')
    weather = {}
    try:
        r = requests.get(f'https://api.weather.gov/points/{long},{lat}')
        point_info = r.json()
        forecast_link = point_info['properties']['forecastHourly']
        r = requests.get(forecast_link)
        weather_data = r.json()
        weather['temp'] = weather_data['properties']['periods'][0]['temperature']
        weather['precipitation'] = weather_data['properties']['periods'][0]['probabilityOfPrecipitation']['value']
        weather['wind'] = weather_data['properties']['periods'][0]['windSpeed']
        weather['humidity'] = weather_data['properties']['periods'][0]['relativeHumidity']['value']
        return weather
    except:
        print('error')
        return None
    return None


def divide_by_count(id, halfhour_average, count, curr, end):
    processed_averages = {}
    for key, val in halfhour_average.items():
        match key:
            case '_id':
                continue
            case 'weather':
                processed_averages[key] = val
                continue
            case 'acceleration':
                processed_averages[key] = rebuild_xyz(val, count)
                continue
            case 'participantid':
                processed_averages[key] = id
                continue
            case 'time':
                processed_averages[key] = format_time(curr, end)
                continue
            case 'location':
                processed_averages[key] = rebuild_location(val, count)
                continue
            case _:
                processed_averages[key] = round(val / count, 3)
                continue
    return processed_averages


def rebuild_location(val, count):
    long = val[0] / count
    lat = val[1] / count
    return f'{long} {lat}'


def get_data_within_range(data_arr, curr, end):
    data_within_range = []
    for data in data_arr:
        if data is not None:
            time = data['time']
            if is_first_date_earlier(curr, time) and is_first_date_earlier(time, end):
                data_within_range.append(data)
    return data_within_range


def format_time(curr, end):
    day = curr.split(' ')[0]
    curr_time_arr = curr.split(' ')[1].split(':')
    end_time_arr = end.split(' ')[1].split(':')
    start_time = f'{curr_time_arr[0]}:{curr_time_arr[1]}'
    end_time = f'{end_time_arr[0]}:{end_time_arr[1]}'
    return f'{day} {start_time} - {end_time}'


def rebuild_xyz(val, count):
    for idx in range(len(val)):
        average = round((val[idx] / count), 3)
        if average == 0.0:
            val[idx] = 0
        else:
            val[idx] = average
    x_str = f'x:{val[0]} '
    y_str = f'y:{val[1]} '
    z_str = f'z:{val[2]}'
    return x_str + y_str + z_str


def sum_long_lat(initial_val, new_val):
    try:
        new_long_lat = new_val.split(' ')
        new_long = float(new_long_lat[0])
        new_lat = float(new_long_lat[1])
        if initial_val is None:
            return [new_long, new_lat]
        old_long = initial_val[0]
        old_lat = initial_val[1]
    except:
        print('error')
    return [old_long + new_long, old_lat + new_lat]


def sum_xyz(initial_val, new_val):
    new_x, new_y, new_z = split_xyz(new_val)
    if initial_val is None:
        return [new_x, new_y, new_z]
    initial_x = initial_val[0]
    initial_y = initial_val[1]
    initial_z = initial_val[2]
    sum_x = initial_x + new_x
    sum_y = initial_y + new_y
    sum_z = initial_z + new_z
    return [sum_x, sum_y, sum_z]


def split_xyz(st):
    xyz_arr = st.split(' ')
    for idx, val in enumerate(xyz_arr):
        xyz_arr[idx] = val.split(':')[1]
    return float(xyz_arr[0]), float(xyz_arr[1]), float(xyz_arr[2])


def add_thirty_minutes(time):
    date_format = "%Y-%m-%d %H:%M:%S.%f"
    dt = datetime.strptime(time, date_format)
    dt_30_minutes_later = dt + timedelta(minutes=30)
    output_string = dt_30_minutes_later.strftime(date_format)
    return output_string


def is_first_date_earlier(first, second):
    first_date = datetime.strptime(first, "%Y-%m-%d %H:%M:%S.%f")
    second_date = datetime.strptime(second, "%Y-%m-%d %H:%M:%S.%f")
    return first_date <= second_date
