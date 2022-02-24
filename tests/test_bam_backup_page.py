import unittest
import context
from unittest import mock
from bam_backup import bam_backup_page


class TestBamBackupPage(unittest.TestCase):
    @mock.patch('bam_backup.bam_backup_page.os')
    def test_module_path(self, mock_os):
        bam_backup_page.module_path()

    @mock.patch('bam_backup.bam_backup_page.g')
    @mock.patch('bam_backup.bam_backup_page.render_template')
    def test_bam_backup_bam_backup_page(self, mock_render, mock_g):
        mock_render.return_value = "test"
        result = bam_backup_page.bam_backup_bam_backup_page()
        self.assertEqual(result, 'test')

    @mock.patch('bam_backup.bam_backup_page.jsonify')
    @mock.patch('bam_backup.bam_backup_page.g')
    @mock.patch('bam_backup.bam_backup_page.RemoteBAMBackupClient')
    @mock.patch('bam_backup.bam_backup_page.bam_backup_ns')
    def test_get_bam(self, mock_ns, mock_remote, mock_g, mock_json):
        backup_file_name = "abc"
        mock_json.return_value = "test"
        result = bam_backup_page.BAMBackup.get(self, backup_file_name)
        self.assertEqual(result, 'test')

    @mock.patch('bam_backup.bam_backup_page.RemoteBAMBackupClient')
    @mock.patch('bam_backup.bam_backup_page.make_response')
    @mock.patch('bam_backup.bam_backup_page.jsonify')
    @mock.patch('bam_backup.bam_backup_page.g')
    @mock.patch('bam_backup.bam_backup_page.bam_backup_ns')
    @mock.patch('bam_backup.bam_backup_page.UserException', Exception)
    def test_get_user_exception(self, mock_ns, mock_g, mock_json, mock_response, mock_remote):
        backup_file_name = "abc"
        mock_json.side_effect = Exception()
        mock_response.return_value = "test"
        with self.assertRaises(Exception):
            result = bam_backup_page.BAMBackup.get(self, backup_file_name)

    @mock.patch('bam_backup.bam_backup_page.RemoteBAMBackupClient')
    @mock.patch('bam_backup.bam_backup_page.make_response')
    @mock.patch('bam_backup.bam_backup_page.jsonify')
    @mock.patch('bam_backup.bam_backup_page.g')
    @mock.patch('bam_backup.bam_backup_page.bam_backup_ns')
    def test_get_exception(self, mock_ns, mock_g, mock_json, mock_response, mock_remote):
        mock_json.side_effect = Exception()
        backup_file_name = "abc"
        mock_response.return_value = "check"
        with self.assertRaises(Exception):
            result = bam_backup_page.BAMBackup.get(self, backup_file_name)
        # self.assertEqual(result, 'check')

    @mock.patch('bam_backup.bam_backup_page.send_file')
    @mock.patch('bam_backup.bam_backup_page.RemoteBAMBackupClient')
    @mock.patch('bam_backup.bam_backup_page.g')
    def test_get_download(self, mock_g, mock_remote, mock_send_file):
        mock_send_file.return_value = "done"
        backup_file_name = "abc"
        check = ('done', 200)
        result = bam_backup_page.DownloadBAMBackup.get(self, backup_file_name)
        self.assertEqual(result, check)

    @mock.patch('bam_backup.bam_backup_page.jsonify')
    @mock.patch('bam_backup.bam_backup_page.make_response')
    @mock.patch('bam_backup.bam_backup_page.send_file')
    @mock.patch('bam_backup.bam_backup_page.RemoteBAMBackupClient')
    @mock.patch('bam_backup.bam_backup_page.g')
    @mock.patch('bam_backup.bam_backup_page.UserException', Exception)
    def test_get_download_user_exception(self, mock_g, mock_remote, mock_send_file, mock_response, mock_json):
        mock_g.user.get_api_netloc.side_effect = Exception()
        mock_response.return_value = "test"
        backup_file_name = "abc"
        result = bam_backup_page.DownloadBAMBackup.get(self, backup_file_name)
        self.assertEqual(result, 'test')

    @mock.patch('bam_backup.bam_backup_page.jsonify')
    @mock.patch('bam_backup.bam_backup_page.make_response')
    @mock.patch('bam_backup.bam_backup_page.send_file')
    @mock.patch('bam_backup.bam_backup_page.RemoteBAMBackupClient')
    @mock.patch('bam_backup.bam_backup_page.g')
    def test_get_download_exception(self, mock_g, mock_remote, mock_send_file, mock_response, mock_json):
        mock_g.user.get_api_netloc.side_effect = Exception()
        mock_response.return_value = "test"
        backup_file_name = "abc"
        result = bam_backup_page.DownloadBAMBackup.get(self, backup_file_name)
        self.assertEqual(result, 'test')

    @mock.patch('bam_backup.bam_backup_page.jsonify')
    @mock.patch('bam_backup.bam_backup_page.RemoteBAMBackupClient')
    @mock.patch('bam_backup.bam_backup_page.g')
    def test_post_run(self, mock_g, mock_remote, mock_json):
        mock_json.return_value = "test"
        result = bam_backup_page.RunBAMBackup.post(self)
        self.assertEqual(result, 'test')

    @mock.patch('bam_backup.bam_backup_page.make_response')
    @mock.patch('bam_backup.bam_backup_page.jsonify')
    @mock.patch('bam_backup.bam_backup_page.RemoteBAMBackupClient')
    @mock.patch('bam_backup.bam_backup_page.g')
    @mock.patch('bam_backup.bam_backup_page.UserException', Exception)
    def test_post_run_user_exception(self, mock_g, mock_remote, mock_json, mock_response):
        mock_g.user.get_api_netloc.side_effect = Exception()
        mock_response.return_value = "test"
        result = bam_backup_page.RunBAMBackup.post(self)
        self.assertEqual(result, 'test')

    @mock.patch('bam_backup.bam_backup_page.make_response')
    @mock.patch('bam_backup.bam_backup_page.jsonify')
    @mock.patch('bam_backup.bam_backup_page.RemoteBAMBackupClient')
    @mock.patch('bam_backup.bam_backup_page.g')
    def test_post_run_exception(self, mock_g, mock_remote, mock_json, mock_response):
        mock_g.user.get_api_netloc.side_effect = Exception()
        mock_response.return_value = "test"
        result = bam_backup_page.RunBAMBackup.post(self)
        self.assertEqual(result, 'test')

    @mock.patch('bam_backup.bam_backup_page.make_response')
    @mock.patch('bam_backup.bam_backup_page.jsonify')
    @mock.patch('bam_backup.bam_backup_page.RemoteBAMBackupClient')
    @mock.patch('bam_backup.bam_backup_page.g')
    def test_get_check(self,  mock_g, mock_remote, mock_json, mock_response):
        mock_json.return_value = "test"
        result = bam_backup_page.CheckBackupStatus.get(self)
        self.assertEqual(result, 'test')

    @mock.patch('bam_backup.bam_backup_page.make_response')
    @mock.patch('bam_backup.bam_backup_page.jsonify')
    @mock.patch('bam_backup.bam_backup_page.RemoteBAMBackupClient')
    @mock.patch('bam_backup.bam_backup_page.g')
    @mock.patch('bam_backup.bam_backup_page.UserException', Exception)
    def test_get_check_user_exception(self, mock_g, mock_remote, mock_json, mock_response):
        mock_g.user.get_api_netloc.side_effect = Exception()
        mock_response.return_value = "test"
        result = bam_backup_page.CheckBackupStatus.get(self)
        self.assertEqual(result, 'test')

    @mock.patch('bam_backup.bam_backup_page.make_response')
    @mock.patch('bam_backup.bam_backup_page.jsonify')
    @mock.patch('bam_backup.bam_backup_page.RemoteBAMBackupClient')
    @mock.patch('bam_backup.bam_backup_page.g')
    def test_get_check_exception(self, mock_g, mock_remote, mock_json, mock_response):
        mock_g.user.get_api_netloc.side_effect = Exception()
        mock_response.return_value = "test"
        result = bam_backup_page.CheckBackupStatus.get(self)
        self.assertEqual(result, 'test')

    @mock.patch('bam_backup.bam_backup_page.make_response')
    @mock.patch('bam_backup.bam_backup_page.jsonify')
    @mock.patch('bam_backup.bam_backup_page.RemoteBAMBackupClient')
    @mock.patch('bam_backup.bam_backup_page.g')
    def test_get_bam_backup_file(self, mock_g, mock_remote, mock_json, mock_response):
        mock_json.return_value = "test"
        result = bam_backup_page.BAMBackupFiles.get(self)
        self.assertEqual(result, 'test')

    @mock.patch('bam_backup.bam_backup_page.make_response')
    @mock.patch('bam_backup.bam_backup_page.jsonify')
    @mock.patch('bam_backup.bam_backup_page.RemoteBAMBackupClient')
    @mock.patch('bam_backup.bam_backup_page.g')
    @mock.patch('bam_backup.bam_backup_page.UserException', Exception)
    def test_get_bam_backup_file_user_exception(self, mock_g, mock_remote, mock_json, mock_response):
        mock_json.side_effect = Exception('ex')
        with self.assertRaises(Exception):
            result = bam_backup_page.BAMBackupFiles.get(self)

    @mock.patch('bam_backup.bam_backup_page.make_response')
    @mock.patch('bam_backup.bam_backup_page.jsonify')
    @mock.patch('bam_backup.bam_backup_page.RemoteBAMBackupClient')
    @mock.patch('bam_backup.bam_backup_page.g')
    def test_get_bam_backup_file_exception(self, mock_g, mock_remote, mock_json, mock_response):
        mock_json.side_effect = Exception('ex')
        with self.assertRaises(Exception):
            result = bam_backup_page.BAMBackupFiles.get(self)

    @mock.patch('bam_backup.bam_backup_page.make_response')
    @mock.patch('bam_backup.bam_backup_page.jsonify')
    @mock.patch('bam_backup.bam_backup_page.RemoteBAMBackupClient')
    @mock.patch('bam_backup.bam_backup_page.g')
    def test_delete_bam_backup_file(self, mock_g, mock_remote, mock_json, mock_response):
        mock_json.return_value = "test"
        result = bam_backup_page.BAMBackupFiles.delete(self)
        self.assertEqual(result, 'test')

    @mock.patch('bam_backup.bam_backup_page.make_response')
    @mock.patch('bam_backup.bam_backup_page.jsonify')
    @mock.patch('bam_backup.bam_backup_page.RemoteBAMBackupClient')
    @mock.patch('bam_backup.bam_backup_page.g')
    @mock.patch('bam_backup.bam_backup_page.UserException', Exception)
    def test_delete_bam_backup_file_user_exception(self, mock_g, mock_remote, mock_json, mock_response):
        mock_json.side_effect = Exception('ex')
        with self.assertRaises(Exception):
            result = bam_backup_page.BAMBackupFiles.delete(self)

    @mock.patch('bam_backup.bam_backup_page.make_response')
    @mock.patch('bam_backup.bam_backup_page.jsonify')
    @mock.patch('bam_backup.bam_backup_page.RemoteBAMBackupClient')
    @mock.patch('bam_backup.bam_backup_page.g')
    def test_delete_bam_backup_file_exception(self, mock_g, mock_remote, mock_json, mock_response):
        mock_json.side_effect = Exception('ex')
        with self.assertRaises(Exception):
            result = bam_backup_page.BAMBackupFiles.delete(self)
