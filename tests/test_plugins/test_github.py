import unittest
from tests.test_api import TestAPIStatus


class TestGitHubAPI(TestAPIStatus):

    def test_github_endpoint(self):
        resp = self.client.get("/plugins/github")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, 'application/json')

        # todo: tame resp.data returning b'{\n  "status": "ok"\n}'
        #self.assertEqual(resp.text, self.expected_status)

    def test_github_status_endpoint(self):
        resp = self.client.get("/plugins/github/status")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, 'application/json')

        # todo: tame resp.data returning b'{\n  "status": "ok"\n}'
        #self.assertEqual(resp.text, self.expected_status)


if __name__ == '__main__':
    unittest.main(verbosity=2)
