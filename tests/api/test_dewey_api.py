import unittest
import json
from unittest.mock import patch, MagicMock
from api.dewey_decimal import app

class TestDeweyAPI(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        app.config['TESTING'] = True

    @patch('api.dewey_decimal.get_dewey_service')
    def test_get_dewey_subject_success_section(self, mock_get_service):
        mock_service = MagicMock()
        mock_service.find_subject.return_value = {"name": "General principles of mathematics"}
        mock_get_service.return_value = mock_service

        response = self.app.get('/api/dewey?code=511')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data, {"name": "General principles of mathematics"})

    @patch('api.dewey_decimal.get_dewey_service')
    def test_get_dewey_subject_success_division(self, mock_get_service):
        mock_service = MagicMock()
        mock_service.find_subject.return_value = {"name": "Mathematics"}
        mock_get_service.return_value = mock_service

        response = self.app.get('/api/dewey?code=510')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data, {"name": "Mathematics"})

    @patch('api.dewey_decimal.get_dewey_service')
    def test_get_dewey_subject_success_class(self, mock_get_service):
        mock_service = MagicMock()
        mock_service.find_subject.return_value = {"name": "Science"}
        mock_get_service.return_value = mock_service

        response = self.app.get('/api/dewey?code=500')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data, {"name": "Science"})

    @patch('api.dewey_decimal.get_dewey_service')
    def test_get_dewey_subject_not_found(self, mock_get_service):
        mock_service = MagicMock()
        mock_service.find_subject.return_value = None
        mock_get_service.return_value = mock_service

        response = self.app.get('/api/dewey?code=999')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data, {"error": "Dewey code not found"})

    def test_get_dewey_subject_no_code(self):
        response = self.app.get('/api/dewey')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data, {"error": "Dewey code must be provided"})

if __name__ == '__main__':
    unittest.main()
