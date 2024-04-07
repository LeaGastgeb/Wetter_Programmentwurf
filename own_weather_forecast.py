import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from weather_app import fetch_weather_data
from datetime import datetime, timedelta
import asyncio

def get_weather_report():
    # get the current weather data from the database

    print("Getting the weather report of the last seven days.")
    # get the data from the database
    data = asyncio.run(fetch_weather_data('Stuttgart'))

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
    print(data)
    return day_reports


def weather_forecast(run: int, para_nr: int, result: dict, day1, day2, day3, day4, day5, day6, day7):
    # generate the weather data of the next seven days based on the last seven days
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

        # preventing negative values for precipitation_sum
        if (para_nr == 2) and (next_day < 0):
            next_day = 0.0

        number = number + 1
        
        X = np.append(X, number).reshape(-1, 1)
        y = np.append(y, next_day)

        # Add new value to the results
        result["fday" + str(run)].append(next_day)


def get_weather_forecast():
    day_reports = get_weather_report()
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

        forecast= {
            'time': date.strftime("%Y-%m-%d"),
            'temperature_max': result["fday"+str(i+1)][0],
            'temperature_min': result["fday"+str(i+1)][1],
            'precipitation_sum': result["fday"+str(i+1)][2], 
            'wind_speed': result["fday"+str(i+1)][3], 
            'station': day_reports["day"+str(i+1)][5], 
            'predicted': True
            }
        final_result.append(forecast)

    print(final_result)
    return result 


def trainings_data():
    # data for testing
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
        day1, day2, day3, day4, day5, day6, day7, day8 = trainings_data()
        result = {"fday1": [], "fday2":[], "fday3":[], "fday4":[], "fday5":[], "fday6":[], "fday7":[]}

        for para_nr in range (0, 4):
            weather_forecast(1, para_nr, result, day1, day2, day3, day4, day5, day6, day7)

        print(result)
    else:
        get_weather_forecast()