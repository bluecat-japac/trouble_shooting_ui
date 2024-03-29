# Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import unittest
import context
from unittest import mock  # pylint:disable=import-error
from trouble_shooting_ui import trouble_shooting_ui_page


class TestTroubleShootingUIPage(unittest.TestCase):
    @mock.patch('trouble_shooting_ui.trouble_shooting_ui_page.os')
    def test_module_path(self, mock_os):
        """
        :param mock_os:
        :return:
        """
        path = mock.Mock()
        mock_os.path.dirname.return_value = path
        actual = trouble_shooting_ui_page.module_path()
        expect = path
        self.assertEqual(expect, actual)
        mock_os.path.dirname.assert_called_once()

    @mock.patch('trouble_shooting_ui_page.request')
    @mock.patch('trouble_shooting_ui_page.common')
    @mock.patch('trouble_shooting_ui_page.render_template')
    def test_trouble_shooting_ui_trouble_shooting_ui_page_get(self, mock_render_template, mock_common, mock_request):
        mock_request.method = 'GET'
        expect = mock.Mock()
        mock_render_template.return_value = expect
        actual = trouble_shooting_ui_page.trouble_shooting_ui_trouble_shooting_ui_page()
        self.assertEqual(actual, expect)
        mock_common.get_bam_data.assert_not_called()

    @mock.patch('trouble_shooting_ui_page.request')
    @mock.patch('trouble_shooting_ui_page.common')
    @mock.patch('trouble_shooting_ui_page.render_template')
    def test_trouble_shooting_ui_trouble_shooting_ui_page_post(self, mock_render_template, mock_common, mock_request):
        mock_request.method = 'POST'
        data = mock.Mock()
        mock_request.form = data
        mock_common.get_bam_data.return_value = '', '', ''
        expect = mock.Mock()
        mock_render_template.return_value = expect
        actual = trouble_shooting_ui_page.trouble_shooting_ui_trouble_shooting_ui_page()
        self.assertEqual(actual, expect)
        mock_common.get_bam_data.assert_called_once_with(data)

    @mock.patch('trouble_shooting_ui_page.request')
    @mock.patch('trouble_shooting_ui_page.jsonify')
    @mock.patch('trouble_shooting_ui_page.common')
    @mock.patch('trouble_shooting_ui_page.util')
    def test_onload(self, mock_util, mock_common, mock_jsonify, mock_request):
        bam_ip = '192.168.88.54'
        mock_common.get_bam_ip.return_value = bam_ip
        configurations = [(123456, 'DemoConfig')]
        mock_util.get_configurations.return_value = configurations
        servers = [654321]
        expect = {'bam': bam_ip, 'configurations': configurations, 'servers': servers}
        mock_jsonify.return_value = expect
        actual = trouble_shooting_ui_page.onload()
        self.assertEqual(actual, expect)
        mock_common.get_bam_ip.assert_called_once()
        mock_util.get_configurations.assert_called_once()

    @mock.patch('trouble_shooting_ui_page.request')
    @mock.patch('trouble_shooting_ui_page.jsonify')
    @mock.patch('trouble_shooting_ui_page.common')
    def test_update_server_list(self, mock_common, mock_jsonify, mock_request):
        mock_request.method = 'POST'
        data = {'config': 1235}
        mock_request.get_json.return_value = data
        servers = [654321]
        expect = {'servers': servers}
        mock_jsonify.return_value = expect
        actual = trouble_shooting_ui_page.update_server_list()
        self.assertEqual(actual, expect)

    @mock.patch('trouble_shooting_ui_page.request')
    @mock.patch('trouble_shooting_ui_page.jsonify')
    @mock.patch('trouble_shooting_ui_page.common')
    def test_submit(self, mock_common, mock_jsonify, mock_request):
        mock_request.method = 'POST'
        data = {"client-id": "123", 'server': 'abc(123)', 'tool': 'dig', 'param': '1.2.3.4', "config-name": "japac"}
        mock_request.get_json.return_value = data
        expect = {'result': "Connecting..."}
        mock_common.prepare_ssh_command.return_value = expect
        mock_jsonify.return_value = expect
        actual = trouble_shooting_ui_page.submit()
        self.assertEqual(actual, expect)
        mock_common.prepare_ssh_command.assert_called_once()

    @mock.patch('trouble_shooting_ui_page.g')
    @mock.patch('trouble_shooting_ui_page.request')
    @mock.patch('trouble_shooting_ui_page.jsonify')
    @mock.patch('trouble_shooting_ui_page.common')
    def test_submit_exception(self, mock_common, mock_jsonify, mock_request, mock_g):
        mock_request.method = 'POST'
        data = {"client-iddddd": "123", 'server': 'abc(123)', 'tool': 'dig', 'param': '1.2.3.4', "config-name": "japac"}
        mock_request.get_json.return_value = data
        expect = {}, 500
        mock_common.prepare_ssh_command.return_value = expect
        mock_jsonify.return_value = {}
        actual = trouble_shooting_ui_page.submit()
        self.assertEqual(actual, expect)
        mock_g.user.logger.error.assert_called_once()

    @mock.patch('trouble_shooting_ui_page.request')
    @mock.patch('trouble_shooting_ui_page.jsonify')
    @mock.patch('trouble_shooting_ui_page.common')
    def test_stream_result_get(self, mock_common, mock_jsonify, mock_request):
        mock_request.method = 'GET'
        config_name = "test"
        mock_request.args.get.return_value = config_name
        mock_common.management_result = {
            "test": {
                "test": {
                    "test": {
                        "test": "test",
                        "status": False
                    }
                }
            }
        }

        result = {"test": "test", "status": False}
        mock_jsonify.return_value = result
        actual = trouble_shooting_ui_page.stream_result()
        self.assertEqual(actual, result)

    @mock.patch('trouble_shooting_ui_page.request')
    @mock.patch('trouble_shooting_ui_page.jsonify')
    @mock.patch('trouble_shooting_ui_page.common')
    def test_stream_result_delete(self, mock_common, mock_jsonify, mock_request):
        mock_request.method = 'DELETE'
        mock_request.args.get.return_value = "test"
        mock_common.management_result = {
            "test": {
                "test": {
                    "test": {
                        "test": "test",
                        "status": False
                    }
                }
            }
        }

        result = {"status": "Sucesss"}
        mock_jsonify.return_value = result
        actual = trouble_shooting_ui_page.stream_result()
        self.assertEqual(actual, result)

    @mock.patch('trouble_shooting_ui_page.g')
    @mock.patch('trouble_shooting_ui_page.request')
    @mock.patch('trouble_shooting_ui_page.jsonify')
    @mock.patch('trouble_shooting_ui_page.common')
    def test_stream_result_exception(self, mock_common, mock_jsonify, mock_request, mock_g):
        mock_request.method = 'GET'
        config_name = None
        mock_request.args.get.return_value = config_name
        mock_common.management_result = {
            "test": {
                "test": {
                    "test": {
                        "test": "test",
                        "status": False
                    }
                }
            }
        }

        result = {"test": "test", "status": False}
        mock_jsonify.return_value = result
        actual = trouble_shooting_ui_page.stream_result()
        self.assertEqual(actual, result)
