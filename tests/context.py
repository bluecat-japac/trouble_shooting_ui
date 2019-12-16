
# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
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

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.modules["bluecat"] = mock.Mock()
sys.modules["bluecat.api_exception"] = mock.Mock()
sys.modules["config"] = mock.Mock()
sys.modules["config.default_config"] = mock.Mock()
sys.modules["main_app"] = mock.Mock()
sys.modules["bluecat_portal.workflows.trouble_shooting_ui.common"] = mock.Mock()
sys.modules["bluecat_portal.config"] = mock.Mock()
sys.modules["bluecat_portal"] = mock.Mock()


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
