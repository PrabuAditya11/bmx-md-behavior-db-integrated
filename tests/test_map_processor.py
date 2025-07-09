import unittest
from src.services.map_processor import load_coordinates, process_csv_data

class TestMapProcessor(unittest.TestCase):

    def test_load_coordinates_valid(self):
        # Assuming we have a valid CSV file path for testing
        result = load_coordinates('tests/test_data/valid_coordinates.csv')
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_load_coordinates_invalid(self):
        result = load_coordinates('tests/test_data/invalid_coordinates.csv')
        self.assertEqual(result, [])

    def test_process_csv_data(self):
        csv_data = [
            {"lat": -6.2088, "lon": 106.8456, "store_name": "Store A"},
            {"lat": -6.2090, "lon": 106.8460, "store_name": "Store B"},
        ]
        processed_data = process_csv_data(csv_data)
        self.assertEqual(len(processed_data), 2)
        self.assertIn("Store A", [store["store_name"] for store in processed_data])

if __name__ == '__main__':
    unittest.main()