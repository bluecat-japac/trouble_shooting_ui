
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
    $('#txt-parameters').val('');
    $('#sl-tool').val('ping');
    $('#result').val('');
    onLoad();
})

var placeholderText = {
    "dig": "@<server IP address> <name query>",
    "ping": "<IP address> [<option>]",
    "traceroute": "<IP address>"
};

function checkInput(){
    config = $('#sl-configuration option:selected').text();
    server = $('#sl-server option:selected').text();
    if (config != ""){
        $('#sl-config').prop('disabled', false);
        $('#sl-server').prop('disabled', false);
    }
    if (server != ""){
        $('#sl-server').prop('disabled', false);
    }
}

function unlockGUI(boolean) {
    if (boolean == true) {
        $('#sl-configuration').prop('disabled', false);
        $('#sl-server').prop('disabled', false);
        $('#sl-tool').prop('disabled', false);
        $('#txt-parameters').prop('disabled', false);
        $('#submit').prop('disabled', false);
    }
    else if (boolean == false) {
        $('#sl-configuration').prop('disabled', true);
        $('#sl-server').prop('disabled', true);
        $('#sl-tool').prop('disabled', true);
        $('#txt-parameters').prop('disabled', true);
        $('#submit').prop('disabled', true);
    }
}

function setPlaceholder() {
    $('#txt-parameters').attr("placeholder", placeholderText[$("#sl-tool option:selected").text()]);
}

function onLoad() {
    $.ajax({
        url: '/trouble_shooting_ui/onload',
        type: 'get',
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
            var config = [];
            for (var i = 0; i < data['configurations'].length; i++) {
                config.push(`<option value=${data['configurations'][i][0]}>${data['configurations'][i][1]}</option>`)
            }
            var server = [];
            for (var i = 0; i < data['server'].length; i++) {
                server.push(`<option value=${data['server'][i][0]}(${data['server'][i][1]})>${data['server'][i][0]}(${data['server'][i][1]})</option>`)
            }
            $('#bam').val(data['bam']);
            $('#sl-configuration').html(config);
            $('#sl-server').html(server);

            if (configuration_name != ""){
                updateServerList(true)
            }
            checkInput();
        },
    });
}

function updateServerList(isCheck=false) {
    $('#sl-server').prop('disabled', true);
    if (isCheck == false){
        var config = document.getElementById('sl-configuration').value;
    } else {
        var config = configuration_id
    }
    $.ajax({
        url: '/trouble_shooting_ui/server',
        type: 'post',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({
            'config': config
        }),
        success: function (data) {
            var server = [];
            for (var i = 0; i < data['server'].length; i++) {
                 server.push(`<option value=${data['server'][i][0]}(${data['server'][i][1]})>${data['server'][i][0]}(${data['server'][i][1]})</option>`)
            }
            $('#sl-server').html(server);

            if ($('#sl-server option:selected').text() != ""){
                $('#sl-server').prop('disabled', false);
            }

            if (configuration_name != "" && server_str != "" && isCheck==true){
                $('#sl-configuration option:contains(' + configuration_name + ')').attr('selected', 'selected');
                $('#sl-server').val(server_str);
            }
            checkSubmit();
        },
    });
}


function checkSubmit() {
    server = $('#sl-server').text();
    parameters = $('#txt-parameters').val();
    if (server != '' && parameters != '') {
        $('#submit').prop('disabled', false);
    } else {
        $('#submit').prop('disabled', true);
    }
}

$("#submit").click(function (e) {
    e.preventDefault();
    $('#lb-require').html("");
    document.getElementById("txt-parameters").style.borderColor ="#707889"

    config = $('#sl-configuration option:selected').text();
    server = $('#sl-server option:selected').text();
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
        "server": server,
        "tool": tool,
        "param": parameters,
        "client-id": window.clientID
    }

    var is_check = document.getElementById('lb-require').textContent;
    if ( is_check == ""){
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
                var interval = setInterval(function(){
                    $.ajax({
                        url: `/trouble_shooting_ui/stream_result?configName=${config}&serverName=${server}&Tool=${tool}&clientID=${window.clientID}`,
                        type: 'get',
                        dataType: 'json',
                        contentType: 'application/json',
                        data: JSON.stringify(j_data),
                        success: function (data){
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
            error: function(xhr, status, error) {
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
            error: function(xhr, status, error) {
                $('#result').val("Failed to get result while execute command. Please check the user logs for more information")
                unlockGUI(true)
            }
        });
    }
    
}

window.onbeforeunload = (function() {
    config = $('#sl-configuration option:selected').text();
    server = $('#sl-server option:selected').text();
    clearConnectionAPI(config, server, window.clientID);
});