# Autor : Lea Gastgeb
# Datum: 30.04.2024
# Version: 0.5
# Licence: Open Source
# Module Short Description: Integration of the weather API and the database


import aiohttp
from datetime import datetime, timedelta
from fastapi import HTTPException
import logging

from database import Database

logging.basicConfig(
    level=logging.WARNING,  
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def fetch_weather_data(city, lat=48.78, lon=9.18):
    """
    Fetch weather data for a given city from the weather API or the database.

    
    Args:
        city (str): The name of the city for which weather data is to be fetched.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing weather data for the specified city.
    """
    try:
        db = Database('mongodb+srv://weatherclient:verteilteSysteme@weather.nncm5t4.mongodb.net/?retryWrites=true&w=majority&appName=Weather')
        db_data = await db.fetch_station(city)  

        station_data_available = True  
        for day in range(7):
            day_conditions_met = False  
            for entry in db_data:
                date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
                condition_1 = entry['time'] == date
                condition_2 = not entry["predicted"]
                if condition_1 and condition_2:
                    day_conditions_met = True  
                    break
            if not day_conditions_met:
                station_data_available = False  
                break
        
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
                        logger.info(f"Erfolgreiche Antwort von der Wetter-API: {data}")

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
                        logger.warning(f"Fehler beim Abrufen der Wetterdaten. Status: {response.status}")
                        return None
                    
    except aiohttp.ClientError as e:
        logger.error(f"HTTP Client Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Fehler bei der HTTP-Anfrage: {str(e)}"
        )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ein unerwarteter Fehler ist aufgetreten: {str(e)}"
        )


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
        
        datetime.strptime(data['time'], '%Y-%m-%d')
        
        if not (-50 <= data['temperature_max'] <= 50 and -50 <= data['temperature_min'] <= data['temperature_max']):
            return False
        if 'precipitation_sum' in data and not (0 <= data['precipitation_sum'] <= 1000):  # Annahme: Maximal 1000 mm
            return False
        if 'wind_speed_10m_max' in data and not (0 <= data['wind_speed_10m_max'] <= 100):  # Annahme: Maximal 200 km/h
            return False
    except ValueError as e:
        logger.error(f"Fehler bei der Datenvalidierung: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Fehler bei der Datenvalidierung: {str(e)}"
        )
    
    return True



def clean_data(data):
    """
    Bereinigt die Wetterdaten, indem ungültige Datensätze entfernt werden.

    Args:
        data (List[Dict[str, Any]]): Die zu bereinigenden Wetterdaten.

    Returns:
        List[Dict[str, Any]]: Die bereinigten Wetterdaten.
    """

    return [record for record in data if validate_data(record)]