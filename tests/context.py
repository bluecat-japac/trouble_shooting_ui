# Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import sys
from unittest import mock


def decorator_fake(*args):
    def func_wrapper(func):
        # pylint: disable=missing-docstring
        return func

    return func_wrapper


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.modules["bluecat"] = mock.Mock()
sys.modules["bluecat.api_exception"] = mock.Mock()
sys.modules["config"] = mock.Mock()
sys.modules["config.default_config"] = mock.Mock()
main_app = mock.MagicMock()
namespace_obj = mock.MagicMock()
namespace_obj.route = decorator_fake
main_app.api.namespace.return_value = namespace_obj


def dummy_decorator(*args, **kwargs):
    '''
        A dummy decorator.
    '''

    def wrapper(cls):
        return cls

    return wrapper


dummy_route = mock.MagicMock()
dummy_route.route = dummy_decorator
dummy_route.expect = dummy_decorator

main_app_mock = mock.MagicMock()
main_app_mock.api.expect = dummy_decorator
main_app_mock.api.namespace.return_value = dummy_route
main_app_mock.app.route = dummy_decorator
sys.modules["main_app"] = main_app_mock
sys.modules["bluecat_portal.workflows.trouble_shooting_ui.common"] = mock.Mock()
sys.modules["bluecat_portal.config"] = mock.Mock()
sys.modules["bluecat_portal"] = mock.Mock()
sys.modules["scp"] = mock.Mock()
sys.modules["flask_restplus"] = mock.Mock()

import flask_restplus


class FakeClass:
    def __init__(self, *args, **kwargs):
        pass


flask_restplus.Resource = FakeClass


def decorator_fake(*args):
    def func_wrapper(func):
        # pylint: disable=missing-docstring
        return func

    return func_wrapper


def route_fake(app, path, methods=None):
    def func_wrapper(func):
        # pylint: disable=missing-docstring
        return func

    return func_wrapper


def workflow_permission_required_fake(path):
    def func_wrapper(func):
        # pylint: disable=missing-docstring
        return func

    return func_wrapper


mock.patch('bluecat.route', route_fake).start()
mock.patch('bluecat.util.workflow_permission_required', workflow_permission_required_fake).start()
mock.patch('bluecat.util.exception_catcher', lambda x: x).start()
mock.patch('bluecat.util.ui_secure_endpoint', lambda x: x).start()
mock.patch('bluecat.util.no_cache', lambda x: x).start()
