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


# Various Flask framework items.
import os
import sys
import traceback
from flask import render_template, jsonify, request, g
from bluecat import route, util
import config.default_config as config
from main_app import app


def module_path():
    sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


from .common import common
from .common.constants import Method
from .common.exceptions import UserException


@route(app, '/trouble_shooting_ui/trouble_shooting_ui_endpoint', methods=["POST", "GET"])
@util.workflow_permission_required('trouble_shooting_ui_page')
@util.exception_catcher
def trouble_shooting_ui_trouble_shooting_ui_page():
    if request.method == Method.POST:
        data = request.form
        server_str, configuration_name, configuration_id = common.get_bam_data(data)
        return render_template(
            'trouble_shooting_ui_page.html',
            text=util.get_text(module_path(), config.language), server_str=server_str,
            configuration_name=configuration_name, configuration_id=configuration_id)
    if request.method == Method.GET:
        return render_template(
            'trouble_shooting_ui_page.html',
            text=util.get_text(module_path(), config.language))


@route(app, '/trouble_shooting_ui/onload', methods=['GET', 'POST'])
@util.workflow_permission_required('trouble_shooting_ui_page')
@util.exception_catcher
def onload():
    try:
        bam_name = common.get_bam_name()
        configurations = g.user.get_api().get_configurations()
        views = []
        servers = []
        configurations = [config_entity.to_json() for config_entity in configurations]
        if configurations:
            configuration = g.user.get_api().get_entity_by_id(configurations[0].get('id', 0))
            views = configuration.get_views()
            views = [view.to_json() for view in views]
            servers = configuration.get_servers()
            servers = [server.to_json() for server in servers]
        return jsonify({'bam': bam_name, 'configurations': configurations, 'servers': servers, 'views': views})
    except Exception as ex:
        g.user.logger.error(str(ex))
        g.user.logger.error(traceback.format_exc())
        return jsonify(str(ex)), 500


@route(app, '/trouble_shooting_ui/views', methods=['GET'])
@util.workflow_permission_required('trouble_shooting_ui_page')
@util.exception_catcher
def get_views():
    try:
        config_id = request.args.get('config_id')
        configuration = g.user.get_api().get_entity_by_id(config_id)
        views = configuration.get_views()
        views = [view.to_json() for view in views]
        return jsonify(views)
    except Exception as ex:
        g.user.logger.error(str(ex))
        g.user.logger.error(traceback.format_exc())
        return jsonify(str(ex)), 500


@route(app, '/trouble_shooting_ui/server', methods=['POST'])
@util.workflow_permission_required('trouble_shooting_ui_page')
@util.exception_catcher
def update_server_list():
    try:
        data = request.get_json()
        configuration_id = data['config_id']
        configuration = g.user.get_api().get_entity_by_id(configuration_id)
        servers = configuration.get_servers()
        servers = [server.to_json() for server in servers]
        return jsonify(servers)
    except UserException as ex:
        g.user.logger.error(str(ex))
        g.user.logger.error(traceback.format_exc())
        return jsonify(str(ex)), 400
    except Exception as ex:
        g.user.logger.error(str(ex))
        g.user.logger.error(traceback.format_exc())
        return jsonify(str(ex)), 500


@route(app, '/trouble_shooting_ui/submit', methods=['POST'])
@util.workflow_permission_required('trouble_shooting_ui_page')
@util.exception_catcher
def submit():
    try:
        data = request.get_json()
        config_name = data['config-name']
        view_id = data['view-id']
        server = data["server"]
        server_ip = server.split('(')[1][:-1]
        client_id = data['client-id']
        param = data['param']
        tool = data["tool"]
        common.prepare_ssh_command(config_name, server, server_ip, client_id, tool, param, view_id)
        return jsonify({'result': "Connecting..."})
    except Exception as ex:
        g.user.logger.error('Exception while run execute command:\n{}'.format(ex))
        g.user.logger.error(traceback.format_exc())
        return jsonify(ex), 500


@route(app, '/trouble_shooting_ui/stream_result', methods=['GET', 'DELETE'])
@util.workflow_permission_required('trouble_shooting_ui_page')
@util.exception_catcher
def stream_result():
    try:
        if request.method == Method.GET:
            config_name = request.args.get('configName')
            server = request.args.get("serverName")
            client_id = request.args.get('clientID')
            tool = request.args.get("Tool")
            stream, status = common.get_stream_result(config_name, server, client_id, tool)
            result = {tool: stream, "status": status}
            response = result
        elif request.method == Method.DELETE:
            config_name = request.args.get('configName')
            server = request.args.get("serverName")
            client_id = request.args.get('clientID')
            common.clear_all_connection(config_name, server, client_id)
            response = {"status": "Success"}
    except Exception as ex:
        g.user.logger.error(ex)
        g.user.logger.error(traceback.format_exc())
        response = {"status": True}
    finally:
        return jsonify(response)
