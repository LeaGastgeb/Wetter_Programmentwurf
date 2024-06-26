# Autor : Johanna Luise Koenig
# Datum: 30.04.2024
# Version: 0.1
# Licence: Open Source
# Module Short Description: Evaluate the results of the weather forecast

import asyncio
import numpy as np
from database import Database
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from weather_app import fetch_weather_data
from sklearn.linear_model import LinearRegression
from weather_forecast import get_weather_forecast


def real_data():
    """
        Function which return real data - must be adjusted manually
    """
    # day = [max_temp, min_temp, prec_sum, wind_speed]
    day1 = [15, 8, 0.32, 19]
    day2 = [18, 10, 0.0, 13]
    day3 = [17, 9, 0.07, 16]
    day4 = [19, 9, 0.09, 11]
    day5 = [19, 10, 0.17, 13]
    day6 = [19, 10, 0.13, 14]
    day7 = [19, 9, 0.0, 19]
    return day1, day2, day3, day4, day5, day6, day7

def formate_weather_forecast():
    """
    Formats the weather forecast data obtained from get_weather_forecast().

    Returns:
        dict: A dictionary containing formatted weather forecast data for each of the next seven days.
            Each day's data includes:
                - Maximum temperature
                - Minimum temperature
                - Total precipitation
                - Wind speed
    """

    forecast = asyncio.run(get_weather_forecast())
    day_reports = {}

    # Format forecast data for each day
    for i in range(0, len(forecast)):
        max_temp = forecast[i]['temperature_max']
        min_temp = forecast[i]['temperature_min']
        prec_sum = forecast[i]['precipitation_sum']
        wind_speed = forecast[i]['wind_speed']

        day_reports["fday" + str(i + 1)] = [max_temp, min_temp, prec_sum, wind_speed]

    return day_reports


def generate_forecast_graphics(para_nr:int):
    """
    Generates a comparison plot between the forecasted and real weather data.

    Args:
        para_nr (int): Parameter number for weather data (0 for maximum temperature, 1 for minimum temperature,
                       2 for total precipitation, 3 for wind speed).

    Returns:
        None
    """
    # get values
    own_forecast=formate_weather_forecast()
    day1, day2, day3, day4, day5, day6, day7 = real_data()

    # generate value-list
    real_data_first_values = [day1[para_nr], day2[para_nr], day3[para_nr], day4[para_nr], day5[para_nr], day6[para_nr], day7[para_nr]]
    own_forecast_first_values = [own_forecast[key][para_nr] for key in own_forecast]

    # Generate Plot
    plt.plot(range(1, 8), own_forecast_first_values, color='orange', label='Eigenprognose')
    plt.plot(range(1, 8), real_data_first_values, color='green', label='Reale Daten')

    # Save plots
    if para_nr==0:
        para_name = 'max_temp'
    elif para_nr==1:
        para_name = 'min_temp'
    elif para_nr==2:
        para_name = 'prec_sum'
    elif para_nr==3:
        para_name = 'wind_speed'
    else:
        para_name = 'ERROR'
    
    # Add Labeling
    plt.xlabel('Tag')
    plt.ylabel(para_name)
    plt.title('Vergleich von Eigenprognose und realen Daten')

    # Show plot
    plt.legend()

    plt.savefig('Vergleich_'+ para_name +'.png')
    plt.clf() 



if __name__ == "__main__":
    # Generate weather forecast data
    forecast = formate_weather_forecast()
    
    # Generate forecast graphics for each parameter
    for para_nr in range(0, 4):
        generate_forecast_graphics(para_nr)
    
    # Print the forecast data
    print(forecast)
    
    # Print finished message
    print('Finished')