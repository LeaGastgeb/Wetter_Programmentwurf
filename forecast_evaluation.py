# Autor : Johanna Luise Koenig
# Datum: 30.04.2024
# Version: 0.1
# Licence: Open Source
# Module Short Description: Evaluate the results of the weather forecast

import asyncio
import numpy as np
from database import Database
from datetime import datetime, timedelta
from weather_app import fetch_weather_data
from sklearn.linear_model import LinearRegression
from own_weather_forecast import get_weather_forecast


def real_data():
    """
        Function which return real data - must be adjusted manually
    """
    # day = [max_temp, min_temp, prec_sum, wind_speed]
    day1 = [23, 12, 0.2, 14]
    day2 = [15, 9, 0.1, 25]
    day3 = [17, 5, 0.0, 26]
    day4 = [16, 6, 0.3, 9]
    day5 = [20, 7, 0.4, 17]
    day6 = [19, 7, 0.1, 12]
    day7 = [10, 9, 0.0, 25]
    day8 = [13, 7, 0.1, 28] # day8 for analysing the results
    return day1, day2, day3, day4, day5, day6, day7, day8

def formate_weather_forecast():
    forecast = asyncio.run(get_weather_forecast())
    print('forecast: ', forecast)
    day_reports = {"day1": [], "day2":[], "day3":[], "day4":[], "day5":[], "day6":[], "day7":[]}
    for i in range(1, len(forecast)):
        date = forecast[i]['time']
        station = forecast[i]['station']
        max_temp = forecast[i]['temperature_max']
        min_temp = forecast[i]['temperature_min']
        prec_sum = forecast[i]['precipitation_sum']
        wind_speed = forecast[i]['wind_speed']
        day_reports["day" + str(i)] = [max_temp, min_temp, prec_sum, wind_speed]
    return day_reports

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
    return day_reports


if __name__ == "__main__":
    forecast=formate_weather_forecast()
    print(forecast)
    print('Finished')