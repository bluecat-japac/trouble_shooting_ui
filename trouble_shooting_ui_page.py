
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


# Various Flask framework items.
import os
import sys

from flask import render_template, jsonify, request
from bluecat import route, util
import config.default_config as config
from main_app import app
from bluecat_portal.workflows.trouble_shooting_ui.common import common


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


@route(app, '/trouble_shooting_ui/trouble_shooting_ui_endpoint', methods=["POST", "GET"])
@util.workflow_permission_required('trouble_shooting_ui_page')
@util.exception_catcher
def trouble_shooting_ui_trouble_shooting_ui_page():
    if request.method == 'POST':
        data = request.form
        server_str, configuration_name, configuration_id = common.get_bam_data(data)
        return render_template(
            'trouble_shooting_ui_page.html',
            text=util.get_text(module_path(), config.language), server_str=server_str,
            configuration_name=configuration_name, configuration_id=configuration_id)
    if request.method == 'GET':
        return render_template(
            'trouble_shooting_ui_page.html',
            text=util.get_text(module_path(), config.language))


@route(app, '/trouble_shooting_ui/onload', methods=['GET', 'POST'])
@util.workflow_permission_required('trouble_shooting_ui_page')
@util.exception_catcher
def onload():
    bam_ip = common.get_bam_ip()
    configurations = util.get_configurations()
    configuration_id = configurations[0][0]
    servers = common.get_server_list(configuration_id)
    return jsonify({'bam': bam_ip, 'configurations': configurations, 'server': servers})


@route(app, '/trouble_shooting_ui/server', methods=['POST'])
@util.workflow_permission_required('trouble_shooting_ui_page')
@util.exception_catcher
def update_server_list():
    if request.method == 'POST':
        data = request.get_json()
        configuration_id = data['config']
        servers = common.get_server_list(configuration_id)
        return jsonify({'server': servers})


@route(app, '/trouble_shooting_ui/submit', methods=['POST'])
@util.workflow_permission_required('trouble_shooting_ui_page')
@util.exception_catcher
def submit():
    if request.method == 'POST':
        data = request.get_json()
        server = data['server']
        tool = data['tool']
        param = data['parameters']
        server_ip = server.split('(')[1][:-1]
        output = common.prepare_ssh_command(server_ip, tool, param)
        return jsonify({'result': output})
