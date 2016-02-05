import unittest
from tests.test_api import TestAPIStatus


class TestTwitterAPI(TestAPIStatus):

    def test_twitter_endpoint(self):
        resp = self.client.get("/plugins/twitter")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, 'application/json')

        # todo: tame resp.data returning b'{\n  "status": "ok"\n}'
        #self.assertEqual(resp.text, self.expected_status)

if __name__ == '__main__':
    unittest.main(verbosity=2)
