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
    return day_reports


def weather_forecast(run: int, para_nr: int, result: dict, day1, day2, day3, day4, day5, day6, day7):
    """
    Generates the weather forecast for the next seven days based on the last seven days.

    Args:
        run (int): The run number for the forecast.
        paraNr (int): The parameter number for the weather data.
        result (dict): The dictionary to store the forecast results.
        day1, day2, day3, day4, day5, day6, day7: Weather data for the last seven days.

    Returns:
        None
    """
    number = 8

    # example data -> the last seven days
    X = np.array([1, 2, 3, 4, 5, 6, 7]).reshape(-1, 1)  # Unabhängige Variable
    y = np.array([day1[para_nr], day2[para_nr], day3[para_nr], day4[para_nr], day5[para_nr], day6[para_nr], day7[para_nr]])

    for run in range(1,8):
        # Create and train linear regression model
        model = LinearRegression()
        model.fit(X, y)

        # Make a prediction for the available data
        predictions = model.predict(X)

        # Get results
        pred1 = 0
        pred2 = 0
        for i, pred in enumerate(predictions):
            if (i == 5):
                pred1 = pred
            elif(i == 6):
                pred2 = pred

        diff = pred2 - pred1
        next_day = pred + diff

        # preventing negative values for precipitation_sum and wind_speed
        if (para_nr == 2) and (next_day < 0):
            next_day = 0.0
        elif (para_nr == 3) and (next_day < 0):
            next_day = 0.0
        
        number = number + 1
        X = np.append(X, number).reshape(-1, 1)
        y = np.append(y, next_day)

        # Add new value to the results
        result["fday" + str(run)].append(next_day)


async def get_weather_forecast(location= 'Stuttgart'):
    """
    Retrieves the weather forecast for the next seven days for a given location.

    Args:
        location (str): The location for which to retrieve the weather forecast. Default is 'Stuttgart'.

    Returns:
        list: A list of dictionaries containing the weather forecast for each of the next seven days.
            Each dictionary includes:
                - Date
                - Maximum temperature
                - Minimum temperature
                - Precipitation sum
                - Wind speed
                - Station
                - Predicted (True for forecast data)
    """
    db = Database('mongodb+srv://weatherclient:verteilteSysteme@weather.nncm5t4.mongodb.net/weather?retryWrites=true&w=majority&appName=Weather')
    day_reports = await get_weather_report(location)
    result = {"fday1": [], "fday2":[], "fday3":[], "fday4":[], "fday5":[], "fday6":[], "fday7":[]}
    # get the date
    date = datetime.now()

    # get the forecast for the next seven days
    for para_nr in range (0, 4):
        #print ('para_nr: ', para_nr)
        weather_forecast(1, para_nr, result, day_reports['day1'], day_reports['day2'], day_reports['day3'], day_reports['day4'], day_reports['day5'], day_reports['day6'], day_reports['day7'])
    
    # get the final result
    final_result= []
    
    for i in range(0, len(result)):
        # get todays date
        date = date + timedelta(days=1)
        # write data in the database
        await db.insert(date.strftime("%Y-%m-%d"), round(result["fday"+str(i+1)][0], 1), round(result["fday"+str(i+1)][1], 1), round(result["fday"+str(i+1)][2], 1), round(result["fday"+str(i+1)][3], 1), day_reports["day"+str(i+1)][5], True)
        forecast= {
            'time': date.strftime("%Y-%m-%d"),
            'temperature_max': round(result["fday"+str(i+1)][0], 1),
            'temperature_min': round(result["fday"+str(i+1)][1], 1),
            'precipitation_sum': round(result["fday"+str(i+1)][2], 1), 
            'wind_speed': round(result["fday"+str(i+1)][3], 1), 
            'station': day_reports["day"+str(i+1)][5], 
            'predicted': True
            }
        final_result.append(forecast)

    print(final_result)
    return final_result 


def test_data():
    """
        Function which return testdata
    """
    # day = [max_temp, min_temp, prec_sum, wind_speed]
    day1 = [18, 4, 0.2, 14]
    day2 = [13, 9, 0.1, 25]
    day3 = [12, 5, 0.0, 26]
    day4 = [16, 6, 0.3, 9]
    day5 = [17, 7, 0.4, 17]
    day6 = [19, 7, 0.1, 12]
    day7 = [10, 9, 0.0, 25]
    day8 = [13, 7, 0.1, 28] # day8 for analysing the results
    return day1, day2, day3, day4, day5, day6, day7, day8

if __name__ == "__main__":
    test = False
    if test == True:
        day1, day2, day3, day4, day5, day6, day7, day8 = test_data()
        result = {"fday1": [], "fday2":[], "fday3":[], "fday4":[], "fday5":[], "fday6":[], "fday7":[]}

        for para_nr in range (0, 4):
            weather_forecast(1, para_nr, result, day1, day2, day3, day4, day5, day6, day7)
        expected_result = {'fday1': [14.0, 8.571428571428573, 0.1285714285714286, 18.0], 'fday2': [13.649122807017545, 9.223057644110273, 0.11854636591478701, 17.899749373433583], 'fday3': [13.421052631578949, 9.646616541353382, 0.11203007518796998, 17.834586466165412], 'fday4': [13.192982456140351, 10.070175438596491, 0.10551378446115289, 17.769423558897238], 'fday5': [12.964912280701757, 10.493734335839598, 0.09899749373433588, 17.70426065162907], 'fday6': [12.736842105263161, 10.917293233082706, 0.09248120300751882, 17.6390977443609], 'fday7': [12.508771929824565, 11.34085213032581, 0.08596491228070181, 17.573934837092725]}
        if(result==expected_result):
            print('\033[32mForecast works.\033[0m')
        else:
            print('\033[31m \nError in weather forecast!\n\033[0m')
    else:
        asyncio.run(get_weather_forecast())
    print('Finished')