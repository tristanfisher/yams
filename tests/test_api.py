import json
import unittest
from flask import jsonify, url_for

from yams_api import api
from yams import app
from config import APP, API


class TestAPIStatus(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        api.config['SERVER_NAME'] = "%s:%s" % (API.LISTEN_HOST, API.LISTEN_PORT)
        cls.client = api.test_client()

    def setUp(self, status_text="ok"):
        self.app_context = api.test_request_context()
        self.app_context.push()
        #self.expected_status = json.loads('{"status":"' + status_text + '"}')

    def tearDown(self):
        self.app_context.pop()

    def test_status_endpoint(self):
        resp = self.client.get("/status")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, 'application/json')

        # todo: tame resp.data returning b'{\n  "status": "ok"\n}'
        #self.assertEqual(resp.text, self.expected_status)


# def suite_api_tests():
#     suite = unittest.TestSuite()
#     suite.addTest(TestAPIStatus('test_status_endpoint'))
#     return suite


if __name__ == '__main__':
    # -v on command line or 0-2
    # - 0 = totals only
    # - 1 = . for pass
    # - 2 = help string and result
    # - E for error
    # - F for failure
    unittest.main(verbosity=2)