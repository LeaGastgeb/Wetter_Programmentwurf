# Autor : Lea Gastgeb
# Datum: 01.03.2024
# Version: 0.1
# Licence: Open Source
# Module Short Description: Interface to the database


import sqlite3

class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.cur.execute('''
                         CREATE TABLE IF NOT EXISTS weather_data (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            time DATETIME,
                            temperature_max REAL NOT NULL,
                            temperature_min REAL NOT NULL,
                            precipitation_sum REAL,
                            wind_speed REAL
                            )'''
                        )
        self.conn.commit()

    def insert(self, time, temp_max, temp_min, humidity, wind_speed):
        self.cur.execute('''
                         INSERT INTO weather_data (time, temperature_max, temperature_min, precipitation_sum, wind_speed)
                         VALUES (?, ?, ?, ?, ?)''',
                         (time, temp_max, temp_min, humidity, wind_speed)
                        )
        self.conn.commit()

    def fetch(self):
        self.cur.execute('''
                         SELECT * FROM weather_data
                         ORDER BY time DESC'''
                        )
        rows = self.cur.fetchall()
        return rows
    
    def delete(self):
        self.cur.execute('''
                         DELETE FROM weather_data'''
                        )
        self.conn.commit()

    def __del__(self):
        self.conn.close()