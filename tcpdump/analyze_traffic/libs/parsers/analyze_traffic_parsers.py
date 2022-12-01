# Copyright 2021 BlueCat Networks. All rights reserved.
from flask_restplus import reqparse

parser = reqparse.RequestParser()
parser.add_argument('configuration_name', type=str, help='Configuration Name', required=False, default='')
parser.add_argument('server_ip', type=str, help='Server IP', required=True)