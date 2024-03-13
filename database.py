# Autor : Lea Gastgeb
# Datum: 13.03.2024
# Version: 0.2
# Licence: Open Source
# Module Short Description: Interface to the database

import requests
import json

class Database:
    def __init__(self, url):
        self.url = url
        self.create_table()

    def create_table(self):
        query = '''
                CREATE TABLE IF NOT EXISTS weather_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time DATETIME,
                    temperature_max REAL NOT NULL,
                    temperature_min REAL NOT NULL,
                    precipitation_sum REAL,
                    wind_speed REAL,
                    station TEXT
                )
                '''
        self.execute_query(query)

    def insert(self, time, temp_max, temp_min, humidity, wind_speed, station):
        query = '''
                INSERT INTO weather_data (time, temperature_max, temperature_min, precipitation_sum, wind_speed, station)
                VALUES (?, ?, ?, ?, ?, ?)
                '''
        params = (time, temp_max, temp_min, humidity, wind_speed, station)
        self.execute_query(query, params)

    def fetch(self):
        query = '''
                SELECT * FROM weather_data
                ORDER BY time DESC
                '''
        return self.execute_query(query)

    def delete(self):
        query = '''
                DELETE FROM weather_data
                '''
        self.execute_query(query)

    def execute_query(self, query, params=None):
        data = {'query': query}
        if params:
            data['params'] = params

        response = requests.post(f'{self.url}/db/execute', json=data)
        response.raise_for_status()
        return response.json()

    def __del__(self):
        pass