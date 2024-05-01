# Autor : Johanna Luise Koenig
# Datum: 08.04.2024
# Version: 0.2
# Licence: Open Source
# Module Short Description: Generate for the next seven days a weather forecast based on the data from the last seven days and write them in the database

import asyncio
import numpy as np
from database import Database
from datetime import datetime, timedelta
from weather_app import fetch_weather_data
from sklearn.linear_model import LinearRegression

async def get_weather_report(location: str):
    """
    Retrieves the weather report of the last seven days for a given location.

    Args:
        location (str): The location for which to retrieve the weather report.

    Returns:
        dict: A dictionary containing weather data for each of the last seven days.
            Each day's data includes:
                - Maximum temperature
                - Minimum temperature
                - Total precipitation
                - Wind speed
                - Date
                - Station
    """

    # get the data from the database
    data = await fetch_weather_data(location)

    # formatting the data
    day_reports = {"day1": [], "day2":[], "day3":[], "day4":[], "day5":[], "day6":[], "day7":[]}
    for i in range(1, len(data)):
        date = data[i]['time']
        station = data[i]['station']
        max_temp = data[i]['temperature_max']
        min_temp = data[i]['temperature_min']
        prec_sum = data[i]['precipitation_sum']
        wind_speed = data[i]['wind_speed']
        day_reports["day" + str(i)] = [max_temp, min_temp, prec_sum, wind_speed, date, station]
    #print("Wetterdaten:\n", day_reports)
    return day_reports



def get_needed_data(day_reports):
    day1 = [day_reports['day1'][0], day_reports['day1'][1], day_reports['day1'][2], day_reports['day1'][3]]
    day2 = [day_reports['day2'][0], day_reports['day2'][1], day_reports['day2'][2], day_reports['day2'][3]]
    day3 = [day_reports['day3'][0], day_reports['day3'][1], day_reports['day3'][2], day_reports['day3'][3]]
    day4 = [day_reports['day4'][0], day_reports['day4'][1], day_reports['day4'][2], day_reports['day4'][3]]
    day5 = [day_reports['day5'][0], day_reports['day5'][1], day_reports['day5'][2], day_reports['day5'][3]]
    day6 = [day_reports['day6'][0], day_reports['day6'][1], day_reports['day6'][2], day_reports['day6'][3]]
    day7 = [day_reports['day7'][0], day_reports['day7'][1], day_reports['day7'][2], day_reports['day7'][3]]
    return day1, day2, day3, day4, day5, day6, day7


def weather_report(day_reports):
    day1, day2, day3, day4, day5, day6, day7 = get_needed_data(day_reports)
    # Trainingsdata
    X_train = [
        [14.7, 2.9, 0.6, 15.3],
        [21.7, 6.8, 0.2, 14.1],
        [19.7, 10.7, 0.1, 13.7],
        [22.2, 10.4, 0.0, 8.7],
        [26.8, 11.0, 0.0, 7.4],
        [27.0, 11.1, 0.0, 14.5],
        [20.3, 12.7, 4.2, 15.6]
    ]
    y_train = [
        [19, 9, 0.0, 19],
        [15, 8, 0.32, 19],
        [18, 10, 0.0, 13],
        [17, 9, 0.07, 16],
        [19, 9, 0.09, 11],
        [19, 10, 0.17, 13],
        [19, 10, 0.13, 14]
    ]

    # Initate and train model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Funktion zur Vorhersage des Wetters für einen Tag
    def predict_weather(day):
        return model.predict([day])

    # Testdaten für Vorhersage
    test_days = [
        day1,
        day2,
        day3,
        day4,
        day5,
        day6,
        day7
    ]

    # get todays date
    date = datetime.now()

    result = []
    # Vorhersage für die nächsten sieben Tage
    for i, day in enumerate(test_days):
        date = date + timedelta(days=1)
        forecast = model.predict([day])
        forecast[0][2] = max(forecast[0][2], 0)  # Niederschlag nicht negativ machen
        forecast[0][3] = max(forecast[0][3], 0)  # Windgeschwindigkeit nicht negativ machen
        forecast= {
            'time': date.strftime("%Y-%m-%d"),
            'temperature_max': round(forecast[0][0],1),
            'temperature_min': round(forecast[0][1], 1),
            'precipitation_sum': round(forecast[0][2], 1), 
            'wind_speed': round(forecast[0][3], 1), 
            'station': day_reports["day1"][5], 
            'predicted': True
            }
        result.append(forecast)
        #print(f"Vorhersage für Tag {i+1}: {forecast}")
    return result


