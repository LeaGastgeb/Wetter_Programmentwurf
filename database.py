# Autor : Lea Gastgeb
# Datum: 13.03.2024
# Version: 0.2
# Licence: Open Source
# Module Short Description: Interface to the database

from pymongo import MongoClient

class Database:
    def __init__(self, url):
        self.client = MongoClient(url)
        self.db = self.client.get_database()
        self.weather_data = self.db.weather_data

    def insert(self, time, temp_max, temp_min, precipitation_sum, wind_speed, station, pred=False):
        data = {
            "time": time,
            "temperature_max": temp_max,
            "temperature_min": temp_min,
            "precipitation_sum": precipitation_sum,
            "wind_speed": wind_speed,
            "station": station,
            "predicted": pred
        }
        self.weather_data.insert_one(data)

    def fetch(self):
        return list(self.weather_data.find().sort("time", -1))

    def delete(self):
        self.weather_data.delete_many({})

    def delete_station(self, station):
        self.weather_data.delete_many({"station": station})

    def fetch_station(self, station):
        return list(self.weather_data.find({"station": station}))

    def __del__(self):
        self.client.close()

# Beispiel zur Verwendung des Database-Objekts mit der neuen MongoDB-Verbindung
if __name__ == "__main__":
    mongo_url = "mongodb+srv://weatherclient:verteilteSysteme@weather.nncm5t4.mongodb.net/weather?retryWrites=true&w=majority&appName=Weather"
    db = Database(mongo_url)
    # Beispiel zum Einfügen von Daten
    db.insert("2024-03-17", 25.0, 15.0, 5.0, 10.0, "Stuttgart")
    # Beispiel zum Abrufen von Daten
    print("Weather data:")
    for data in db.fetch():
        print(data)
    