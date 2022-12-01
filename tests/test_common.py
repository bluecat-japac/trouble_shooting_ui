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
from common import common


class TestCommon(unittest.TestCase):

    @mock.patch('common.common.PortalException', Exception)
    @mock.patch('common.common.hasattr')
    @mock.patch('common.common.os')
    def test_get_bam_ip_exception(self, mock_os, mock_hasattr):
        mock_os.environ = {'no_bam_ip': ''}
        mock_hasattr.return_value = False
        with self.assertRaises(Exception):
            common.get_bam_ip()

    @mock.patch('common.common.g')
    def test_ssh_open_connection_without_exception(self, mock_g):
        """
        :return:
        """
        ssh = mock.Mock()
        hostname = 'host'
        username = 'user'
        password = 'pass'
        timeout = 15
        actual = common.ssh_open_connection(ssh, hostname, username, password, timeout)
        expect = True
        self.assertEqual(expect, actual)

    @mock.patch('common.common.AuthenticationException', Exception)
    @mock.patch('common.common.g')
    def test_ssh_open_connection_with_authentication_error(self, mock_g):
        """
        :return:
        """
        ssh = mock.Mock()
        hostname = 'host'
        username = 'user'
        password = 'pass'
        timeout = 15
        ssh.connect.side_effect = Exception()
        actual = common.ssh_open_connection(ssh, hostname, username, password, timeout)
        expect = False
        self.assertEqual(expect, actual)

    @mock.patch('common.common.g')
    def test_ssh_open_connection_with_attriblute_error(self, mock_g):
        """
        :return:
        """
        ssh = mock.Mock()
        hostname = 'host'
        username = 'user'
        password = 'pass'
        timeout = 15
        ssh.connect.side_effect = AttributeError()
        actual = common.ssh_open_connection(ssh, hostname, username, password, timeout)
        expect = False
        self.assertEqual(expect, actual)

    @mock.patch('common.common.g')
    def test_ssh_open_connection_with_exception(self, mock_g):
        """
        :return:
        """
        ssh = mock.Mock()
        hostname = 'host'
        username = 'user'
        password = 'pass'
        timeout = 15
        ssh.connect.side_effect = Exception()
        actual = common.ssh_open_connection(ssh, hostname, username, password, timeout)
        expect = False
        self.assertEqual(expect, actual)

    @mock.patch('common.common.management_result')
    @mock.patch('common.common.iter')
    @mock.patch('common.common.update_status_global_stream_result')
    @mock.patch('common.common.update_result_global_stream_result')
    def test_exec_command(self, mock_update_result_global_stream_result,
                          mock_update_status_global_stream_result, mock_iter, mock_management_result):
        """
        :param mock_set_rule:
        :return:
        """
        ssh = mock.MagicMock()
        cmd = "ping 192.168.88.88"
        config_name = "japac"
        server = "bdds01(192.168.88.88)"
        client_id = "123"
        tool = "ping"
        _, stdout, stderr = mock.MagicMock(), mock.MagicMock(), mock.MagicMock()
        ssh.exec_command.return_value = _, stdout, stderr
        mock_iter.return_value = ["a", "b"]
        global management_result
        management_result = mock.MagicMock()
        common.exec_command(ssh, cmd, config_name, server, client_id, tool)

    @mock.patch('common.common.g')
    def test_get_bam_name_happy_case(self, mock_g):
        mock_g.user = mock.MagicMock()
        mock_g.user.get_api_netloc.return_value = "192.168.88.200"
        from bluecat_portal import config
        config.api_url = [("BAM 200", 'http://192.168.88.200/Services/API?wsdl')]
        bam_name = common.get_bam_name()
        self.assertEqual(bam_name, "BAM 200")

    @mock.patch('common.common.g')
    def test_get_bam_name_happy_case_2(self, mock_g):
        mock_g.user = mock.MagicMock()
        mock_g.user.get_api_netloc.return_value = "192.168.88.200"
        from bluecat_portal import config
        config.api_url = 'http://192.168.88.200/Services/API?wsdl'
        bam_name = common.get_bam_name()
        self.assertEqual(bam_name, "192.168.88.200")

    @mock.patch('common.common.PortalException', Exception)
    @mock.patch('common.common.g')
    def test_get_bam_name_case_exception(self, mock_g):
        mock_g.user = mock.MagicMock()
        mock_g.user.get_api_netloc.return_value = "192.168.88.100"
        from bluecat_portal import config
        config.api_url = [("BAM 200", 'http://192.168.88.200/Services/API?wsdl')]

        with self.assertRaises(Exception):
            bam_name = common.get_bam_name()


    @mock.patch('common.common.iter')
    @mock.patch('common.common.g')
    @mock.patch('common.common.socket.timeout', Exception)
    def test_exec_command_exception(self, mock_g, mock_iter):
        """
        :param mock_set_rule:
        :return:
        """
        mock_management_result = {
            "japac": {
                "bdds01(192.168.88.88)": {
                    "123": {
                        "status": False
                    }
                }
            }
        }
        ssh = mock.MagicMock()
        cmd = "ping 192.168.88.88"
        config_name = "japac"
        server = "bdds01(192.168.88.88)"
        client_id = "123"
        tool = "ping"
        _, stdout, stderr = mock.MagicMock(), mock.MagicMock(), mock.MagicMock()
        ssh.exec_command.side_effect = Exception("ex")
        mock_iter.side_effect = Exception("ex")
        common.exec_command(ssh, cmd, config_name, server, client_id, tool)

    @mock.patch('common.common.management_result')
    def test_update_status_global_stream_result(self, mock_management_result):
        """
        :param mock_set_rule:
        :return:
        """
        mock_management_result = {
            "japac": {
                "bdds01(192.168.88.88)": {
                    "123": {
                        "status": False
                    }
                }
            }
        }
        config_name = "japac"
        server = "bdds01(192.168.88.88)"
        client_id = "123"
        common.update_status_global_stream_result(config_name, server, client_id, status=False)

    @mock.patch('common.common.management_result')
    def test_update_result_global_stream_result_global_none(self, mock_management_result):
        """
        :param mock_set_rule:
        :return:
        """
        mock_management_result = {}
        config_name = "japac"
        server = "bdds01(192.168.88.88)"
        client_id = "123"
        tool = "ping"
        stream_result = "tesssssss"
        status = True
        common.update_result_global_stream_result(config_name, server, client_id, tool, stream_result, status)

    @mock.patch('common.common.os')
    @mock.patch('common.common.RSAKey')
    @mock.patch('common.common.exec_command')
    @mock.patch('common.common.SSHClient')
    @mock.patch('common.common.ssh_open_connection')
    def test_prepare_ssh_command_fail(self, mock_ssh_open_connection, mock_sshclient, mock_exec, mock_rsa, mock_os):
        current_path = '/'
        mock_os.path.dirname.return_value = current_path
        key_path = '/id_rsa'
        mock_os.path.join.return_value = key_path
        key = mock.Mock()
        mock_rsa.from_private_key_file.return_value = key
        ssh = mock.Mock()
        mock_sshclient.return_value = ssh
        mock_ssh_open_connection.return_value = False
        config_name = "japac"
        server = "bdds01"
        hostname = "192.168.88.88"
        client_id = "123"
        tool = "ping"
        param = "192.168.88.54"
        with self.assertRaises(Exception):
            common.prepare_ssh_command(config_name, server, hostname, client_id, tool, param)
            mock_exec.assert_not_called()

    @mock.patch('common.common.g')
    @mock.patch('common.common.SSHException', Exception)
    @mock.patch('common.common.os')
    @mock.patch('common.common.RSAKey')
    @mock.patch('common.common.exec_command')
    def test_prepare_ssh_command_ssh_exception(self, mock_exec, mock_rsa, mock_os, mock_g):
        current_path = None
        mock_os.path.dirname.return_value = current_path
        key_path = '/id_rsa'
        mock_os.path.join.return_value = key_path
        mock_rsa.from_private_key_file.side_effect = Exception("ex")
        config_name = "japac"
        server = "bdds01"
        hostname = "192.168.88.88"
        client_id = "123"
        tool = "ping"
        param = "192.168.88.54"
        with self.assertRaises(Exception):
            common.prepare_ssh_command(config_name, server, hostname, client_id, tool, param)
            mock_exec.assert_not_called()
            mock_g.user.logger.error.asert_called_once()

    @mock.patch('common.common.management_result')
    @mock.patch('common.common.get_loop_back_ip')
    @mock.patch('common.common.Thread')
    @mock.patch('common.common.update_result_global_stream_result')
    @mock.patch('common.common.os')
    @mock.patch('common.common.RSAKey')
    @mock.patch('common.common.exec_command')
    @mock.patch('common.common.SSHClient')
    @mock.patch('common.common.ssh_open_connection')
    def test_prepare_ssh_command(self, mock_ssh_open_connection, mock_sshclient, mock_exec, mock_rsa, mock_os,
                                 mock_update_result_global_stream_result, mock_thread, mock_get_loop_back_ip, mock_rs):
        current_path = '/'
        mock_os.path.dirname.return_value = current_path
        key_path = '/id_rsa'
        mock_os.path.join.return_value = key_path
        key = mock.Mock()
        mock_rsa.from_private_key_file.return_value = key
        ssh = mock.Mock()
        mock_sshclient.return_value = ssh
        mock_ssh_open_connection.return_value = True
        config_name = "japac"
        server = "bdds01"
        hostname = "192.168.88.88"
        client_id = "123"
        tool = "ping"
        param = "192.168.88.54"
        t = mock.MagicMock()
        mock_thread.return_value = t
        common.prepare_ssh_command(config_name, server, hostname, client_id, tool, param, view_id=1)
        mock_exec.assert_not_called()


    @mock.patch('common.common.g')
    def test_get_bam_data_no_exception(self, mock_g):
        data = {'oid': 1234}
        server = {'name': 'bdds'}
        config = {'id': 1234, 'name': 'config'}
        common.get_bam_data(data)

    @mock.patch('common.common.PortalException', Exception)
    @mock.patch('common.common.g')
    def test_get_bam_data_exception(self, mock_g):
        data = {'oid': 1234}
        server = {'name': 'bdds'}
        config = {'id': 1234, 'name': 'config'}
        mock_g.user.get_api = Exception('ex')
        with self.assertRaises(Exception):
            common.get_bam_data(data)
            mock_g.user.get_api.return_value._api_client.service.getParent.assert_called_once_with(134)
            mock_g.user.get_api.return_value._api_client.service.getEntityById.assert_called_once_with(134)


    @mock.patch('common.common.management_result')
    def test_get_stream_result(self, mock_management_result):
        """
        :param mock_set_rule:
        :return:
        """
        mock_management_result = {
            "japac": {
                "bdds01(192.168.88.88)": {
                    "123": {
                        "status": False
                    }
                }
            }
        }
        config_name = "japac"
        server = "bdds01(192.168.88.88)"
        client_id = "123"
        tool = "ping"
        status = False
        global management_result
        management_result = mock.MagicMock()
        common.get_stream_result(config_name, server, client_id, tool)

    @mock.patch('common.common.management_result')
    def test_clear_all_connection(self, mock_management_result):
        mock_management_result = {
            "japac": {
                "bdds01(192.168.88.88)": {
                    "123": {
                        "status": False
                    }
                }
            }
        }
        config_name = "japac"
        server = "bdds01(192.168.88.88)"
        client_id = "123"

        global management_result
        management_result = mock.MagicMock()
        common.clear_all_connection(config_name, server, client_id)

    @mock.patch('common.common.configparser')
    @mock.patch('common.common.g')
    @mock.patch('common.common.os')
    def test_get_config_case1(self, mock_os, mock_g, mock_config):
        mock_os.path = mock.Mock()
        mock_os.path.exists.return_value = True
        check = mock_config.configParser()
        result = common.get_config("abc")

    @mock.patch('common.common.configparser')
    @mock.patch('common.common.g')
    @mock.patch('common.common.os')
    def test_get_config_case2(self, mock_os, mock_g, mock_config):
        mock_os.path = mock.Mock()
        mock_os.path.exists.return_value = False
        result = common.get_config("abc")
        self.assertEqual(None, result)

    @mock.patch('common.common.configparser')
    @mock.patch('common.common.g')
    @mock.patch('common.common.os')
    def test_get_config_exception(self, mock_os, mock_g, mock_config):
        mock_os.path = mock.Mock()
        mock_os.path.exists = Exception('ex')
        actual = common.get_config("abc")
        self.assertEqual(actual, None)


    @mock.patch('common.common.str')
    @mock.patch('common.common.g')
    def test_get_loop_back_ip(self, mock_g, mock_str):
        ssh = mock.MagicMock()
        view_id = 1
        _, stdout, _ = mock.MagicMock(), mock.MagicMock(), mock.MagicMock()
        ssh.exec_command.return_value = _, stdout, _
        mock_g.user.logger = mock.MagicMock()
        mock_g.user.logger.info().return_value = 'cfff'
        mock_str.return_value = '(127.0.0.1);'
        result = common.get_loop_back_ip(ssh, view_id)
        self.assertEqual('127.0.0.1)', result)


    @mock.patch('common.common.str')
    @mock.patch('common.common.g')
    @mock.patch('common.common.socket.timeout', Exception)
    def test_get_loop_back_ip_exception(self, mock_g, mock_str):
        ssh = mock.MagicMock()
        view_id = 1
        _, stdout, _ = mock.MagicMock(), mock.MagicMock(), mock.MagicMock()
        ssh.exec_command.return_value = Exception("ex")
        mock_g.user.logger = mock.MagicMock()
        mock_g.user.logger.info().return_value = Exception("ex")
        mock_str.return_value = '(127.0.0.1);'
        common.get_loop_back_ip(ssh, view_id)


    @mock.patch('common.common.scp_file_from_server')
    def test_wait_for_scp_success(self, mock_scp_file_from_server):
        ssh = mock.MagicMock()
        bk_file_name = "test"
        result = common.wait_for_scp_success(ssh, bk_file_name, timeout=1)
        self.assertEqual('Timeout!', result)

    @mock.patch('common.common.SCPClient')
    def test_scp_file_from_server(self, mock_scp):
        ssh = mock.MagicMock()
        source_path = "test"
        destination_path = "123"
        common.scp_file_from_server(ssh, source_path, destination_path)



