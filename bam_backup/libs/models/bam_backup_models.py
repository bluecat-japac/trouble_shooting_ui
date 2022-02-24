# Copyright 2021 BlueCat Networks. All rights reserved.

from flask_restplus import fields
from main_app import api

delete_bam_backup_model = api.model(
    'Delete Bam Backup File',
    {
        'backup_files_name': fields.List(fields.String, required=False)
    }
)
