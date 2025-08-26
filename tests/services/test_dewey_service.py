import unittest
import os
import json
from services.dewey_service import DeweyService

class TestDeweyService(unittest.TestCase):

    def setUp(self):
        # Create a dummy data file for testing
        self.test_data_path = "tests/services/test_dewey_data.json"
        os.makedirs(os.path.dirname(self.test_data_path), exist_ok=True)
        with open(self.test_data_path, 'w') as f:
            json.dump({
                "500": {
                    "name": "Science",
                    "divisions": {
                        "510": {
                            "name": "Mathematics",
                            "sections": {
                                "510": {"name": "Mathematics"},
                                "511": {"name": "General principles of mathematics"}
                            }
                        }
                    }
                }
            }, f)
        self.service = DeweyService(data_path=self.test_data_path)

    def tearDown(self):
        os.remove(self.test_data_path)

    def test_find_subject_section(self):
        subject = self.service.find_subject("511")
        self.assertEqual(subject, {"name": "General principles of mathematics"})

    def test_find_subject_division(self):
        subject = self.service.find_subject("510")
        self.assertEqual(subject, {"name": "Mathematics"})

    def test_find_subject_class(self):
        subject = self.service.find_subject("500")
        self.assertEqual(subject, {"name": "Science"})

    def test_find_subject_not_found(self):
        subject = self.service.find_subject("999")
        self.assertIsNone(subject)

    def test_find_subject_invalid_code(self):
        subject = self.service.find_subject("abc")
        self.assertIsNone(subject)

    def test_find_subject_empty_code(self):
        subject = self.service.find_subject("")
        self.assertIsNone(subject)

if __name__ == '__main__':
    unittest.main()
