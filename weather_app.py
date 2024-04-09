# Autor : Lea Gastgeb
# Datum: 08.04.2024
# Version: 0.3
# Licence: Open Source
# Module Short Description: Integration of the weather API and the database


import aiohttp
from datetime import datetime, timedelta
from fastapi import FastAPI,  HTTPException

from database import Database


app = FastAPI()

async def fetch_weather_data(city, lat=48.78, lon=9.18):
    """
    Fetch weather data for a given city from the weather API or the database.

    Args:
        city (str): The name of the city for which weather data is to be fetched.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing weather data for the specified city.
    """
    try:
        db = Database('mongodb+srv://weatherclient:verteilteSysteme@weather.nncm5t4.mongodb.net/weather?retryWrites=true&w=majority&appName=Weather')
        db_data = await db.fetch_station(city)  # Await the execution of the coroutine function

        station_data_available = True  # Initialize with True
        for day in range(7):
            day_conditions_met = False  # Initialize with False for the current day
            for entry in db_data:
                date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
                condition_1 = entry['time'] == date
                condition_2 = not entry["predicted"]
                # print(f"Day: {day}, Time: {entry['time']}, time_count: {date},Predicted: {entry['predicted']}, Condition 1: {condition_1}, Condition 2: {condition_2}")
                if condition_1 and condition_2:
                    day_conditions_met = True  # Conditions met for this day
                    break
            if not day_conditions_met:
                station_data_available = False  # Conditions not met for this day
                break
        # station_data_available = all(
        #     entry['time'] == (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d') and
        #     not entry["predicted"]
        #     for day in range(7) for entry in db_data
        # )
        if station_data_available:
            print("Station data available in the database")            
            for entry in db_data:
                entry.pop('_id', None)
            return db_data

        else:
            print("Station data not available in the database. Fetching from the weather API")
            url = 'https://api.open-meteo.com/v1/forecast'
            params = {
                'latitude': lat,
                'longitude': lon,
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max',
                'timezone': 'Europe/Berlin',
                'past_days': 7,
                'forecast_days': 2
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        time = data['daily']['time']
                        temperature_max = data['daily']['temperature_2m_max']
                        temperature_min = data['daily']['temperature_2m_min']
                        precipitation_sum = data['daily']['precipitation_sum']
                        wind_speed = data['daily']['wind_speed_10m_max']
                        station = city

                        await db.delete_station(station)
                        for i in range(0, 8):
                            await db.insert(time[i], temperature_max[i], temperature_min[i], precipitation_sum[i], wind_speed[i], station)
                        
                        db_data = await db.fetch_station(station)
                        
                        for entry in db_data:
                            entry.pop('_id', None)
                        return db_data

                    else:
                        print("Error retrieving weather data. Status Code: ", response.status)
                        return None
                    
    except aiohttp.ClientError as e:
        error_message = f"Error making HTTP request: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)



def validate_data(data) :
    """
    Validiert die Wetterdaten.

    Args:
        data (Dict[str, Any]): Das zu validierende Wetterdaten-Datensatz.

    Returns:
        bool: True, wenn die Daten gültig sind, sonst False.
    """
    if 'time' not in data or 'temperature_max' not in data or 'temperature_min' not in data:
        return False
    
    try:
        # Datum validieren
        datetime.strptime(data['time'], '%Y-%m-%d')
        # Temperaturwerte validieren
        if not (-50 <= data['temperature_max'] <= 50 and -50 <= data['temperature_min'] <= data['temperature_max']):
            return False
        if 'precipitation_sum' in data and not (0 <= data['precipitation_sum'] <= 1000):  # Annahme: Maximal 1000 mm
            return False
        if 'wind_speed_10m_max' in data and not (0 <= data['wind_speed_10m_max'] <= 100):  # Annahme: Maximal 200 km/h
            return False
    except ValueError:
        return False
    
    return True



def clean_data(data):
    """
    Bereinigt die Wetterdaten, indem ungültige Datensätze entfernt werden.

    Args:
        data (List[Dict[str, Any]]): Die zu bereinigenden Wetterdaten.

    Returns:
        List[Dict[str, Any]]: Die bereinigten Wetterdaten.
    """
    cleaned_data = [record for record in data if validate_data(record)]
    return cleaned_data