import os
import socket
from threading import Thread
import traceback
from flask import g
from scp import SCPClient
from .common import get_connection, scp_file_from_server
from .constants import DpkgOption, TCPDUMP_DOWNLOAD_DIR, TCPDUMP_PARENT_DOWNLOAD_DIR, TCP_CAPTURE_FILE_NAME, \
    ALLOWED_INTERFACE, REMOVE_TCPDUMP_SCRIPT, REMOTE_REMOVE_TCPDUMP_SCRIPT_DIR

LISTENING_ON = False


class InstallationResponse():
    def __init__(self, host, status, message):
        self.server_name = host.get("server_name")
        self.server_ip = host.get("server_ip")
        self.status = status
        self.message = message


class TcpDump(object):

    def __init__(self, host, ssh_timeout=30):
        """
        Host { "server_name": "", "server_ip": ""}
        """
        self.host = host
        self.ssh_timeout = ssh_timeout
        self.ssh = get_connection(self.host.get("server_ip"), timeout=ssh_timeout)
        self.scp = None
        self.conn = None

    def _connect(self):
        if self.conn is None:
            try:
                self.ssh = get_connection(self.host.get("server_ip"))
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

    def uninstall_package(self, package=DpkgOption.NAME_PACKAGE):
        """
        Uninstall the package
        """
        # If package has not installed yet, the uninstalled process must be ignored
        if self.check_if_installed_package(package=package):
            # Then execute the process by script
            self.run_script(REMOVE_TCPDUMP_SCRIPT, REMOTE_REMOVE_TCPDUMP_SCRIPT_DIR)
            # After completed uninstalled package, we should check package
            # Ensure to remove package
            if not self.check_if_installed_package(package=package):
                return InstallationResponse(host=self.host,
                                            status=True,
                                            message="Removed tcpdump successfully")
            else:
                return InstallationResponse(host=self.host,
                                            status=False,
                                            message="Error removed tcpdump")
        else:
            return InstallationResponse(host=self.host,
                                        status=False,
                                        message="Ignored process since tcpdump has already removed")

    def run_script(self, script_file, remote_dir):
        """
        Execute the script from remote
        """
        script_path = os.path.join(remote_dir, script_file)

        # Open ftp protocol to check file remotely
        client_sftp = self.ssh.open_sftp()
        # Check if local file is newer than the remote file
        try:
            if script_file not in client_sftp.listdir(remote_dir):
                message = f"The script {script_path} was not found"
                g.user.logger.error(message)
                raise Exception(message)

        except Exception as ex:
            message = f"The script {script_path} was not found"
            g.user.logger.error(message)
            raise Exception(message)

        # close ftp session
        client_sftp.close()

        # Execute the command
        cmd = f"sudo {script_path}"
        self._exec_command(cmd)

    def start(self, data):
        """
        Start to analyze the tcpdump.
        - Support to stop tcpdump automatically when meet conditions:
        timeout, reach max file, number of capture packets, or force stop
        - Tcpdump is running timeout process and terminates it if it is still running after a given period of time

        SUPPORT TO STOP WHEN MEET MAX SIZE FILE
        Since tcpdump don't support stopped automatically
        We use feature ulimit to limit size file.
        """
        # Tcpdump will always create output to same output file (same file name).
        # So write same file with many process can't.
        # Should check tcpdump process in advance
        if not self.check_if_tcpdump_is_running():
            current_user = self.find_the_current_user()

            # TO DO: cmd should move to prepare phase
            TEMPLATE_CMD = \
                f'{data["max_capture_file"]} sudo {data["max_capture_time"]} ' \
                f'tcpdump {data["interface"]} {data["port"]} {data["packets_to_capture"]} ' \
                f'{data["optional"]} -w {TCP_CAPTURE_FILE_NAME} -Z {current_user}'

            g.user.logger.info(f"Analyze Traffic: Command line to run: {TEMPLATE_CMD}")

            # Run the tcpdump process in background
            thread = Thread(target=self._tcpdump_command, args=(self.ssh, TEMPLATE_CMD))
            thread.start()
            thread.join(2)

            # To confirm the tcpdump operate normal.
            global LISTENING_ON
            if LISTENING_ON:
                LISTENING_ON = False
                g.user.logger.error(f"Analyze Traffic: Tcpdump failed to start")
                raise Exception("Tcpdump failed to start")
            return "Tcpdump started successfully"
        else:
            self.disconnect()
            return "Tcpdump is still running"

    def stop(self):
        """
        Kill the current tcpdump process.
        tcpdump is running in timeout command. So if we force to stop tcpdump process.
        we should kill timeout process
        """
        if self.check_if_tcpdump_is_running():
            self._killall_command("timeout")
            if not self.check_if_tcpdump_is_running():
                g.user.logger.info(f"Analyze Traffic: Tcpdump stopped successfully")
                return "Tcpdump stopped successfully"
            else:
                g.user.logger.error(f"Analyze Traffic: Tcpdump failed to stop")
                raise Exception("Tcpdump failed to stop")
        else:
            g.user.logger.info(f"Analyze Traffic: No Tcpdump process to stop")
            return "No Tcpdump process to stop"

    def get_status(self):
        """
        Get tcpdump process: Running or stopped
        """
        if self.check_if_tcpdump_is_running():
            g.user.logger.info(f"Analyze Traffic: Tcpdump status is running")
            return "Running"
        else:
            g.user.logger.info(f"Analyze Traffic: Tcpdump status stopped")
            return "Stopped"

    def check_if_installed_package(self, package):
        """
        Check message from returned remote. If found the installed package, return true.Otherwise, return false
        """
        console = self._check_status_package(package=package, option=DpkgOption.STATUS)
        # Check log console
        for item in console:
            if DpkgOption.CHECK_INSTALL_STATUS in item:
                return False
        return True

    def find_the_current_user(self):
        """
        Show the current user in this process
        Purpose: If tcpdump is running as root, after opening the capture device or input savefile, but
        before opening any savefiles for output, change the user ID to user and the group ID to the primary group
        of user.
        Get the current user and set user by -Z option
        """
        console = self._exec_command(cmd="id -un")
        return console[0]

    def check_if_tcpdump_is_running(self):
        """
        Check the tcpdump whether is running or not
        """
        return self._pgrep_command()

    def _check_status_package(self, package, option):
        """
        Check the status package
        """
        cmd = 'dpkg {0} {1}'.format(option, package)
        return self._exec_command(cmd)

    def _tcpdump_command(self, ssh, cmd):
        """
        Support interface tcpdump command line
        """
        try:
            global LISTENING_ON
            _, stdout, _ = ssh.exec_command('{}'.format(cmd), get_pty=True)

            # Get from console to check tcpdump operate normal
            first_message = stdout.readline().rstrip()
            second_message = stdout.readline().rstrip()
            if 'tcpdump: listening on' not in first_message and 'tcpdump: listening on' not in second_message:
                LISTENING_ON = True

            # Return true if the remote process has exited and returned an exit
            # status. Polling task in here.
            while not stdout.channel.exit_status_ready():
                # for line in iter(stdout.readline, ""):
                #     print(line)
                pass

            # The ssh connection must be closed when terminate tcpdump process.
            # prevent to orphaned ssh connection.
            ssh.close()

        except socket.timeout:
            ssh.close()
            err_mess = 'Timeout to run command!'
            raise Exception(err_mess)
        except Exception as ex:
            ssh.close()
            raise ex

    def _killall_command(self, task):
        """
        Support interface ssh to kill a process
        """
        self._exec_command(cmd=f'sudo killall {task}')

    def _pgrep_command(self):
        """
        Use pgrep to check whether a process is running or not.
        Return true if process is running, Otherwise false
        """
        console = self._exec_command(cmd='pgrep tcpdump')
        return True if console else False

    def _exec_command(self, cmd, timeout=5):
        """
        Support general command line to remote
        """
        try:
            _, stdout, _ = self.ssh.exec_command(cmd, get_pty=True, timeout=timeout)
            console = [x.rstrip() for x in stdout.readlines()]
            g.user.logger.debug(console)
            return console
        except socket.timeout:
            err_mess = 'Timeout to run command!'
            g.user.logger.error(err_mess)
            raise Exception(err_mess)
        except Exception as ex:
            g.user.logger.error(str(ex))
            raise ex

    def get_interface_network(self):
        """
        General tcpdump get interface command
        """
        console = self._exec_command(cmd='sudo tcpdump -D')
        interface_list = self._parser_interface_console(result=console)
        g.user.logger.info(interface_list)
        return interface_list

    def _parser_interface_console(self, result):
        """
        Get an interface info and split to get only the interface name
        Ex: interface info
            1.eth0 [Up, Running]
            2.any (Pseudo-device that captures on all interfaces) [Up, Running]
            3.lo [Up, Running, Loopback]
            4.docker0 [Up]
            5.nflog (Linux netfilter log (NFLOG) interface)
            6.nfqueue (Linux netfilter queue (NFQUEUE) interface)
        Return:
              [
                "eth0",
                "any",
                "lo",
                "docker0",
                "nflog",
                "nfqueue"
              ]
        """
        interface_list = []
        for r in result:
            interface_info = r.split(".")
            interface_name = interface_info[1].split(" ")[0].lower()
            if interface_name in ALLOWED_INTERFACE:
                interface_list.append(interface_name)
        return interface_list

    def check_if_exist_capture_file(self):
        """
        Check the capture file exist in remote host
        """
        return self._exec_command(cmd=f"find . -type f -name  {TCP_CAPTURE_FILE_NAME}")

    def download_and_get_local_capture_file(self):
        """
        Download the capture file and store to local
        """
        try:
            capture_file = self.check_if_exist_capture_file()
            if not capture_file:
                g.user.logger.error(f'{TCP_CAPTURE_FILE_NAME} file was not found')
                raise Exception(f'{TCP_CAPTURE_FILE_NAME} file was not found')

            local_path = os.path.join(TCPDUMP_PARENT_DOWNLOAD_DIR, TCPDUMP_DOWNLOAD_DIR)
            if os.path.exists(local_path):
                # Check if folder has files or not,
                # if yes remove all file and this folder , otherwise just remove this folder
                if len(os.listdir(local_path)) == 0:
                    os.rmdir(local_path)
                else:
                    for f in os.listdir(local_path):
                        file_rm = os.path.join(local_path, f)
                        if os.path.isfile(file_rm):
                            os.remove(file_rm)
                    os.rmdir(local_path)

            os.mkdir(local_path)
            local_capture_path = os.path.join(local_path, TCP_CAPTURE_FILE_NAME)
            scp_file_from_server(self.ssh, TCP_CAPTURE_FILE_NAME, local_capture_path)
            return local_capture_path
        except socket.timeout:
            err_mess = 'Failed to execute command download capture file from: {} : Timeout!'.format(
                self.host.get("server_ip"))
            g.user.logger.error(err_mess)
            raise Exception(err_mess)
        except Exception as ex:
            g.user.logger.error(str(ex))
            g.user.logger.error(traceback.format_exc())
            raise ex
