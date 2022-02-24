# Copyright 2021 BlueCat Networks. All rights reserved.

from flask_restplus import fields
from main_app import api

server_model = api.model(
    "entity_model", {
        "server_ip": fields.String(description='Ip of host', example='127.0.0.1'),
    }
)

installation_tcpdump_model = api.model(
    "installation_model", {
        "configuration_name": fields.String(description='Configuration name', example='configuration'),
        "server_ips": fields.List(fields.String(description='Ip of host', example='127.0.0.1'))
    })