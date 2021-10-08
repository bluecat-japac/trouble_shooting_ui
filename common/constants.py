# Copyright 2021 BlueCat Networks. All rights reserved.

"""[CONSTANTS]
"""

NAMED_PATH = '/jail/named/etc/named.conf'


class Constants():
    @classmethod
    def all(cls):
        return [value for name, value in vars(cls).items() if name.isupper()]


class Method:
    GET = 'GET'
    POST = 'POST'
    DELETE = 'DELETE'
