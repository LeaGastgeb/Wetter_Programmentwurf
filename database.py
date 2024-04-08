# Autor : Lea Gastgeb
# Datum: 13.03.2024
# Version: 0.2
# Licence: Open Source
# Module Short Description: Interface to the database

import motor.motor_asyncio
from pymongo.errors import PyMongoError
import asyncio

class Database:
    def __init__(self, url):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(url)
        self.db = self.client.weather
        # self.client = MongoClient(url)
        # self.db = self.client.get_database()
        # self.weather_data = self.db.weather_data

    async def insert(self, time, temp_max, temp_min, precipitation_sum, wind_speed, station, pred=False):
        data = {
            "time": time,
            "temperature_max": temp_max,
            "temperature_min": temp_min,
            "precipitation_sum": precipitation_sum,
            "wind_speed": wind_speed,
            "station": station,
            "predicted": pred
        }
        #self.weather_data.insert_one(data)
        try:
            await self.db.collection.insert_one(data)
        except PyMongoError as e:
            print(f"Error inserting data into MongoDB: {e}")

    async def fetch(self):
        #return list(self.weather_data.find().sort("time", -1))
        try:
            data = await self.db.collection.find().to_list(length=None)
            return data
        except PyMongoError as e:
            print(f"Error fetching data from MongoDB: {e}")
            return []

    async def delete(self):
        try:
            await self.db.collection.delete_many({})
        except PyMongoError as e:
            print(f"Error deleting data from MongoDB: {e}")
        #self.weather_data.delete_many({})

    async def delete_station(self, station):
        try:
            await self.db.collection.delete_many({"station": station})
        except PyMongoError as e:
            print(f"Error deleting data from MongoDB: {e}")
        # self.weather_data.delete_many({"station": station})

    async def fetch_station(self, station):
        #return list(self.weather_data.find({"station": station}))
        try:
            data = await self.db.collection.find({"station": station}).to_list(length=None)
            return data
        except PyMongoError as e:
            print(f"Error fetching data from MongoDB: {e}")
            return []

    async def close_connection(self):
        try:
            await self.client.close()
        except PyMongoError as e:
            print(f"Error closing MongoDB connection: {e}")


async def test():
    mongo_url = "mongodb+srv://weatherclient:verteilteSysteme@weather.nncm5t4.mongodb.net/weather?retryWrites=true&w=majority&appName=Weather"
    db = Database(mongo_url)
    # Beispiel zum Einfügen von Daten
    # await db.insert("2024-03-17", 25.0, 15.0, 5.0, 10.0, "Stuttgart")
    # Beispiel zum Abrufen von Daten
    print("Weather data:")
    data = await db.fetch_station("Stuttgart")
    for entry in data:
        print(entry)
    
    # await db.delete_station("Stuttgart")
# Beispiel zur Verwendung des Database-Objekts mit der neuen MongoDB-Verbindung
if __name__ == "__main__":
    asyncio.run(test())

