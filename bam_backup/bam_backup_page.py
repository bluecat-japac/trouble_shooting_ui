# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.
import os
import sys
import traceback
from flask_restplus import Resource
from flask import render_template, g, make_response, jsonify, send_file

from bluecat import route, util
import config.default_config as config
from main_app import app, api
from ..common.exceptions import UserException
from ..common.backup_file import RemoteBAMBackupClient
from ..common.common import get_config
from ..common.constants import DEFAULT_BAM_BACKUP_CONFIG
from .libs.models import bam_backup_models
from .libs.parsers import bam_backup_parsers


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


@route(app, '/bam_backup/bam_backup_endpoint')
@util.workflow_permission_required('bam_backup_page')
@util.exception_catcher
@util.ui_secure_endpoint
@util.no_cache
def bam_backup_bam_backup_page():
    config_file = get_config(DEFAULT_BAM_BACKUP_CONFIG)
    return render_template(
        'bam_backup_page.html',
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
        max_count_file=config_file.get("BAM_BACKUP", "max_count_file", fallback="")
    )


bam_backup_ns = api.namespace(
    'bam_backup',
    path='/bam_backup',
    description='Bam Backup by Gateway',
)


@bam_backup_ns.route('/backup_file')
class BAMBackupFiles(Resource):
    @util.workflow_permission_required('bam_backup_page')
    @util.exception_catcher
    @util.ui_secure_endpoint
    @util.no_cache
    def get(self):
        """ Get backup file from BAM"""
        try:
            remote_client = RemoteBAMBackupClient(g.user.get_api_netloc())
            result = remote_client.read_backup_file()
            remote_client.disconnect()
            return jsonify(result)
        except UserException as user_ex:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(user_ex)), 400)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)

    @util.workflow_permission_required('bam_backup_page')
    @util.exception_catcher
    @util.ui_secure_endpoint
    @util.no_cache
    @api.expect(bam_backup_models.delete_bam_backup_model, validate=True)
    def delete(self):
        """ Delete backup file from BAM"""
        try:
            data = bam_backup_parsers.delete_bam_backup_parser.parse_args()
            backup_files_name = data.get('backup_files_name')
            remote_client = RemoteBAMBackupClient(g.user.get_api_netloc())
            result = remote_client.delete_backup_file(backup_files_name)
            return jsonify(result)
        except UserException as user_ex:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(user_ex)), 400)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


@bam_backup_ns.route('/backup_file/<string:backup_file_name>')
class BAMBackup(Resource):
    @util.workflow_permission_required('bam_backup_page')
    @util.exception_catcher
    @util.ui_secure_endpoint
    @util.no_cache
    def get(self, backup_file_name):
        """ Support get backup file from BAM by backup name"""
        try:
            hostname = g.user.get_api_netloc()
            remote_client = RemoteBAMBackupClient(hostname)
            bk_list = remote_client.read_backup_file()
            filter_bk = [bk for bk in bk_list if bk.get('name') == backup_file_name]
            result = filter_bk[0] if filter_bk else {}
            return jsonify(result)
        except UserException as user_ex:
            remote_client = None
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(user_ex)), 400)
        except Exception as e:
            remote_client = None
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)
        finally:
            if remote_client:
                remote_client.disconnect()


@bam_backup_ns.route('/local_backup_path/<string:backup_file_name>')
class DownloadBAMBackup(Resource):
    @util.workflow_permission_required('bam_backup_page')
    @util.exception_catcher
    @util.ui_secure_endpoint
    @util.no_cache
    def get(self, backup_file_name):
        """ Support download backup file from BAM and return local path"""
        try:
            hostname = g.user.get_api_netloc()
            remote_client = RemoteBAMBackupClient(hostname)
            local_bk_path = remote_client.download_and_get_local_backup_file(backup_file_name)
            return send_file(local_bk_path, as_attachment=True), 200
        except UserException as user_ex:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(user_ex)), 400)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


@bam_backup_ns.route('/run')
class RunBAMBackup(Resource):
    @util.workflow_permission_required('bam_backup_page')
    @util.exception_catcher
    @util.ui_secure_endpoint
    @util.no_cache
    def post(self):
        """ Run default backup file"""
        try:
            remote_client = RemoteBAMBackupClient(g.user.get_api_netloc())
            result = remote_client.run_backup_file()
            return jsonify(result)
        except UserException as user_ex:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(user_ex)), 400)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


@bam_backup_ns.route('/check_status')
class CheckBackupStatus(Resource):
    @util.workflow_permission_required('bam_backup_page')
    @util.exception_catcher
    @util.ui_secure_endpoint
    @util.no_cache
    def get(self):
        """ Check status after run backup file"""
        try:
            remote_client = RemoteBAMBackupClient(g.user.get_api_netloc())
            result = remote_client.check_backup_status()
            return jsonify(result)
        except UserException as user_ex:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(user_ex)), 400)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)
