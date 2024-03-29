# Autor : Lea Gastgeb
# Datum: 27.03.2024
# Version: 0.3
# Licence: Open Source
# Module Short Description: Integration of the weather API and the database


import aiohttp
from datetime import datetime, timedelta
from database import Database
from fastapi import FastAPI, Request
from geopy.geocoders import Nominatim 

app = FastAPI()

async def fetch_weather_data(city):
    db = Database('mongodb+srv://weatherclient:verteilteSysteme@weather.nncm5t4.mongodb.net/weather?retryWrites=true&w=majority&appName=Weather')
    db_data = db.fetch()

    # Check if data for the last 7 days is available for specific station
    station_data_available = False
    for day in range(7):
        date_to_check = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
        found = False
        for entry in db_data:
            if entry['time'] == date_to_check and entry['station'] == city:
                found = True
                break
        if not found:
            station_data_available = False
            break
        else:
            station_data_available = True
    
    if station_data_available:
        print(db_data)
        return db_data
    else:
        print("Daten der letzten 7 Tage einschließlich heute sind nicht vollständig verfügbar für ", city)
        url = 'https://api.open-meteo.com/v1/forecast'
        params = {
            'latitude': 48.7823,
            'longitude': 9.177,
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
                    station = city  # Define the station here

                    db.delete_station(station)
                    for i in range(0, 8):
                        db.insert(time[i], temperature_max[i], temperature_min[i], precipitation_sum[i], wind_speed[i], station)

                    return db.fetch_station(station)

                else:
                    print("Fehler beim Abrufen der Wetterdaten. Status Code: ", response.status)
                    return None

async def get_ip(request: Request):
    client_ip = request.client.host
    return client_ip


async def get_location_from_ip(ip: str):
    geolocator = Nominatim(user_agent="weather_app")
    location = await geolocator.geocode(ip)
    location_city = await geolocator.reverse((location.latitude, location.longitude))
    return location_city.raw.get('address', {}).get('city', '')

@app.get("/")
async def read_root():
    return "Willkommen bei unserem Wettervorhersagesystem"

@app.get("/weather")
async def read_weather(request: Request):
    client_ip = request.client.host
    client_location = await get_location_from_ip(client_ip)
    return await fetch_weather_data(client_location)

async def main():
    client_ip = '127.0.0.1' #await get_ip(request=Request())
    client_location = await get_location_from_ip(client_ip)
    await fetch_weather_data(client_location)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())