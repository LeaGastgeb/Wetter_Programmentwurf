# Autor : Lea Gastgeb
# Datum: 09.04.2024
# Version: 0.1
# Licence: Open Source

import unittest
from unittest.mock import MagicMock
from weather_app import validate_data, fetch_weather_data, clean_data
import asyncio


class TestWeatherFunctions(unittest.TestCase):
    
    def test_fetch_weather_data_api_success(self):
        # Mock für eine erfolgreiche API-Antwort
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json.return_value = {'daily': {'time': ['2024-04-09'], 'temperature_2m_max': [20], 'temperature_2m_min': [10], 'precipitation_sum': [5], 'wind_speed_10m_max': [15]}}

        with unittest.mock.patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            result = asyncio.run(fetch_weather_data('Stuttgart'))
            self.assertIsNotNone(result)

    def test_fetch_weather_data_api_failure(self):
        # Mock für eine fehlgeschlagene API-Antwort
        mock_response = MagicMock()
        mock_response.status = 404

        with unittest.mock.patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            result = asyncio.run(fetch_weather_data('Berlin'))
            self.assertIsNone(result)

    # Weitere Tests für fetch_weather_data mit Datenbankzugriff können hinzugefügt werden

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
            'temperature_max': 80,  # Ungültige Temperatur
            'temperature_min': 90,  # Ungültige Temperatur
            'precipitation_sum': -5,  # Negative Niederschlagsmenge
            'wind_speed_10m_max': 150  # Hohe Windgeschwindigkeit
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