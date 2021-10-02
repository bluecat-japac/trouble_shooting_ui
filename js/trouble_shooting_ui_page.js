// Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// JavaScript for your page goes in here.

$(document).ready(function () {
    window.submitted = false;
    $('#txt-parameters').attr("placeholder", "<IP address> [<option>]");
    $('#submit').prop('disabled', true);
    $('#sl-config').prop('disabled', true);
    $('#sl-server').prop('disabled', true);
    $('#sl-view').prop('disabled', true);
    $('#txt-parameters').val('');
    $('#sl-tool').val('ping');
    $('#result').val('');
    onLoad();
    $('#txt-parameters').keypress(function (e) {
        var key = e.which;
        if (key == 13) {
            $('#submit').click();
        }
    });

})

var placeholderText = {
    "dig": "@<server IP address> <name query>",
    "ping": "<IP address> [<option>]",
    "traceroute": "<IP address>"
};

function unlockGUI(boolean) {
    let ELEMENT = ['sl-configuration', 'sl-view', 'sl-server', 'sl-server', 'sl-tool', 'txt-parameters', 'submit'];
    if (boolean) {
        for (const el of ELEMENT) {
            $(`#${el}`).prop('disabled', false);
        }
    } else {
        for (const el of ELEMENT) {
            $(`#${el}`).prop('disabled', true);
        }
    }
}

function setPlaceholder() {
    $('#txt-parameters').attr("placeholder", placeholderText[$("#sl-tool option:selected").text()]);
    $('#txt-parameters').val('');
    $('#submit').prop('disabled', true);
    $('#result').val('');
}

function onLoad() {
    $.ajax({
        url: '/trouble_shooting_ui/onload',
        type: 'get',
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
            $('#bam').val(data['bam']);
            for (const elName of ['configurations', 'views', 'servers']) {
                var elHTML = [];

                if (elName == 'views') {
                    elHTML.push(`<option value='0'>Not Selected</option>`)
                }
                for (var i = 0; i < data[elName].length; i++) {
                    var value = data[elName][i].id;
                    var txt = data[elName][i].name;
                    if (elName == 'servers') {
                        var serverIP = getProperty(data[elName][i], 'defaultInterfaceAddress');
                        value = data[elName][i].name + ` (${serverIP})`;
                        txt = value;
                    }
                    elHTML.push(`<option value=${value}>${txt}</option>`)
                }
                $(`#sl-${elName.substring(0, elName.length - 1)}`).html(elHTML);
                if (data[elName].length > 0) {
                    $(`#sl-${elName.substring(0, elName.length - 1)}`).prop('disabled', false);
                }
            }
        },
    });
}

function updateViewAndServerList(isCheck = false) {
    $('#sl-view').html('');
    $('#sl-server').prop('disabled', true);
    $('#sl-view').prop('disabled', true);
    if (!isCheck) {
        var configID = $('#sl-configuration').val();
    } else {
        var configID = configuration_id;
    }
    getViews(configID);
    getServers(configID);
}


function checkSubmit() {
    var server = $('#sl-server').text();
    var parameters = $('#txt-parameters').val();
    if (server && parameters) {
        $('#submit').prop('disabled', false);
    } else {
        $('#submit').prop('disabled', true);
    }
}

