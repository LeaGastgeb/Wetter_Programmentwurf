# Autor : Lea Gastgeb 
# Datum: 09.04.2024
# Version: 0.3
# Licence: Open Source
# Module Short Description: Backend for the weather forecast system

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
    g = geocoder.ip("me")
    if not g or not g.latlng:
        return "Stuttgart", "48.78", "9.18"  # Standardwerte
    else:
        location = g.city if g.city else "Stuttgart"
        lat = g.latlng[0]
        lon = g.latlng[1]
        return location, lat, lon
    


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
    uvicorn.run(app, host="localhost", port=8016)
    asyncio.run(main())