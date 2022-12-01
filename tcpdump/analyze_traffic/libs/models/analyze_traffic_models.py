# Copyright 2021 BlueCat Networks. All rights reserved.

from flask_restplus import fields
from main_app import api

started_analyze_traffic_model = api.model(
    "started_analyze_traffic_model", {
        "configuration_name": fields.String(description='Configuration', example='configuration'),
        "server_ip": fields.String(description='Ip of host', example='127.0.0.1'),
        "interface": fields.String(description='Interface network of server', example='eth0'),
        "port": fields.Integer(description='Port server', example=80),
        "packets_to_capture": fields.Integer(description='Number of captured packets', example=100),
        "max_capture_file": fields.Integer(description='Max output file', example=1),
        "max_capture_time": fields.Integer(description='Max capture time', example=10),
        "optional": fields.String(description='Extra optional', example=' '),
    }
)

stopped_analyze_traffic_model = api.model(
    "stopped_analyze_traffic_model", {
        "configuration_name": fields.String(description='Configuration', example='configuration'),
        "server_ip": fields.String(description='Ip of host', example='127.0.0.1'),
    }
)
