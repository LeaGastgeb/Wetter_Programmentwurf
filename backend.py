# Autor : Lea Gastgeb 
# Datum: 09.04.2024
# Version: 0.3
# Licence: Open Source
# Module Short Description: 

import aiohttp
import asyncio
from fastapi import FastAPI
from functools import lru_cache
import time
import geocoder

from weather_app import fetch_weather_data
from own_weather_forecast import get_weather_forecast


app = FastAPI()


async def get_location_from_ip():
    """
    Retrieves location information based on the IP address of the client.
    
    Returns:
        tuple: A tuple containing location information in the format (location, latitude, longitude).
    """
    g = geocoder.ip('me')
    location = g.city
    lat = g.latlng[0]
    lon = g.latlng[1]
    return location, lat, lon


async def simulate_client(client_id):
    """
    Simulates a client requesting weather data from a server.
    
    Args:
        client_id (int): The ID of the client.
    """
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
async def cached_fetch_weather_data(city: str, lat, lon):
    """
    Wrapper function to cache the result of fetch_weather_data function.

    Args:
        city (str): The name of the city for which weather data is to be fetched.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing weather data for the specified city.
    """
    return await fetch_weather_data(city, lat, lon)



@app.get("/")
async def read_root():
    """
    Endpoint to get the root message of the API.

    Returns:
        str: Welcome message.
    """
    return "Welcome to our weather forecast system"



@app.get("/weather")
async def read_weather():
    """
    Endpoint to fetch weather data for a city.

    Args:
        request (Request): The request object.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing weather data for the specified city.
    """
    client_location = await get_location_from_ip()
    print(f"Location: {client_location}")
    start_time = time.time()  

    num_clients = 1
    await simulate_many_clients(num_clients)

    end_time = time.time() 
    duration = end_time - start_time  

    print(f"Processing time for /weather request: {duration} seconds")

    return await fetch_weather_data(client_location[0], client_location[1], client_location[2])



@app.get("/weather/forecast")
async def read_weather_forecast():
    """
    Endpoint to get the weather forecast.

    Returns:
        str: Weather forecast message.
    """
    return await get_weather_forecast()



async def main():
    fetch_weather_data('Stuttgart', '48.78', '9.18')



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    asyncio.run(main())