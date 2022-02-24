# Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.
import os
import sys
import traceback
from flask import render_template, g, make_response, jsonify, request
from flask_restplus import Resource
from bluecat import route, util
import config.default_config as config
from main_app import app, api
from ...common.exceptions import UserException, InvalidParam
from ...common.tcpdump import TcpDump, InstallationResponse
from ...common.common import get_bam_name, validate_configuration_and_server
from .libs.models import installation_models


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


installation_tcpdump_ns = api.namespace(
    'installation',
    path='/installation',
    description='Installation TcpDump by Gateway',
)


@route(app, '/installation/installation_endpoint')
@util.workflow_permission_required('installation_page')
@util.exception_catcher
@util.ui_secure_endpoint
def installation_installation_page():
    return render_template(
        'installation_page.html',
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
        bam_name=get_bam_name(),
        bam_ip=g.user.get_api_netloc()
    )


@installation_tcpdump_ns.route('/package/uninstall')
class UninstallTcpDump(Resource):
    @util.workflow_permission_required('installation_page')
    @util.exception_catcher
    @util.ui_secure_endpoint
    @util.no_cache
    @installation_tcpdump_ns.expect(installation_models.installation_tcpdump_model)
    def post(self):
        """ Uninstall the tcpdump"""
        try:
            message = []
            hosts = []
            data = request.get_json()
            configuration_name = data.get("configuration_name")
            server_ips = data.get("server_ips")
            for server_ip in server_ips:
                host = validate_configuration_and_server(configuration_name, server_ip)
                hosts.append(host)

            for host in hosts:
                try:
                    tcpdump = None
                    tcpdump = TcpDump(host=host)
                    response = tcpdump.uninstall_package()
                    tcpdump.disconnect()
                except Exception as e:
                    if tcpdump:
                        tcpdump.disconnect()
                    g.user.logger.error(traceback.format_exc())
                    response = InstallationResponse(host=host,
                                                    status=False,
                                                    message=str(e))
                message.append(response.__dict__)
            g.user.logger.debug(f"{request.url} {request.method}: Return state server-{message}")
            return jsonify(message), 200
        except InvalidParam as ex:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(ex)), 400)

        except Exception as ex:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(ex)), 500)


@installation_tcpdump_ns.route('/configurations')
class ConfigurationCollection(Resource):
    @util.rest_workflow_permission_required('installation_page')
    @util.exception_catcher
    @util.ui_secure_endpoint
    @util.no_cache
    def get(self):
        """ Get all known configuration(s). """
        try:
            configurations = g.user.get_api().get_configurations()
            result = [config_entity.to_json() for config_entity in configurations]
            g.user.logger.debug(f"{request.url} {request.method}: Configuration list-{result}")
            return jsonify(result), 200
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


@installation_tcpdump_ns.route('/configurations/<string:configuration>')
class Configuration(Resource):
    @util.rest_workflow_permission_required('installation_page')
    @util.exception_catcher
    @util.ui_secure_endpoint
    @util.no_cache
    def get(self, configuration):
        """ Get configuration with specified name. """
        try:
            configuration = g.user.get_api().get_configuration(configuration)
            result = configuration.to_json()
            g.user.logger.debug(f"{request.url} {request.method}: Configuration-{result}")
            return jsonify(result), 200
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


@installation_tcpdump_ns.route('/configurations/<string:configuration>/servers')
class ServersList(Resource):
    @util.workflow_permission_required('installation_page')
    @util.exception_catcher
    @util.ui_secure_endpoint
    @util.no_cache
    def get(self, configuration):
        """ Get all known Server(s) with specified Configuration name. """
        try:
            configuration = g.user.get_api().get_configuration(configuration)
            servers = configuration.get_servers()
            servers = [server.to_json() for server in servers]
            g.user.logger.debug(f"{request.url} {request.method}: Server list-{servers}")
            return jsonify(servers), 200
        except UserException as ex:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(ex)), 400)
        except Exception as ex:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(ex)), 500)
