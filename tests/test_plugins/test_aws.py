import unittest
from unittest.mock import Mock, patch
from tests.test_api import TestAPIStatus
from yams_api.plugins.dev.aws.methods import AWSPublicResource


class TestAWSAPI(TestAPIStatus):

    def test_aws_endpoint_reachable(self):
        resp = self.client.get("/plugins/aws/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, 'application/json')

    # Todo: Exception handling tests
    @unittest.skip('Exceptions not fully implemented. skipping')
    def test_aws_endpoint_server_error(self):

        with self.assertRaises(Exception):
            resp = self.client.get("/plugins/aws/")
        self.assertEqual(resp.status_code, 500)
        self.assertEqual(resp.mimetype, 'application/json')

        #self.assertEqual(resp.data, b'{\n  "status": "ok"\n}')

    @patch('yams_api.plugins.dev.aws.views.methods.AWSResource')
    def test_aws_ec2_awsresource_returns_successfully(self, m_methods):
        m_aws_obj = Mock()
        m_methods.return_value = m_aws_obj
        m_aws_obj.get_resource.return_value = "my_resource"

        resp = self.client.get("/plugins/aws/ec2/some_resource")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, 'application/json')

        self.assertEqual(resp.data, b'{\n  "response": "my_resource"\n}')


    @unittest.skip("method not implemented yet. skipping")
    def test_aws_ec2_resource_returns_successfully(self):
        pass

    @patch.object(AWSPublicResource, 'get_aws_endpoint_status')
    def test_aws_ec2_awspublicresource_returns_successfully(self, m_obj):
        m_obj.return_value = "running"

        resp = self.client.get("/plugins/aws/status")
        self.assertEqual(resp.mimetype, 'application/json')

        # todo: get proper response for public resource response
        self.assertEqual(resp.data, b'{\n  "response": "running"\n}')

if __name__ == '__main__':
    unittest.main(verbosity=2)
