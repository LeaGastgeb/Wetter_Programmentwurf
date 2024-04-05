# Autor : Lea Gastgeb
# Datum: 27.03.2024
# Version: 0.3
# Licence: Open Source
# Module Short Description: Integration of the weather API and the database


import aiohttp
import asyncio
from datetime import datetime, timedelta
from database import Database
from fastapi import FastAPI, Request
from geopy.geocoders import Nominatim 

app = FastAPI()

async def fetch_weather_data(city):
    db = Database('mongodb+srv://weatherclient:verteilteSysteme@weather.nncm5t4.mongodb.net/weather?retryWrites=true&w=majority&appName=Weather')
    db_data = db.fetch()

    station_data_available = all(entry['time'] == (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d') and entry['station'] == city for day in range(7) for entry in db_data)

    if station_data_available:
        for entry in db_data:
            entry.pop('_id', None)
        return db_data
    
    else:
       # print("Daten der letzten 7 Tage einschließlich heute sind nicht vollständig verfügbar für ", city)
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
                    
                    db_data = db.fetch_station(station)
                    for entry in db_data:
                        entry.pop('_id', None)
                    return db_data

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


async def simulate_client(client_id):
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/weather") as response:
            if response.status == 200:
                data = await response.json()
                print(f"Client {client_id}: Received weather data: {data}")
            else:
                print(f"Client {client_id}: Error retrieving weather data. Status code: {response.status}")

async def simulate_many_clients(num_clients):
    tasks = [simulate_client(client_id) for client_id in range(num_clients)]
    await asyncio.gather(*tasks)

@app.get("/")
async def read_root():
    return "Willkommen bei unserem Wettervorhersagesystem"

@app.get("/weather")
async def read_weather(request: Request):
    num_clients = 10
    await asyncio.gather(simulate_many_clients(num_clients), fetch_weather_data('Stuttgart'))
    # client_ip = request.client.host
    # client_location = await get_location_from_ip(client_ip)
     
    return await fetch_weather_data("Stuttgart")

async def main():
    # client_ip = '127.0.0.1' #await get_ip(request=Request())
    # client_location = await get_location_from_ip(client_ip)
    num_clients = 10
    await asyncio.gather(simulate_many_clients(num_clients), fetch_weather_data('Stuttgart'))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
    asyncio.run(main())
    