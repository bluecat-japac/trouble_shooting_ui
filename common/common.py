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
import socket
import traceback
import bluecat_portal.config as user_config

from threading import Thread
from flask import g
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.ssh_exception import AuthenticationException, SSHException
from bluecat.api_exception import PortalException

from ..common.constants import NAMED_PATH

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
            for bam in user_config.api_url:
                if bam_ip == re.search('//(.+?)/', bam[1]).group(1):
                    return bam[0]

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
        'Connecting to BDDS {} ...'.format(hostname))
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


def prepare_ssh_command(config_name, server, hostname, client_id, tool, param, view_id=0, username='bluecat', timeout=30,
                        **kwargs):
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
    current_path = os.path.dirname(os.path.abspath(__file__))
    key_path = os.path.join(current_path, '../ssh/key')
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