async def get_weather_forecast(location= 'Stuttgart'):
    db = Database('mongodb+srv://weatherclient:verteilteSysteme@weather.nncm5t4.mongodb.net/weather?retryWrites=true&w=majority&appName=Weather')
    day_reports = await get_weather_report(location)
    result = weather_report(day_reports)
    #print("Ergebnis:\n", result)
    return result

if __name__ == "__main__":
    test = True
    if(test == True):
        test_day_reports = {'day1': [14.7, 2.9, 0.6, 15.3, '2024-04-26', 'Stuttgart'], 'day2': [21.7, 6.8, 0.2, 14.1, '2024-04-27', 'Stuttgart'], 'day3': [19.7, 10.7, 0.1, 13.7, '2024-04-28', 'Stuttgart'], 'day4': [22.2, 10.4, 0.0, 8.7, '2024-04-29', 'Stuttgart'], 'day5': [26.8, 11.0, 0.0, 7.4, '2024-04-30', 'Stuttgart'], 'day6': [27.0, 11.1, 0.0, 14.5, '2024-05-01', 'Stuttgart'], 'day7': [20.3, 12.7, 4.2, 15.6, '2024-05-02', 'Stuttgart'], 'day8': [26.7, 14.8, 2.2, 12.1, '2024-05-03', 'Stuttgart'], 'day9': [28.4, 16.8, 2.7, 11.9, '2024-05-04', 'Stuttgart'], 'day10': [29.6, 18.0, 3.1, 11.7, '2024-05-05', 'Stuttgart'], 'day11': [30.7, 19.3, 3.4, 11.6, '2024-05-06', 'Stuttgart'], 'day12': [31.8, 20.5, 3.7, 11.4, '2024-05-07', 'Stuttgart'], 'day13': [32.9, 21.8, 4.1, 11.3, '2024-05-08', 'Stuttgart'], 'day14': [34.0, 23.0, 4.4, 11.1, '2024-05-09', 'Stuttgart']}
        expected_result = [{'time': '2024-05-03', 'temperature_max': 17.5, 'temperature_min': 8.5, 'precipitation_sum': 0.1, 'wind_speed': 20.3, 'station': 'Stuttgart', 'predicted': True}, {'time': '2024-05-04', 'temperature_max': 17.7, 'temperature_min': 8.9, 'precipitation_sum': 0.2, 'wind_speed': 16.8, 'station': 'Stuttgart', 'predicted': True}, {'time': '2024-05-05', 'temperature_max': 17.9, 'temperature_min': 10.0, 'precipitation_sum': 0.0, 'wind_speed': 14.0, 'station': 'Stuttgart', 'predicted': True}, {'time': '2024-05-06', 'temperature_max': 17.9, 'temperature_min': 9.2, 'precipitation_sum': 0.0, 'wind_speed': 13.7, 'station': 'Stuttgart', 'predicted': True}, {'time': '2024-05-07', 'temperature_max': 18.0, 'temperature_min': 8.8, 'precipitation_sum': 0.1, 'wind_speed': 13.0, 'station': 'Stuttgart', 'predicted': True}, {'time': '2024-05-08', 'temperature_max': 17.9, 'temperature_min': 9.6, 'precipitation_sum': 0.2, 'wind_speed': 13.3, 'station': 'Stuttgart', 'predicted': True}, {'time': '2024-05-09', 'temperature_max': 19.1, 'temperature_min': 10.0, 'precipitation_sum': 0.1, 'wind_speed': 13.9, 'station': 'Stuttgart', 'predicted': True}]
        result = weather_report(test_day_reports)
        if(result==expected_result):
            print('\033[32mForecast works.\033[0m')
        else:
            print('\033[31m \nError in weather forecast!\n\033[0m')
    else:
        asyncio.run(get_weather_forecast())
    print('Finished')