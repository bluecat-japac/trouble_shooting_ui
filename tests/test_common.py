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
    @mock.patch('common.common.os')
    def test_get_bam_ip_in_os_environ(self, mock_os):
        mock_os.environ = {'BAM_IP': '1.1.1.1/Services/API?wsdl'}
        expect = '1.1.1.1'
        actual = common.get_bam_ip()
        self.assertEqual(expect, actual)

    @mock.patch('common.common.os')
    def test_get_bam_ip_in_os_environ_http(self, mock_os):
        mock_os.environ = {'BAM_IP': 'http://1.1.1.2/Services/API?wsdl'}
        expect = '1.1.1.2'
        actual = common.get_bam_ip()
        self.assertEqual(expect, actual)

    @mock.patch('common.common.user_config')
    @mock.patch('common.common.os')
    def test_get_bam_ip_in_config_file_list(self, mock_os, mock_user_config):
        mock_os.environ = {'no_bam_ip': ''}
        mock_user_config.api_url = [('1.2.3.4', 'http://172.27.19.203/Services/API?wsdl')]
        expect = '1.2.3.4'
        actual = common.get_bam_ip()
        self.assertEqual(expect, actual)

    @mock.patch('common.common.user_config')
    @mock.patch('common.common.os')
    def test_get_bam_ip_in_config_file_str(self, mock_os, mock_user_config):
        mock_os.environ = {'no_bam_ip': ''}
        mock_user_config.api_url = 'http://172.27.19.203/Services/API?wsdl'
        expect = '172.27.19.203'
        actual = common.get_bam_ip()
        self.assertEqual(expect, actual)

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

    @mock.patch('common.common.Thread')
    @mock.patch('common.common.update_result_global_stream_result')
    @mock.patch('common.common.os')
    @mock.patch('common.common.RSAKey')
    @mock.patch('common.common.exec_command')
    @mock.patch('common.common.SSHClient')
    @mock.patch('common.common.ssh_open_connection')
    def test_prepare_ssh_command(self, mock_ssh_open_connection, mock_sshclient, mock_exec, mock_rsa, mock_os,
                                 mock_update_result_global_stream_result, mock_thread):
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
        common.prepare_ssh_command(config_name, server, hostname, client_id, tool, param)
        mock_exec.assert_not_called()

    @mock.patch('common.common.get_server_ip')
    @mock.patch('common.common.g')
    def test_get_bam_data_no_exception(self, mock_g, mock_get_server_ip):
        data = {'oid': 1234}
        server = {'name': 'bdds'}
        mock_g.user.get_api.return_value._api_client.service.getEntityById.return_value = server
        mock_get_server_ip.return_value = '1.2.3.4'
        config = {'id': 5678, 'name': 'config'}
        mock_g.user.get_api.return_value._api_client.service.getParent.return_value = config
        actual = common.get_bam_data(data)
        expect = ('bdds(1.2.3.4)', 'config', 5678)
        self.assertEqual(expect, actual)
        mock_g.user.get_api.return_value._api_client.service.getEntityById.assert_called_once_with(1234)
        mock_g.user.get_api.return_value._api_client.service.getParent.assert_called_once_with(1234)

    @mock.patch('common.common.get_server_ip')
    @mock.patch('common.common.g')
    def test_get_bam_data_exception(self, mock_g, mock_get_server_ip):
        data = {'oid': 1234}
        server = {'name': 'bdds'}
        mock_g.user.get_api.return_value._api_client.service.getEntityById.return_value = server
        mock_get_server_ip.side_effect = Exception()
        config = {'id': 5678, 'name': 'config'}
        mock_g.user.get_api.return_value._api_client.service.getParent.return_value = config
        actual = common.get_bam_data(data)
        expect = ('', '', '')
        self.assertEqual(expect, actual)
        mock_g.user.get_api.return_value._api_client.service.getEntityById.assert_called_once_with(1234)
        mock_g.user.get_api.return_value._api_client.service.getParent.assert_not_called()
