# Copyright 2021 BlueCat Networks. All rights reserved.
"""[CONSTANTS]
"""
import os

NAMED_PATH = '/jail/named/etc/named.conf'
DEFAULT_USER = 'bluecat'
DEFAULT_TIMEOUT = 30
DEFAULT_SSH_KEY_PATH = '../ssh/key'

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_BAM_BACKUP_CONFIG = current_path + '/../bam_backup/config.ini'
DEFAULT_TCPDUMP_CONFIG = os.path.join(parent_path, 'tcpdump/config.ini')
TCPDUMP_DOWNLOAD_DIR = 'download'
TCPDUMP_PARENT_DOWNLOAD_DIR = os.path.join(parent_path, 'tcpdump/analyze_traffic/')
TCP_CAPTURE_FILE_NAME = 'capture.cap'
REMOTE_REMOVE_TCPDUMP_SCRIPT_DIR = '/usr/local/bluecat'
REMOVE_TCPDUMP_SCRIPT = 'remove_tcpdump.sh'
ALLOWED_INTERFACE = ["any", "eth0", "eth1", "eth2", "eth3", "bond0"]


class Constants():
    @classmethod
    def all(cls):
        return [value for name, value in vars(cls).items() if name.isupper()]


class Method:
    GET = 'GET'
    POST = 'POST'
    DELETE = 'DELETE'


class BamBackup:
    BACKUP_DATA_DIR = '/data/backup'
    DEFAULT_BACKUP_NAME = 'default'
    DEFAULT_LOCAL_BK_PATH = current_path + '/../bam_backup/bk_data'
    BACKUP_STATUS_PATH = '/etc/bcn/backup_status.dat'
    DEFAULT_BACKUP_STATUS = ['success', 'failed', 'running', '----', 'local_failed', 'remote_failed']


class DpkgOption:
    # Get name package
    NAME_PACKAGE = 'tcpdump'

    #  Install the package
    INSTALL = '-i'

    # Purge an installed or already removed package. This
    # removes everything, including confides, and anything else
    # cleaned up from postrm
    PURGE = '-P'

    # List packages matching given pattern.
    LIST = '-l'

    # Display package status details..
    STATUS = '-s'

    # Check INSTALL
    CHECK_INSTALL_STATUS = "is not installed and no information is available"
