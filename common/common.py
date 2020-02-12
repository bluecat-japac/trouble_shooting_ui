# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
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


import os
import socket
import traceback
from threading import Thread
from flask import g
from bluecat import entity
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.ssh_exception import AuthenticationException, SSHException
import bluecat_portal.config as user_config
from bluecat.api_exception import PortalException

stream_result = ""
management_result = {}


def get_bam_ip():
    """
    :return:
    """
    if 'BAM_IP' in os.environ:
        if 'http' in os.environ['BAM_IP']:
            bam_ip = os.environ['BAM_IP'].split('/')[2]
        else:
            bam_ip = os.environ['BAM_IP'].split('/')[0]
        return bam_ip

    if hasattr(user_config, 'api_url'):
        if isinstance(user_config.api_url, str):
            bam_ip = user_config.api_url.split('/')[2]
        else:
            bam_ip = user_config.api_url[0][0]
        return bam_ip

    raise PortalException(
        'No BAM configured in Config.py or Environment variable BAM_IP')


def get_server_ip(server):
    """
    :param server:
    :return:
    """
    props = server['properties'].split('|')
    for prop in props:
        if prop.startswith('defaultInterfaceAddress'):
            ip = prop.split('=')[1]
            return ip


def get_server_list(configuration_id):
    servers = g.user.get_api()._api_client.service.getEntities(
        configuration_id, entity.Entity.Server, 0, 1000)
    server_list = []
    for server in servers:
        ip = get_server_ip(server)
        server_list.append([server['name'], ip])
    return server_list


def ssh_open_connection(ssh, hostname, username, key, timeout, **kwargs):
    """
    :param ssh:
    :param hostname:
    :param username:
    :param password:
    :param timeout:
    :param kwargs:
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
    :param timeout:
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


def prepare_ssh_command(config_name, server, hostname, client_id, tool, param, username='bluecat', timeout=30,
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
    :param kwargs:
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
    tool_cmd = {
        "ping": "ping -c 10 {}",
        "dig": "dig {}",
        "traceroute": "traceroute {}"
    }

    if ":" in param:
        tool_cmd = {
            "ping": "ping6 -c 10 {}",
            "dig": "dig {}",
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
    configuration_name = ''
    configuration_id = ''
    try:
        server_id = data.get("oid", "")
        server = g.user.get_api()._api_client.service.getEntityById(server_id)
        server_name = server.get("name", "")
        server_ip = get_server_ip(server)
        server_str = server_name + "(" + server_ip + ")"
        configuration = g.user.get_api()._api_client.service.getParent(server_id)
        configuration_name = configuration.get("name", "")
        configuration_id = configuration.get("id", "")
    except Exception as ex:
        g.user.logger.error('Error when get data from BAM: {}'.format(ex))
        g.user.logger.error(traceback.format_exc())
    finally:
        return server_str, configuration_name, configuration_id
