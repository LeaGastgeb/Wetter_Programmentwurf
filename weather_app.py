# Autor : Lea Gastgeb
# Datum: 08.04.2024
# Version: 0.3
# Licence: Open Source
# Module Short Description: Integration of the weather API and the database


import aiohttp
import asyncio
from datetime import datetime, timedelta
from database import Database
from fastapi import FastAPI, Request, HTTPException
from functools import lru_cache
from typing import List, Dict, Any
import time
import geocoder

app = FastAPI()

async def fetch_weather_data(city, lat, lon):
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



def validate_data(data: Dict[str, Any]) -> bool:
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
        if not (-50 <= data['temperature_max'] <= 50 and -500 <= data['temperature_min'] <= data['temperature_max']):
            return False
        if 'precipitation_sum' in data and not (0 <= data['precipitation_sum'] <= 1000):  # Annahme: Maximal 1000 mm
            return False
        if 'wind_speed_10m_max' in data and not (0 <= data['wind_speed_10m_max'] <= 100):  # Annahme: Maximal 200 km/h
            return False
    except ValueError:
        return False
    
    return True



def clean_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Bereinigt die Wetterdaten, indem ungültige Datensätze entfernt werden.

    Args:
        data (List[Dict[str, Any]]): Die zu bereinigenden Wetterdaten.

    Returns:
        List[Dict[str, Any]]: Die bereinigten Wetterdaten.
    """
    cleaned_data = [record for record in data if validate_data(record)]
    return cleaned_data



async def get_ip(request: Request):
    client_ip = request.client.host
    return client_ip



async def get_location_from_ip(ip: str):
    g = geocoder.ip('me')
    location = g.city
    lat = g.latlng[0]
    lon = g.latlng[1]
    return location, lat, lon


async def simulate_client(client_id):
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/weather") as response:
            if response.status == 200:
                data = await response.json()
                print(f"Client {client_id}: Received weather data: {data}")
            else:
                print(f"Client {client_id}: Error retrieving weather data. Status code: {response.status}")



async def simulate_many_clients(num_clients: int):
    """
    Simulate multiple clients accessing the /weather endpoint simultaneously.

    Args:
        num_clients (int): Number of clients to simulate.
    """
    tasks = [fetch_weather_data("Stuttgart", "48.78", "9.18") for _ in range(num_clients)]
    await asyncio.gather(*tasks)



# Caching the weather data for a certain period to reduce API calls
@lru_cache(maxsize=None)
async def cached_fetch_weather_data(city: str, lat, lon) -> List[Dict[str, Any]]:
    """
    Wrapper function to cache the result of fetch_weather_data function.

    Args:
        city (str): The name of the city for which weather data is to be fetched.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing weather data for the specified city.
    """
    return await fetch_weather_data(city, lat, lon)



@app.get("/")
async def read_root() -> str:
    """
    Endpoint to get the root message of the API.

    Returns:
        str: Welcome message.
    """
    return "Welcome to our weather forecast system"



@app.get("/weather")
async def read_weather(request: Request) -> List[Dict[str, Any]]:
    """
    Endpoint to fetch weather data for a city.

    Args:
        request (Request): The request object.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing weather data for the specified city.
    """
    client_ip = request.client.host
    
    client_location = await get_location_from_ip(client_ip)
    print(f"Client IP: {client_ip}, Location: {client_location}")
    start_time = time.time()  

    num_clients = 1
    await simulate_many_clients(num_clients)

    end_time = time.time() 
    duration = end_time - start_time  

    print(f"Processing time for /weather request: {duration} seconds")

    return await fetch_weather_data(client_location[0], client_location[1], client_location[2])



@app.get("/weather_forecast")
async def read_weather_forecast() -> str:
    """
    Endpoint to get the weather forecast.

    Returns:
        str: Weather forecast message.
    """
    return "Weather forecast"



async def main():
    # client_ip = '127.0.0.1' #await get_ip(request=Request())
    # client_location = await get_location_from_ip(client_ip)
    fetch_weather_data('Stuttgart', '48.78', '9.18')



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
    asyncio.run(main())
    