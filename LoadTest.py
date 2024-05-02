from locust import HttpUser, task, between

class WeatherAPILoadTest(HttpUser):
    host = 'http://10.8.0.1'
    # Wartezeit zwischen Aufgaben, um Anfragerate zu variieren
    wait_time = between(1, 3)  # 1 bis 3 Sekunden
    
    @task  # Definiert eine Aufgabe, die von Clients ausgeführt wird
    def get_weather(self):
        # Abrufen des Wetter-Endpunkts
        self.client.get("/weather")