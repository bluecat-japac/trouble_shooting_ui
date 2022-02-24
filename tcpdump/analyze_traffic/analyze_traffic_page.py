# Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.
import os
import sys
import traceback

from flask import render_template, g, make_response, jsonify, request, send_file
from flask_restplus import Resource
from bluecat import route, util
import config.default_config as config
from main_app import app, api
from ...common.exceptions import UserException, InvalidParam
from ...common.tcpdump import TcpDump
from ...common.common import get_bam_name, prepare_cmd_tcpdump, validate_configuration_and_server
from ...common.constants import TCP_CAPTURE_FILE_NAME
from .libs.models import analyze_traffic_models
from .libs.parsers import analyze_traffic_parsers


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


analyze_traffic_ns = api.namespace(
    'analyze_traffic',
    path='/analyze_traffic',
    description='Analyze Traffic TcpDump by Gateway',
)


@route(app, '/analyze_traffic/analyze_traffic_endpoint')
@util.workflow_permission_required('analyze_traffic_page')
@util.exception_catcher
@util.ui_secure_endpoint
def analysis_analysis_page():
    return render_template(
        'analyze_traffic_page.html',
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
        bam_name=get_bam_name(),
        bam_ip=g.user.get_api_netloc()
    )


@analyze_traffic_ns.route('/start')
class StartedTcpDump(Resource):
    @util.workflow_permission_required('analyze_traffic_page')
    @util.exception_catcher
    @util.ui_secure_endpoint
    @util.no_cache
    @analyze_traffic_ns.expect(analyze_traffic_models.started_analyze_traffic_model)
    def post(self):
        """ Start tcpdump"""
        try:
            tcpdump = None
            data = request.get_json()
            host = validate_configuration_and_server(data.get('configuration_name'), data.get('server_ip'))
            # Retrieve interfaces network from host
            tcpdump = TcpDump(host=host)
            interfaces = tcpdump.get_interface_network()
            tcpdump.disconnect()

            # Prepare the commandline to run Tcpdump
            keypair_cmd = prepare_cmd_tcpdump(data, interfaces)
            tcpdump = TcpDump(host=host)
            response = tcpdump.start(keypair_cmd)
            return jsonify(response), 201

        except InvalidParam as ex:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(ex)), 400)
        except Exception as ex:
            if tcpdump:
                tcpdump.disconnect()
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(ex)), 500)


@analyze_traffic_ns.route('/stop')
class StoppedTcpDump(Resource):
    @util.workflow_permission_required('analyze_traffic_page')
    @util.exception_catcher
    @util.ui_secure_endpoint
    @util.no_cache
    @analyze_traffic_ns.expect(analyze_traffic_models.stopped_analyze_traffic_model)
    def post(self):
        """ Stop tcpdump"""
        try:
            tcpdump = None
            data = request.get_json()
            host = validate_configuration_and_server(data.get('configuration_name'), data.get('server_ip'))
            tcpdump = TcpDump(host=host)
            response = tcpdump.stop()
            tcpdump.disconnect()
            return jsonify(response), 201

        except InvalidParam as ex:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(ex)), 400)
        except Exception as ex:
            if tcpdump:
                tcpdump.disconnect()
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(ex)), 500)


@analyze_traffic_ns.route('/status')
class TcpDumpStatus(Resource):
    @util.workflow_permission_required('analyze_traffic_page')
    @util.exception_catcher
    @util.ui_secure_endpoint
    @util.no_cache
    @analyze_traffic_ns.expect(analyze_traffic_parsers.parser)
    def get(self):
        """ Get tcpdump status"""
        try:
            tcpdump = None
            server_ip = request.args.get('server_ip')
            config_name = request.args.get('configuration_name')
            host = validate_configuration_and_server(config_name, server_ip)
            tcpdump = TcpDump(host=host)
            response = tcpdump.get_status()
            tcpdump.disconnect()
            return jsonify(response), 200

        except InvalidParam as ex:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(ex)), 400)
        except Exception as e:
            if tcpdump:
                tcpdump.disconnect()
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


@analyze_traffic_ns.route('/configurations')
class ConfigurationCollection(Resource):
    @util.rest_workflow_permission_required('analyze_traffic_page')
    @util.exception_catcher
    @util.ui_secure_endpoint
    @util.no_cache
    def get(self):
        """ Get all known configuration(s). """
        try:
            configurations = g.user.get_api().get_configurations()
            result = [config_entity.to_json() for config_entity in configurations]
            return jsonify(result), 200
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


@analyze_traffic_ns.route('/configurations/<string:configuration>')
class Configuration(Resource):
    @util.rest_workflow_permission_required('analyze_traffic_page')
    @util.exception_catcher
    @util.ui_secure_endpoint
    @util.no_cache
    def get(self, configuration):
        """ Get configuration with specified name. """
        try:
            configuration = g.user.get_api().get_configuration(configuration)
            result = configuration.to_json()
            return jsonify(result), 200
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


@analyze_traffic_ns.route('/configurations/<string:configuration>/servers')
class ServersList(Resource):
    @util.workflow_permission_required('analyze_traffic_page')
    @util.exception_catcher
    @util.ui_secure_endpoint
    @util.no_cache
    def get(self, configuration):
        """ Get all known Server(s) with specified Configuration name. """
        try:
            configuration = g.user.get_api().get_configuration(configuration)
            servers = configuration.get_servers()
            servers = [server.to_json() for server in servers]
            return jsonify(servers), 200
        except UserException as ex:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(ex)), 400)
        except Exception as ex:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(ex)), 500)


@analyze_traffic_ns.route('/download')
class Download(Resource):
    @util.workflow_permission_required('analyze_traffic_page')
    @util.exception_catcher
    @util.ui_secure_endpoint
    @util.no_cache
    @analyze_traffic_ns.expect(analyze_traffic_parsers.parser)
    def get(self):
        """ Support download capture.cap file from BAM and return local path"""
        try:
            tcpdump = None
            server_ip = request.args.get('server_ip')
            config_name = request.args.get('configuration_name')
            host = validate_configuration_and_server(config_name, server_ip)
            tcpdump = TcpDump(host=host)
            local_capture_path = tcpdump.download_and_get_local_capture_file()
            tcpdump.disconnect()
            return send_file(local_capture_path,
                             as_attachment=True,
                             attachment_filename=TCP_CAPTURE_FILE_NAME), 200

        except InvalidParam as ex:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(ex)), 400)
        except Exception as e:
            if tcpdump:
                tcpdump.disconnect()
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


@analyze_traffic_ns.route('/interfaces')
class InterfacesList(Resource):
    @util.workflow_permission_required('analyze_traffic_page')
    @util.exception_catcher
    @util.ui_secure_endpoint
    @util.no_cache
    @analyze_traffic_ns.expect(analyze_traffic_parsers.parser)
    def get(self):
        """ Get all Interface(s) of server with specified server ip. """
        try:
            tcpdump = None
            server_ip = request.args.get('server_ip')
            config_name = request.args.get('configuration_name')
            host = validate_configuration_and_server(config_name, server_ip)
            tcpdump = TcpDump(host=host)
            interface_list = tcpdump.get_interface_network()
            tcpdump.disconnect()
            return jsonify(interface_list), 200

        except InvalidParam as ex:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(ex)), 400)
        except Exception as ex:
            if tcpdump:
                tcpdump.disconnect()
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(ex)), 500)