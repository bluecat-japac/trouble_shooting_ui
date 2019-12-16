
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
from flask import g
from bluecat import entity
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.ssh_exception import AuthenticationException, SSHException
import bluecat_portal.config as user_config
from bluecat.api_exception import PortalException


def get_bam_ip():
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

    raise PortalException('No BAM configured in Config.py or Environment variable BAM_IP')


def get_server_ip(server):
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
        g.user.logger.error("Exception trying to connect to server: \nSSH key hasn't been copy to server yet: ssh-copy-id -i <key> bluecat@<server>")
        g.user.logger.error(traceback.format_exc())
        return False
    except AttributeError:
        g.user.logger.error('Exception trying to connect to server: Problem with key file!')
        g.user.logger.error(traceback.format_exc())
        return False
    except Exception as e:
        g.user.logger.error(
            'Exception trying to connect to server {} : {}'.format(hostname, e))
        g.user.logger.error(traceback.format_exc())
        return False


def exec_command(ssh, cmd, timeout):
    """
    :param ssh:
    :param cmd:
    :param timeout:
    :return:
    """
    output = ''
    try:
        _, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        error = stderr.read().decode('utf-8')
        if error:
            g.user.logger.error('Error when execute command: {} : {}'.format(cmd, error))
            g.user.logger.error(traceback.format_exc())
            output = error
        else:
            output = stdout.read().decode('utf-8')
            g.user.logger.info(output)
    except socket.timeout:
        output = 'Failed to execute command: {} : Timeout!'.format(cmd)
        g.user.logger.error(output)
        g.user.logger.error(traceback.format_exc())
    finally:
        return output


def prepare_ssh_command(hostname, tool, param, username='bluecat', timeout=30, **kwargs):
    current_path = os.path.dirname(os.path.abspath(__file__))
    key_path = os.path.join(current_path, '../ssh/key')
    try:
        key = RSAKey.from_private_key_file(key_path)
    except SSHException:
        g.user.logger.error('Exception trying to connect to server: SSH key must be in PEM format : ssh-keygen -m PEM')
        g.user.logger.error(traceback.format_exc())
        return 'Failed to connect to server!'
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    is_connected = ssh_open_connection(ssh, hostname, username, key, timeout, **kwargs)
    if not is_connected:
        return 'Failed to connect to server!'
    tool_cmd = {
        "ping": "ping -c 4 {}",
        "dig": "dig {}",
        "traceroute": "traceroute {}"
    }
    cmd = tool_cmd.get(tool).format(param)

    output = exec_command(ssh, cmd, timeout=timeout)
    return output


def get_bam_data(data):
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