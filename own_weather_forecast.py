import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

def get_weather_report():
    # get the current weather data from the database
    print("Getting the weather report of the last seven days.")

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

def weather_forecast(run: int, para_nr: int, result: dict, day1, day2, day3, day4, day5, day6, day7):
    number = 8

    # Beispiel Daten
    X = np.array([1, 2, 3, 4, 5, 6, 7]).reshape(-1, 1)  # Unabhängige Variable
    y = np.array([day1[para_nr], day2[para_nr], day3[para_nr], day4[para_nr], day5[para_nr], day6[para_nr], day7[para_nr]])  # Abhängige Variable

    for run in range(1,8):
        print('Run: ', run)
        # Lineares Regressionsmodell erstellen und trainieren
        model = LinearRegression()
        model.fit(X, y)

        # Vorhersage für die vorhandenen Daten machen
        predictions = model.predict(X)
        print(predictions)

        # Ergebnisse ausgeben
        pred1 = 0
        pred2 = 0
        for i, pred in enumerate(predictions):
            print(f"Vorhersage für X={X[i][0]}: {pred}")
            if (i == 5):
                pred1 = pred
            elif(i == 6):
                pred2 = pred
        print(pred1, pred2)
        diff = pred2 - pred1
        print(f"Vorhersage für X={number}: {pred+diff}")
        next_day = pred + diff
        number = number + 1
        
        X = np.append(X, number).reshape(-1, 1)
        y = np.append(y, next_day)
        print(y)

        # Add new value to the results
        result["fday" + str(run)].append(next_day)


def get_weather_forecast():
    day1, day2, day3, day4, day5, day6, day7 = get_weather_report()
    result = {"fday1": [], "fday2":[], "fday3":[], "fday4":[], "fday5":[], "fday6":[], "fday7":[]}

    for para_nr in range (0, 4):
        weather_forecast(1, para_nr, result, day1, day2, day3, day4, day5, day6, day7)
    return result 


if __name__ == "__main__":
    day1, day2, day3, day4, day5, day6, day7, day8 = trainings_data()
    result = {"fday1": [], "fday2":[], "fday3":[], "fday4":[], "fday5":[], "fday6":[], "fday7":[]}

    for para_nr in range (0, 4):
        weather_forecast(1, para_nr, result, day1, day2, day3, day4, day5, day6, day7)

    print(result)