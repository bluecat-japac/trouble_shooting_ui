# Copyright 2021 BlueCat Networks. All rights reserved.

from bluecat.api_exception import safe_str


class UserException(Exception):
    def __init__(self, msg):
        self.msg = msg or "User input incorrect"

    def __str__(self):
        return safe_str(self.msg)


class InvalidParam(UserException):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return safe_str(self.message)
