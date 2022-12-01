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

import re
import os
import time
import datetime
import socket
import traceback
import configparser
import bluecat_portal.config as user_config
from os import walk

from threading import Thread
from flask import g
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.ssh_exception import AuthenticationException, SSHException
from scp import SCPClient  # pylint:disable=import-error
from bluecat.api_exception import PortalException

from .constants import NAMED_PATH, DEFAULT_USER, DEFAULT_TIMEOUT, DEFAULT_SSH_KEY_PATH, BamBackup, \
    DEFAULT_TCPDUMP_CONFIG
from .exceptions import InvalidParam

stream_result = ""
management_result = {}


def get_bam_name():
    """
    :return: Alias BAM
    """
    bam_ip = g.user.get_api_netloc()
    if hasattr(user_config, 'api_url'):
        if isinstance(user_config.api_url, str):
            return user_config.api_url.split('/')[2]
        else:
            try:
                for bam in user_config.api_url:
                    if '/Services' in bam[1] and bam_ip == re.search('//(.+?)/', bam[1]).group(1):
                        return bam[0]
                    elif bam_ip == bam[1].split('//')[1]:
                        return bam[0]
            except Exception as ex:
                g.user.logger.error("Exception get bam name: {}".format(str(ex)))
                g.user.logger.error(traceback.format_exc())

    raise PortalException(
        'No BAM configured in config.py')


def ssh_open_connection(ssh, hostname, username, key, timeout, **kwargs):
    """
    :param ssh:
    :param key:
    :param hostname:
    :param username:
    :param timeout:
    :return:
    """
    g.user.logger.info(
        'Connecting to Server {} ...'.format(hostname))
    try:
        ssh.load_system_host_keys()
        ssh.connect(hostname, username=username,
                    pkey=key, timeout=timeout, **kwargs)
        return True
    except AuthenticationException:
        g.user.logger.error(
            "Exception trying to connect to server: \nSSH key hasn't been copy to server yet: ssh-copy-id -i <key> bluecat@<server>")
        g.user.logger.error(traceback.format_exc())
        return False
    except AttributeError:
        g.user.logger.error(
            'Exception trying to connect to server: Problem with key file!')
        g.user.logger.error(traceback.format_exc())
        return False
    except Exception as e:
        g.user.logger.error(
            'Exception trying to connect to server {} : {}'.format(hostname, e))
        g.user.logger.error(traceback.format_exc())
        return False


def exec_command(ssh, cmd, config_name, server, client_id, tool):
    """
    :param ssh:
    :param cmd:
    :param config_name:
    :param server:
    :param client_id:
    :param tool:
    :return:
    """
    try:
        global management_result
        _, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        for line in iter(stdout.readline, ""):
            status = False
            stream_result = management_result[config_name][server][client_id][tool]
            stream_result += line
            # Update global stream result
            update_result_global_stream_result(
                config_name, server, client_id, tool, stream_result, status)
        # update status global stream result
        update_status_global_stream_result(config_name, server, client_id, True)
    except socket.timeout:
        output = 'Failed to execute command: {} : Timeout!'.format(cmd)
        g.user.logger.error(output)
        g.user.logger.error(traceback.format_exc())


def prepare_ssh_command(config_name, server, hostname, client_id, tool, param, view_id=0, **kwargs):
    """
    :param config_name:
    :param server:
    :param hostname:
    :param client_id:
    :param tool:
    :param param:
    :param username:
    :param timeout:
    :return:
    """
    global management_result
    ssh = get_connection(hostname, **kwargs)
    dig_cmd = "dig {}"
    if view_id != 0:
        loop_back_ip = get_loop_back_ip(ssh, view_id)
        if loop_back_ip:
            dig_cmd += ' -b {}'.format(loop_back_ip)
    tool_cmd = {
        "ping": "ping -c 10 {}",
        "dig": dig_cmd,
        "traceroute": "traceroute {}"
    }

    if ":" in param:
        tool_cmd = {
            "ping": "ping6 -c 10 {}",
            "dig": dig_cmd,
            "traceroute": "traceroute6 {}"
        }
    cmd = tool_cmd.get(tool).format(param)
    update_result_global_stream_result(
        config_name, server, client_id, tool, stream_result, "False")
    t = Thread(target=exec_command, args=(
        ssh, cmd, config_name, server, client_id, tool))
    t.start()
    management_result[config_name][server][client_id]['ssh'] = ssh
    management_result[config_name][server][client_id]['thread'] = t


def get_stream_result(config_name, server, client_id, tool):
    global management_result
    stream_result = management_result[config_name][server][client_id][tool]
    status = management_result[config_name][server][client_id]['status']
    return stream_result, status


