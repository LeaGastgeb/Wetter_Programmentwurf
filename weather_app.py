import requests
from datetime import datetime 
from database import Database
import pandas as pd
from fastapi import FastAPI

app = FastAPI()

def fetch_weather_data():
    current_date = datetime.now().strftime('%Y-%m-%d')

    db = Database('weather_data.db')

    db_data = db.fetch()

    if db_data and current_date in db_data[0][1]:
        
        columns = ['id','time', 'temperature_max', 'temperature_min', 'precipitation_sum', 'wind_speed']
        df = pd.DataFrame(db_data, columns=columns)
        df = df.drop(columns=['id'])
        

    else:
        
        url = 'https://api.open-meteo.com/v1/forecast'
        params = {
            'latitude': 48.7823,
            'longitude': 9.177,
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max',
            'timezone': 'Europe/Berlin',
            'past_days': 7,
            'forecast_days': 2
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()

            time = data['daily']['time']
            temperature_max = data['daily']['temperature_2m_max']
            temperature_min = data['daily']['temperature_2m_min']
            precipitation_sum = data['daily']['precipitation_sum']
            wind_speed = data['daily']['wind_speed_10m_max']
            
            db.delete()
            for i in range(0, 8):
                db.insert(time[i], temperature_max[i], temperature_min[i], precipitation_sum[i], wind_speed[i])
            
            df = pd.DataFrame({
                'Date': time,
                'Temperature_Max': temperature_max,
                'Temperature_Min': temperature_min,
                'Precipitation_Sum': precipitation_sum,
                'Wind_Speed': wind_speed
            })

            return df
    
        else:
            print("Fehler beim Abrufen der Wetterdaten. Status Code: ", response.status_code)
            return None

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/weather")
async def read_weather():
    return fetch_weather_data().to_dict()


def main():
    fetch_weather_data()

if __name__ == "__main__":
    main()
