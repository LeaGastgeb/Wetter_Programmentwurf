# Autor : Lea Gastgeb
# Datum: 30.04.2024
# Version: 0.3
# Licence: Open Source
# Module Short Description: Interface to the database

import motor.motor_asyncio
from pymongo.errors import PyMongoError
import asyncio
from fastapi import HTTPException
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, url):
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(url)
            self.db = self.client.weather
            logger.info("Verbindung zur MongoDB erfolgreich hergestellt")
        except Exception as e:
            logger.error(f"Fehler bei der Verbindung zur MongoDB: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to MongoDB: {e}")
        

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
        try:
            await self.db.weather_data.insert_one(data)
            logger.info("Daten erfolgreich eingefügt")
        except PyMongoError as e:
            logger.error(f"Fehler beim Einfügen der Daten in die Datenbank: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Fehler beim Einfügen der Daten in die Datenbank: {str(e)}"
            )
        

    async def fetch(self):
        try:
            data = await self.db.weather_data.find().to_list(length=None)
            logger.info("Daten erfolgreich abgerufen")
            return data
        except PyMongoError as e:
            logger.error(f"Fehler beim Abrufen der Daten: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Fehler beim Abrufen der Daten: {str(e)}"
            )
        

    async def delete(self):
        try:
            await self.db.weather_data.delete_many({})
            logger.info(f"Wetterdaten erfolgreich gelöscht")
        except PyMongoError as e:
            logger.error(f"Fehler beim Löschen der Daten: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Fehler beim Löschen: {str(e)}"
            )

    async def delete_station(self, station):
        try:
            await self.db.weather_data.delete_many({"station": station})
            logger.info(f"Wetterdaten für {station} erfolgreich gelöscht")
        except PyMongoError as e:
            logger.error(f"Fehler beim Löschen der Daten für {station}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Fehler beim Löschen der Daten für {station}: {str(e)}"
            )

    async def fetch_station(self, station):
        try:
            data = await self.db.weather_data.find({"station": station}).to_list(length=None)
            logger.info(f"Wetterdaten für {station} erfolgreich abgerufen")
            return data
        except PyMongoError as e:
            logger.error(f"Fehler beim Abrufen der Daten für {station}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Fehler beim Abrufen der Wetterdaten aus der Datenbank: {str(e)}"
            )

    async def close_connection(self):
        try:
            await self.client.close()
            logger.info("Verbindung zur MongoDB erfolgreich geschlossen")
        except PyMongoError as e:
            logger.error(f"Fehler beim Schließen der MongoDB-Verbindung: {str(e)}")


async def test():
    mongo_url = "mongodb+srv://weatherclient:verteilteSysteme@weather.nncm5t4.mongodb.net/weather?retryWrites=true&w=majority&appName=Weather"
    db = Database(mongo_url)
    print("Weather data:")
    data = await db.fetch_station("Stuttgart")
    for entry in data:
        print(entry)
    
if __name__ == "__main__":
    asyncio.run(test())