def clear_all_connection(config_name, server, client_id):
    try:
        global management_result
        thread = management_result[config_name][server][client_id]['thread']
        ssh = management_result[config_name][server][client_id]['ssh']
        if ssh.get_transport() is not None:
            ssh.close()

        if thread.isAlive():
            thread.join()

        del management_result[config_name][server][client_id]
    except KeyError:
        g.user.logger.error('Invalid data: {}, {}, {}'.format(config_name, server, client_id))


def update_status_global_stream_result(config_name, server, client_id, status=False):
    global management_result
    management_result[config_name][server][client_id]['status'] = status


def update_result_global_stream_result(config_name, server, client_id, tool, stream_result, status):
    """
    :param config_name:
    :param server:
    :param client_id:
    :param tool:
    :param stream_result:
    :param status:
    :return:
    """
    global management_result
    config = management_result.get(config_name, None)
    if config:
        server_data = config.get(server, None)
        if server_data:
            client_data = server_data.get(client_id, None)
            if client_data:
                client_data.update({
                    tool: stream_result,
                    "status": status
                })
            else:
                server_data.update({client_id: {
                    tool: stream_result,
                    "status": status
                }})
        else:
            config.update(
                {
                    server: {
                        client_id: {
                            tool: stream_result,
                            "status": status
                        }
                    }
                }
            )
    else:
        management_result.update({
            config_name: {
                server: {
                    client_id: {
                        tool: stream_result,
                        "status": status
                    }
                }
            }
        })


def get_bam_data(data):
    """
    :param data:
    :return:
    """
    server_str = ''
    try:
        server_id = data.get("oid", "")
        server = g.user.get_api().get_entity_by_id(server_id)
        server_name = server.get_name()
        server_ip = server.get_property('defaultInterfaceAddress')
        server_str = server_name + "(" + server_ip + ")"
        configuration = server.get_configuration()
    except Exception as ex:
        g.user.logger.error('Error when get data from BAM: {}'.format(ex))
        g.user.logger.error(traceback.format_exc())
    finally:
        return server_str, configuration.get_name(), configuration.get_id()


def get_loop_back_ip(ssh, view_id):
    """
    Search and get loop back IP by View
    :param ssh:
    :param view_id: id of view
    :return:
    """
    try:
        loop_back_ip = None
        _, stdout, _ = ssh.exec_command("sudo cat {} | awk '/match-clients.* key VIEW{};/'".format(NAMED_PATH, view_id))
        match_client_line = str(stdout.read().decode())
        g.user.logger.info('Get loop back IP from: {}'.format(match_client_line))
        list_out = [x.strip() for x in re.findall('(127.0.0.*?);', match_client_line)]
        if list_out:
            loop_back_ip = list_out[0]
        return loop_back_ip
    except socket.timeout:
        output = 'Failed to execute command get IP look back of view: {} : Timeout!'.format(view_id)
        g.user.logger.error(output)
        g.user.logger.error(traceback.format_exc())


def get_connection(hostname, username=DEFAULT_USER, timeout=DEFAULT_TIMEOUT, **kwargs):
    current_path = os.path.dirname(os.path.abspath(__file__))
    key_path = os.path.join(current_path, DEFAULT_SSH_KEY_PATH)
    try:
        key = RSAKey.from_private_key_file(key_path)
    except SSHException:
        g.user.logger.error(
            'Exception trying to connect to server: SSH key must be in PEM format : ssh-keygen -m PEM')
        g.user.logger.error(traceback.format_exc())
        raise Exception('Failed to connect to server!')
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    is_connected = ssh_open_connection(
        ssh, hostname, username, key, timeout, **kwargs)
    if not is_connected:
        raise Exception('Failed to connect to server!')
    return ssh


def get_config(config_file_path):
    try:
        if not os.path.exists(config_file_path):
            return None
        else:
            config = configparser.ConfigParser()
            config.read(config_file_path)
            return config
    except Exception:
        return None


def scp_file_from_server(ssh, source_path, destination_path):
    with SCPClient(ssh.get_transport()) as scp:
        scp.get(source_path, destination_path, recursive=True)
        scp.close()


def wait_for_scp_success(ssh, bk_file_name, timeout=30):
    local_bk_path = '{}/{}'.format(BamBackup.DEFAULT_LOCAL_BK_PATH, bk_file_name)
    start_time = datetime.datetime.now().timestamp() * 1000
    is_exist = True if os.path.exists(local_bk_path) else False
    while not is_exist:
        time.sleep(2)
        try:
            scp_file_from_server(ssh, '{}/{}'.format(BamBackup.BACKUP_DATA_DIR, bk_file_name), local_bk_path)
            is_exist = True if os.path.exists(local_bk_path) else False
        except Exception as ex:
            raise ex
        if ((datetime.datetime.now().timestamp() * 1000) - start_time) > timeout * 1000:
            return 'Timeout!'


