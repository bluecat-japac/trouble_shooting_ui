import unittest
import context
from unittest import mock  # pylint:disable=import-error
from common.backup_file import RemoteBAMBackupClient


class TestBackupFile(unittest.TestCase):
    @mock.patch('common.backup_file.get_connection')
    def test_initial_value(self, mock_get_connection):
        backup_test = RemoteBAMBackupClient("abc", 1)
        assert backup_test.hostname == "abc"
        assert backup_test.ssh_timeout == 1

    @mock.patch('common.backup_file.SCPClient')
    @mock.patch('common.backup_file.get_connection')
    def test_connect_no_exception(self, mock_get_connection, mock_scp):
        backup_test = RemoteBAMBackupClient("abc", 1)
        backup_test.ssh.get_transport.return_value = "test"
        backup_test._connect()
        mock_scp.assert_called_once_with("test")

    @mock.patch('common.backup_file.g')
    @mock.patch('common.backup_file.SCPClient')
    @mock.patch('common.backup_file.get_connection')
    def test_connect_exception(self, mock_get_connection, mock_scp, mock_g):
        backup_test = RemoteBAMBackupClient("abc", 1)
        backup_test.ssh.get_transport = Exception('ex')
        with self.assertRaises(Exception):
            backup_test._connect()

    @mock.patch('common.backup_file.get_connection')
    def test_disconnect(self, mock_get_connection):
        backup_test = RemoteBAMBackupClient("abc", 1)
        backup_test.scp = mock.Mock()
        backup_test.disconnect()

    @mock.patch('common.backup_file.g')
    @mock.patch('common.backup_file.get_connection')
    def test_disconnect_exception(self, mock_get_connection, mock_g):
        backup_test = RemoteBAMBackupClient("abc", 1)
        backup_test.ssh.close = Exception('ex')
        backup_test.disconnect()
        mock_g.user.logger.error.assert_called_once()

    @mock.patch('common.backup_file.iter')
    @mock.patch('common.backup_file.g')
    @mock.patch('common.backup_file.get_connection')
    def test_read_backup_file(self, mock_get_connection, mock_g, mock_iter):
        backup_test = RemoteBAMBackupClient("abc", 1)
        _, stdout, _ = mock.MagicMock(), mock.MagicMock(), mock.MagicMock()
        backup_test.ssh.exec_command.return_value = _, stdout, _
        mock_g.user.logger.info().return_value = 'test'
        mock_iter.return_value = ["1 2 3 4 5 6 7 8 9", "233333"]
        result = backup_test.read_backup_file()
        check = [{'name': '9', 'date': '6 7 8', 'size': '5'}]
        self.assertEqual(result, check)


    @mock.patch('common.backup_file.iter')
    @mock.patch('common.backup_file.g')
    @mock.patch('common.backup_file.get_connection')
    @mock.patch('common.backup_file.socket.timeout', Exception)
    def test_read_backup_file_timeout(self, mock_get_connection, mock_g, mock_iter):
        backup_test = RemoteBAMBackupClient("abc", 1)
        _, stdout, _ = mock.MagicMock(), mock.MagicMock(), mock.MagicMock()
        backup_test.ssh.exec_command.return_value = _, stdout, _
        mock_g.user.logger.info.side_effect = Exception('ex')
        backup_test.read_backup_file()
        mock_g.user.logger.error.assert_called_once()

    @mock.patch('common.backup_file.iter')
    @mock.patch('common.backup_file.g')
    @mock.patch('common.backup_file.get_connection')
    def test_read_backup_file_exception(self, mock_get_connection, mock_g, mock_iter):
        backup_test = RemoteBAMBackupClient("abc", 1)
        _, stdout, _ = mock.MagicMock(), mock.MagicMock(), mock.MagicMock()
        backup_test.ssh.exec_command.return_value = _, stdout, _
        mock_g.user.logger.info.side_effect = Exception('ex')
        with self.assertRaises(Exception):
            backup_test.read_backup_file()

    @mock.patch('common.backup_file.g')
    @mock.patch('common.backup_file.get_connection')
    def test_run_backup_file(self, mock_get_connection, mock_g):
        backup_test = RemoteBAMBackupClient("abc", 1)
        _, stdout, _ = mock.MagicMock(), mock.MagicMock(), mock.MagicMock()
        backup_test.ssh.exec_command.return_value = _, stdout, _
        stdout.readline.return_value = 'nohup: ignoring'
        mock_g.user.logger.info().return_value = 'test'
        result = backup_test.run_backup_file()
        check = 'Run backup successfully.'
        self.assertEqual(check, result)

    @mock.patch('common.backup_file.g')
    @mock.patch('common.backup_file.get_connection')
    def test_run_backup_file_case_raise(self, mock_get_connection, mock_g):
        backup_test = RemoteBAMBackupClient("abc", 1)
        _, stdout, _ = mock.MagicMock(), mock.MagicMock(), mock.MagicMock()
        backup_test.ssh.exec_command.return_value = _, stdout, _
        stdout.readline.return_value = 'abc'
        mock_g.user.logger.info().return_value = 'test'
        with self.assertRaises(Exception):
            backup_test.run_backup_file()

    @mock.patch('common.backup_file.g')
    @mock.patch('common.backup_file.get_connection')
    @mock.patch('common.backup_file.socket.timeout', Exception)
    def test_run_backup_file_timeout(self, mock_get_connection, mock_g):
        backup_test = RemoteBAMBackupClient("abc", 1)
        _, stdout, _ = mock.MagicMock(), mock.MagicMock(), mock.MagicMock()
        backup_test.ssh.exec_command.return_value = _, stdout, _
        mock_g.user.logger.info.side_effect = Exception()
        with self.assertRaises(Exception):
            backup_test.run_backup_file()

    @mock.patch('common.backup_file.g')
    @mock.patch('common.backup_file.get_connection')
    def test_run_backup_file_exception(self, mock_get_connection, mock_g):
        backup_test = RemoteBAMBackupClient("abc", 1)
        _, stdout, _ = mock.MagicMock(), mock.MagicMock(), mock.MagicMock()
        backup_test.ssh.exec_command.return_value = _, stdout, _
        mock_g.user.logger.info.side_effect = Exception()
        with self.assertRaises(Exception):
            backup_test.run_backup_file()

    @mock.patch('common.backup_file.g')
    @mock.patch('common.backup_file.get_connection')
    @mock.patch('common.backup_file.socket.timeout', Exception)
    def test_check_backup_status_timeout(self, mock_get_connection, mock_g):
        backup_test = RemoteBAMBackupClient("abc", 1)
        mock_g.user.logger.info.side_effect = Exception('ex')
        with self.assertRaises(Exception):
            backup_test.check_backup_status()

    @mock.patch('common.backup_file.g')
    @mock.patch('common.backup_file.get_connection')
    def test_check_backup_status_exception(self, mock_get_connection, mock_g):
        backup_test = RemoteBAMBackupClient("abc", 1)
        mock_g.user.logger.info.side_effect = Exception('ex')
        with self.assertRaises(Exception):
            backup_test.check_backup_status()

    @mock.patch('common.backup_file.g')
    @mock.patch('common.backup_file.get_connection')
    def test_delete_backup_file_case1(self, mock_get_connection, mock_g):
        backup_test = RemoteBAMBackupClient("abc", 1)
        bk_files_name = "t"
        backup_test.read_backup_file = mock.MagicMock(side_effect=[[{"name": "t1"}, {"name": "t2"}, {"name": "t3"}], [2, 3, 4]])
        with self.assertRaises(Exception):
            backup_test.delete_backup_file(bk_files_name)

    @mock.patch('common.backup_file.os')
    @mock.patch('common.backup_file.g')
    @mock.patch('common.backup_file.get_connection')
    def test_delete_backup_file_case2(self, mock_get_connection, mock_g, mock_os):
        backup_test = RemoteBAMBackupClient("abc", 1)
        bk_files_name = "t"
        backup_test.read_backup_file = mock.MagicMock(side_effect=[[{"name": "t"}, {"name": "t2"}, {"name": "t3"}], [2, 3, 4]])
        mock_os.path.isfile.return_value = True
        _, stdout, _ = mock.MagicMock(), mock.MagicMock(), mock.MagicMock()
        backup_test.ssh.exec_command.return_value = _, stdout, _
        mock_g.user.logger.info().return_value = "log"
        stdout.readline.return_value = ""
        check = 'Delete backup files named t successfully.'
        result = backup_test.delete_backup_file(bk_files_name)
        self.assertEqual(check, result)

    @mock.patch('common.backup_file.os')
    @mock.patch('common.backup_file.g')
    @mock.patch('common.backup_file.get_connection')
    def test_delete_backup_file_case3(self, mock_get_connection, mock_g, mock_os):
        backup_test = RemoteBAMBackupClient("abc", 1)
        bk_files_name = "t"
        backup_test.read_backup_file = mock.MagicMock(side_effect=[[{"name": "t"}, {"name": "t2"}, {"name": "t3"}], [2, 3, 4]])
        mock_os.path.isfile.return_value = True
        _, stdout, _ = mock.MagicMock(), mock.MagicMock(), mock.MagicMock()
        backup_test.ssh.exec_command.return_value = _, stdout, _
        mock_g.user.logger.info().return_value = "log"
        stdout.readline.return_value = "case3"
        with self.assertRaises(Exception):
            result = backup_test.delete_backup_file(bk_files_name)

    @mock.patch('common.backup_file.os')
    @mock.patch('common.backup_file.g')
    @mock.patch('common.backup_file.get_connection')
    @mock.patch('common.backup_file.socket.timeout', Exception)
    def test_delete_backup_file_timeout(self, mock_get_connection, mock_g, mock_os):
        backup_test = RemoteBAMBackupClient("abc", 1)
        bk_files_name = "t"
        backup_test.read_backup_file = mock.MagicMock(side_effect=[[{"name": "t"}, {"name": "t2"}, {"name": "t3"}], [2, 3, 4]])
        mock_os.path.isfile.return_value = True
        _, stdout, _ = mock.MagicMock(), mock.MagicMock(), mock.MagicMock()
        backup_test.ssh.exec_command.return_value = _, stdout, _
        mock_g.user.logger.info.side_effect = Exception('ex')
        with self.assertRaises(Exception):
            backup_test.delete_backup_file(bk_files_name)

    @mock.patch('common.backup_file.str')
    @mock.patch('common.backup_file.os')
    @mock.patch('common.backup_file.g')
    @mock.patch('common.backup_file.get_connection')
    def test_delete_backup_file_exception(self, mock_get_connection, mock_g, mock_os, mock_str):
        backup_test = RemoteBAMBackupClient("abc", 1)
        bk_files_name = "t"
        backup_test.read_backup_file = mock.MagicMock(side_effect=[[{"name": "t"}, {"name": "t2"}, {"name": "t3"}], [2, 3, 4]])
        mock_os.path.isfile.return_value = True
        _, stdout, _ = mock.MagicMock(), mock.MagicMock(), mock.MagicMock()
        backup_test.ssh.exec_command.return_value = _, stdout, _
        mock_g.user.logger.info.side_effect = Exception('ex')
        with self.assertRaises(Exception):
            backup_test.delete_backup_file(bk_files_name)

    @mock.patch('common.backup_file.get_connection')
    def test_download_and_get_local_backup_file_invalid_param(self, mock_get_connection):
        backup_test = RemoteBAMBackupClient("abc", 1)
        bk_files_name = "t"
        backup_test.read_backup_file = mock.MagicMock(side_effect=[[{"name": "t1"}, {"name": "t2"}, {"name": "t3"}], [2, 3, 4]])
        with self.assertRaises(Exception):
            backup_test.download_and_get_local_backup_file(bk_files_name)

    @mock.patch('common.backup_file.wait_for_scp_success')
    @mock.patch('common.backup_file.scp_file_from_server')
    @mock.patch('common.backup_file.os')
    @mock.patch('common.backup_file.get_connection')
    def test_download_and_get_local_backup_file(self, mock_get_connection, mock_os, mock_scp_file_from_server, mock_wait_for_scp_success):
        backup_test = RemoteBAMBackupClient("abc", 1)
        bk_files_name = "t"
        backup_test.read_backup_file = mock.MagicMock(side_effect=[[{"name": "t"}, {"name": "t2"}, {"name": "t3"}], [2, 3, 4]])
        mock_os.path.isdir.return_value = ''
        mock_os.listdir.return_value = "1234567"
        mock_os.path.getctime.return_value = 20
        mock_wait_for_scp_success.return_value = "Exactly"
        result = backup_test.download_and_get_local_backup_file(bk_files_name)
        self.assertEqual(result, 'Exactly')

    @mock.patch('common.backup_file.g')
    @mock.patch('common.backup_file.wait_for_scp_success')
    @mock.patch('common.backup_file.scp_file_from_server')
    @mock.patch('common.backup_file.os')
    @mock.patch('common.backup_file.get_connection')
    @mock.patch('common.backup_file.socket.timeout', Exception)
    def test_download_and_get_local_backup_file_timeout(self, mock_get_connection, mock_os, mock_scp_file_from_server, mock_wait_for_scp_success, mock_g):
        backup_test = RemoteBAMBackupClient("abc", 1)
        bk_files_name = "t"
        backup_test.read_backup_file = mock.MagicMock(side_effect=[[{"name": "t"}, {"name": "t2"}, {"name": "t3"}], [2, 3, 4]])
        mock_os.path.isdir = mock.MagicMock(side_effect=Exception('ex'))
        with self.assertRaises(Exception):
            result = backup_test.download_and_get_local_backup_file(bk_files_name)

    @mock.patch('common.backup_file.g')
    @mock.patch('common.backup_file.str')
    @mock.patch('common.backup_file.wait_for_scp_success')
    @mock.patch('common.backup_file.scp_file_from_server')
    @mock.patch('common.backup_file.os')
    @mock.patch('common.backup_file.get_connection')
    def test_download_and_get_local_backup_file_exception(self, mock_get_connection, mock_os, mock_scp_file_from_server, mock_wait_for_scp_success, mock_str, mock_g):
        backup_test = RemoteBAMBackupClient("abc", 1)
        bk_files_name = "t"
        backup_test.read_backup_file = mock.MagicMock(side_effect=[[{"name": "t"}, {"name": "t2"}, {"name": "t3"}], [2, 3, 4]])
        mock_os.path.isdir = mock.MagicMock(side_effect=Exception('ex'))
        with self.assertRaises(Exception):
            result = backup_test.download_and_get_local_backup_file(bk_files_name)

