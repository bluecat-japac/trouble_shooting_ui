# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import socket
import traceback

from flask import g
from scp import SCPClient

from .constants import BamBackup, DEFAULT_BAM_BACKUP_CONFIG
from .common import get_connection, scp_file_from_server, wait_for_scp_success, get_config
from .exceptions import InvalidParam, BamBackupError


class RemoteBAMBackupClient(object):
    def __init__(self, hostname, ssh_timeout=30):
        self.hostname = hostname
        self.ssh_timeout = ssh_timeout
        self.ssh = get_connection(self.hostname)
        self.scp = None
        self.conn = None

    def _connect(self):
        if self.conn is None:
            try:
                self.ssh = get_connection(self.hostname)
                self.scp = SCPClient(self.ssh.get_transport())
            except Exception as e:
                g.user.logger.error(e)
                raise RuntimeError(e)
        return self.ssh

    def disconnect(self):
        try:
            if self.ssh:
                self.ssh.close()
            if self.scp:
                self.scp.close()
        except Exception as e:
            g.user.logger.error(e)

    def read_backup_file(self):
        try:
            _, stdout, _ = self.ssh.exec_command('ls -h -l {}'.format(BamBackup.BACKUP_DATA_DIR), get_pty=True)
            g.user.logger.info('Get Backup file from: {}'.format(self.hostname))
            result = []
            for line in iter(stdout.readline, ""):
                backup_data = line.rstrip().split()
                if backup_data and len(backup_data) == 9:
                    result.append({
                        'name': backup_data[8],
                        'date': '{} {} {}'.format(backup_data[5], backup_data[6], backup_data[7]),
                        'size': backup_data[4]
                    })
            return result
        except socket.timeout:
            err_mess = 'Failed to execute command get backup file from: {} : Timeout!'.format(self.hostname)
            g.user.logger.error(err_mess)
        except Exception as ex:
            g.user.logger.error(str(ex))
            raise ex

    def run_backup_file(self):
        try:
            _, stdout, _ = self.ssh.exec_command(
                'nohup sudo /usr/bin/perl /usr/local/bcn/backup.pl -i {} '.format(BamBackup.DEFAULT_BACKUP_NAME),
                get_pty=True)
            g.user.logger.info('Start to run backup file ...')
            run_message = stdout.readline().rstrip()
            if not run_message or 'nohup: ignoring' in run_message:
                return 'Run backup successfully.'
            raise BamBackupError(run_message)
        except socket.timeout:
            err_mess = 'Failed to execute command run backup file from: {} : Timeout!'.format(self.hostname)
            g.user.logger.error(err_mess)
            raise err_mess
        except Exception as ex:
            g.user.logger.error(str(ex))
            g.user.logger.error(traceback.format_exc())
            raise ex
        finally:
            self.disconnect()

    def check_backup_status(self):
        try:
            g.user.logger.info('Start to get backup status ...')
            _, stdout, _ = self.ssh.exec_command(
                'sudo cat {}'.format(BamBackup.BACKUP_STATUS_PATH), get_pty=True)
            result = []
            for line in iter(stdout.readline, ""):
                backup_data = line.rstrip().split()
                if backup_data and backup_data[-1] in BamBackup.DEFAULT_BACKUP_STATUS:
                    if backup_data[-1] == '----':
                        result.append({
                            'name': backup_data[0],
                            'start_time': backup_data[1],
                            'end_time': backup_data[2],
                            'status': backup_data[-1]
                        })
                        continue
                    end_time = backup_data[3] if len(backup_data) == 5 else '{} {}'.format(backup_data[3], backup_data[4])
                    result.append({
                        'name': backup_data[0],
                        'start_time': '{} {}'.format(backup_data[1], backup_data[2]),
                        'end_time': end_time,
                        'status': backup_data[-1]
                    })
            if not result:
                g.user.logger.warning("Can't read the backup status. Please check the permission.")
        except socket.timeout:
            err_mess = 'Failed to execute command get backup status from: {} : Timeout!'.format(self.hostname)
            g.user.logger.error(err_mess)
            raise err_mess
        except Exception as ex:
            g.user.logger.error(str(ex))
            g.user.logger.error(traceback.format_exc())
            raise ex
        finally:
            self.disconnect()
        return result

    def delete_backup_file(self, bk_files_name):
        bk_list = self.read_backup_file()
        run_message = ''
        try:
            for bk_file_name in bk_files_name:
                if bk_file_name not in [bk.get('name') for bk in bk_list]:
                    raise InvalidParam('Backup File named {} was not found in {}'.format(bk_file_name, self.hostname))
                # Remove bk file in local
                local_bk_path = '{}/{}'.format(BamBackup.DEFAULT_LOCAL_BK_PATH, bk_file_name)
                if os.path.isfile(local_bk_path):
                    os.remove(local_bk_path)
                # Remove bk file in BAM
                _, stdout, _ = self.ssh.exec_command('rm -rf {}/{}'.format(BamBackup.BACKUP_DATA_DIR, bk_file_name),
                                                     get_pty=True)
                g.user.logger.info('Start to delete backup file named {} in {} ...'.format(bk_file_name, self.hostname))
                run_message += stdout.readline().rstrip()
            if not run_message:
                return 'Delete backup files named {} successfully.'.format(', '.join(bk_files_name))
            raise BamBackupError(run_message)
        except socket.timeout:
            err_mess = 'Failed to execute command delete backup file {} from: {} : Timeout!'.format(
                ', '.join(bk_files_name), self.hostname)
            g.user.logger.error(err_mess)
            raise err_mess
        except Exception as ex:
            g.user.logger.error(str(ex))
            g.user.logger.error(traceback.format_exc())
            raise ex
        finally:
            self.disconnect()

    def download_and_get_local_backup_file(self, bk_file_name):
        bk_list = self.read_backup_file()
        if bk_file_name not in [bk.get('name') for bk in bk_list]:
            raise InvalidParam('Backup File named {} was not found in {}'.format(bk_file_name, self.hostname))
        try:
            if not os.path.isdir(BamBackup.DEFAULT_LOCAL_BK_PATH):
                os.mkdir(BamBackup.DEFAULT_LOCAL_BK_PATH)
            local_bk_path = '{}/{}'.format(BamBackup.DEFAULT_LOCAL_BK_PATH, bk_file_name)
            config_file = get_config(DEFAULT_BAM_BACKUP_CONFIG)
            max_file_store = config_file.get("BAM_BACKUP", "max_file_store", fallback="")
            max_file_store = 5 if not max_file_store else int(max_file_store)
            list_of_files = os.listdir(BamBackup.DEFAULT_LOCAL_BK_PATH)
            full_path = ["{}/{}".format(BamBackup.DEFAULT_LOCAL_BK_PATH, x) for x in list_of_files]
            if len(list_of_files) >= max_file_store:
                oldest_file = min(full_path, key=os.path.getctime)
                os.remove(oldest_file)

            scp_file_from_server(self.ssh, '{}/{}'.format(BamBackup.BACKUP_DATA_DIR, bk_file_name), local_bk_path)
            check_timeout = wait_for_scp_success(self.ssh, bk_file_name)
            return check_timeout if check_timeout else local_bk_path
        except socket.timeout:
            err_mess = 'Failed to execute command download backup file {} from: {} : Timeout!'.format(bk_file_name,
                                                                                                      self.hostname)
            g.user.logger.error(err_mess)
            raise err_mess
        except Exception as ex:
            g.user.logger.error(str(ex))
            g.user.logger.error(traceback.format_exc())
            raise ex
        finally:
            self.disconnect()