def scan_upload_package(dir):
    """
    Return the result of one file. If more than files, return Execption
    """
    top_level_files = []
    for (dirpath, dirnames, filenames) in walk(dir):
        top_level_files = filenames
        # Only scan one level
        break

    if len(top_level_files) == 1:
        return top_level_files[0]
    elif len(top_level_files) == 0:
        raise Exception("Could not find package to install!")
    else:
        raise Exception("Could install since many package!")


def validate_configuration_and_server(config_name, server_ip):
    # Check the server ip is in BAM Ip. If it is not exist, we will continuous to check the list server Ip of
    # specific configuration.
    bam_ip = g.user.get_api_netloc()
    if bam_ip == server_ip:
        return {"server_name": get_bam_name(), "server_ip": server_ip, "config_name": config_name}

    # Check the given configuration is in BAM
    configuration = g.user.get_api().get_configuration(config_name)
    if not configuration:
        raise InvalidParam("Invalid configuration name {}".format(config_name))
    servers = configuration.get_servers()

    for server in servers:
        if server_ip == server.get_property('defaultInterfaceAddress'):
            return {"server_name": server.get_name(), "server_ip": server_ip, "config_name": config_name}

    raise InvalidParam("Server ip {} is not found in configuration {}".format(server_ip, config_name))


def prepare_cmd_tcpdump(data, supported_interfaces):
    """
    Validate input parameter and prepare the cmd from request
    E.g.

       {
          "configuration_name": "config"
          "servers_ip": "127.0.0.1",
          "interface": "gh",
          "port": 80,
          "packets_to_capture": 1,
          "max_capture_file": 1,
          "max_capture_time": 1,
          "optional": " "
        }
    """
    config_file = get_config(DEFAULT_TCPDUMP_CONFIG)
    upper_limit_packets_capture = config_file.getint("ANALYZE_TRAFFIC", "upper_limit_packets_capture", fallback="")
    upper_limit_capture_file_size = config_file.getint("ANALYZE_TRAFFIC", "upper_limit_capture_file_size", fallback="")
    upper_limit_capture_time = config_file.getint("ANALYZE_TRAFFIC", "upper_limit_capture_time", fallback="")

    keypair_cmd = {}
    # Check interface network
    interface = data.get("interface")
    if isinstance(interface, str) and interface:
        if interface in supported_interfaces:
            keypair_cmd['interface'] = f"-i {interface}"
        else:
            raise InvalidParam(f"Interface {interface} is not supported")
    else:
        raise InvalidParam("Interface must be string")

    # Check timeout (s)
    max_capture_time = data.get("max_capture_time")
    if isinstance(max_capture_time, int):
        if 0 < max_capture_time < upper_limit_capture_time:
            keypair_cmd['max_capture_time'] = f"timeout {max_capture_time}"
        else:
            raise InvalidParam(f"Max capture time must be greater than 0 and smaller than {max_capture_time}")
    else:
        raise InvalidParam("Max capture time must be integer")

    # Check port
    port = data.get("port")
    if port is None:
        keypair_cmd['port'] = ""
    else:
        if isinstance(port, int):
            if 0 <= port <= 65535:
                keypair_cmd['port'] = f"port {port}"
            else:
                raise InvalidParam("Port must be between 0 and 65535")
        else:
            raise InvalidParam("Port must be integer")

    # Check required parameter. Must be less than one field
    max_capture_file = data.get("max_capture_file")
    packets_to_capture = data.get("packets_to_capture")

    if not max_capture_file and not packets_to_capture:
        raise InvalidParam("Either max capture file size or packets capture is required")

    # Check number of packets to capture
    if isinstance(packets_to_capture, int):
        if 0 < packets_to_capture < 1000:
            keypair_cmd['packets_to_capture'] = f"-c {packets_to_capture}"
        else:
            raise InvalidParam(f"Number of packets to capture must be greater than 0 "
                               f"and smaller than {upper_limit_packets_capture}")
    else:
        keypair_cmd['packets_to_capture'] = ""

    # Check max file (MB)
    if isinstance(max_capture_file, int):
        if 0 < max_capture_file < 20:
            keypair_cmd['max_capture_file'] = f"ulimit -f {max_capture_file * 1024};"
        else:
            raise InvalidParam(f"Max capture file size must be greater than 0 and "
                               f"smaller than {upper_limit_capture_file_size}")
    else:
        keypair_cmd['max_capture_file'] = ""

    # Check optional
    optional = data.get("optional")
    if optional is None:
        keypair_cmd['optional'] = ""
    else:
        if isinstance(optional, str):
            # limit the len input string
            if len(optional) < 100:
                keypair_cmd['optional'] = f"{optional}"
            else:
                raise InvalidParam("Optional is too long")
        else:
            raise InvalidParam("Optional must be string")
    return keypair_cmd
