# Copyright 2021 BlueCat Networks. All rights reserved.
from flask_restplus import reqparse

delete_bam_backup_parser = reqparse.RequestParser()
delete_bam_backup_parser.add_argument(
    'backup_files_name',
    location="json",
    type=list,
    required=False,
    help='The backup files name',
)
