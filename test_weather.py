# Autor : Lea Gastgeb
# Datum: 09.04.2024
# Version: 0.1
# Licence: Open Source

import unittest
from unittest.mock import MagicMock
from weather_app import validate_data, fetch_weather_data, clean_data
import asyncio
from database import Database


class TestWeatherFunctions(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.db = Database("mongodb+srv://weatherclient:verteilteSysteme@weather.nncm5t4.mongodb.net/?retryWrites=true&w=majority&appName=Weather")

    def tearDown(self):
        self.loop.close()

    def test_insert_data(self):
            self.loop.run_until_complete(self.db.insert("2024-06-30", 25, 15, 10, 5, "TestStation"))
            data = self.loop.run_until_complete(self.db.fetch_station("TestStation"))
            self.assertEqual(len(data), 1)
    
    def test_fetch_data(self):
        data = self.loop.run_until_complete(self.db.fetch_station("TestStation"))
        self.assertEqual(len(data), 0)
    
    def test_delete_data(self):
        self.loop.run_until_complete(self.db.delete_station("TestStation"))
        data = self.loop.run_until_complete(self.db.fetch_station("TestStation"))
        self.assertEqual(len(data), 0)

    def test_fetch_weather_data_api_success(self):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json.return_value = {'daily': {'time': ['2024-04-09'], 'temperature_2m_max': [20], 'temperature_2m_min': [10], 'precipitation_sum': [5], 'wind_speed_10m_max': [15]}}

        with unittest.mock.patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            result = self.loop.run_until_complete(fetch_weather_data('Stuttgart'))
            self.assertIsNotNone(result)

    def test_fetch_weather_data_api_failure(self):
        mock_response = MagicMock()
        mock_response.status = 404

        with unittest.mock.patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            result = self.loop.run_until_complete(fetch_weather_data('Berlin'))
            self.assertIsNone(result)

    def test_validate_data_valid(self):
        valid_data = {
            'time': '2024-04-09',
            'temperature_max': 25,
            'temperature_min': 15,
            'precipitation_sum': 5,
            'wind_speed_10m_max': 20
        }
        self.assertTrue(validate_data(valid_data))

    def test_validate_data_invalid(self):
        invalid_data = {
            'time': '2024-04-09',
            'temperature_max': 80,  
            'temperature_min': 90,  
            'precipitation_sum': -5,  
            'wind_speed_10m_max': 150  
        }
        self.assertFalse(validate_data(invalid_data))

    def test_clean_data(self):
        data = [
            {'time': '2024-04-09', 'temperature_max': 25, 'temperature_min': 15},
            {'time': '2024-04-10', 'temperature_max': 30, 'temperature_min': 20},
            {'time': '2024-04-11', 'temperature_max': 35, 'temperature_min': 25},
            {'time': '2024-04-12', 'temperature_max': 40, 'temperature_min': 30},
            {'time': '2024-04-13', 'temperature_max': 45, 'temperature_min': 35},
            {'time': '2024-04-14', 'temperature_max': 50, 'temperature_min': 40},
            {'time': '2024-04-15', 'temperature_max': 55, 'temperature_min': 45}
        ]
        cleaned_data = clean_data(data)
        self.assertEqual(len(cleaned_data), 6)


if __name__ == '__main__':
    unittest.main()