$("#submit").click(function (e) {
    e.preventDefault();
    $('#lb-require').html("");
    document.getElementById("txt-parameters").style.borderColor = "#707889"

    var config = $('#sl-configuration option:selected').text();
    var server = $('#sl-server option:selected').text();
    var view_id = $('#sl-view').val();

    tool = $('#sl-tool option:selected').text();
    parameters = $('#txt-parameters').val();
    var d = new Date();
    var milisecond = d.getMilliseconds().toString()
    var second = d.getSeconds().toString();
    var minute = d.getMinutes().toString();
    var hour = d.getHours().toString();
    var day = d.getDate().toString();
    var month = d.getMonth().toString();
    date = milisecond.concat(second, minute, hour, day, month)
    var s_name = server.split('(')[0]
    var server_name_re = '/\W/g'
    var server_name = s_name.replace(/\W/g, '_')
    window.clientID = server_name.concat('_', date)

    var regex = new RegExp("^([^$;`>|/]+)$")

    if (parameters == "" || regex.test(parameters) == false) {
        $('#lb-require').html("Invalid value. Input contains escape characters!")
        document.getElementById("txt-parameters").style.borderColor = "#cc0033"
    }

    var j_data = {
        "config-name": config,
        "view-id": view_id,
        "server": server,
        "tool": tool,
        "param": parameters,
        "client-id": window.clientID
    }

    var is_check = document.getElementById('lb-require').textContent;
    if (is_check == "") {
        window.submitted = true;
        unlockGUI(false);
        $('#result').val('Connecting...')
        $.ajax({
            url: '/trouble_shooting_ui/submit',
            type: 'post',
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify(j_data),
            success: function (data) {
                $('#result').val(data['result'])
                unlockGUI(false)
                var interval = setInterval(function () {
                    $.ajax({
                        url: `/trouble_shooting_ui/stream_result?configName=${config}&serverName=${server}&Tool=${tool}&clientID=${window.clientID}`,
                        type: 'get',
                        dataType: 'json',
                        contentType: 'application/json',
                        data: JSON.stringify(j_data),
                        success: function (data) {
                            var result = data[tool];
                            var status = data['status'];
                            unlockGUI(false)
                            $('#result').val(result)
                            if (status == true) {
                                clearInterval(interval);
                                unlockGUI(true)
                                clearConnectionAPI(config, server, window.clientID);
                                window.submitted = false;
                            }
                        }
                    });
                }, 1000);
            },
            error: function (xhr, status, error) {
                $('#result').val("Failed to get result while execute command. Please check the user logs for more information")
                unlockGUI(true)
            }
        });
    }
})

function clearConnectionAPI(config, server, clientID) {
    if (window.submitted === true) {
        $.ajax({
            url: `/trouble_shooting_ui/stream_result?configName=${config}&serverName=${server}&clientID=${clientID}`,
            type: 'DELETE',
            dataType: 'json',
            contentType: 'application/json',
            success: function (data) {

            },
            error: function (xhr, status, error) {
                $('#result').val("Failed to get result while execute command. Please check the user logs for more information")
                unlockGUI(true)
            }
        });
    }

}

window.onbeforeunload = (function () {
    config = $('#sl-configuration option:selected').text();
    server = $('#sl-server option:selected').text();
    clearConnectionAPI(config, server, window.clientID);
});

function getViews(configID) {
    $.ajax({
        url: '/trouble_shooting_ui/views?config_id=' + configID,
        type: 'get',
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
            var viewHTML = [];
            viewHTML.push(`<option value='0'>Not Selected</option>`)
            for (var i = 0; i < data.length; i++) {
                viewHTML.push(`<option value=${data[i].id}>${data[i].name}</option>`)
            }
            $('#sl-view').html(viewHTML);
            if (data.length > 0) {
                $('#sl-view').prop('disabled', false);
            }
        },
    });
}


function getServers(configID) {

    $.ajax({
        url: '/trouble_shooting_ui/server',
        type: 'post',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({
            'config_id': configID
        }),
        success: function (data) {
            var serverHTML = [];
            for (var i = 0; i < data.length; i++) {
                var serverIP = getProperty(data[i], 'defaultInterfaceAddress');
                serverHTML.push(`<option value='${data[i].name} (${serverIP})'>${data[i].name}(${serverIP})</option>`)
            }
            $('#sl-server').html(serverHTML);

            if (data.length > 0) {
                $('#sl-server').prop('disabled', false);
            }
            checkSubmit();
        },
    });
}