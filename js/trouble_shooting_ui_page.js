
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
    
    $('#txt-parameters').attr("placeholder", "<specify IP address>");
    $('#submit').prop('disabled', true);
    $('#sl-config').prop('disabled', true);
    $('#sl-server').prop('disabled', true);
    $('#txt-parameters').val('');
    $('#result').val('');
    onLoad();
})

var placeholderText = {
    "dig": "@<server IP address> <name query>",
    "ping": "<specify IP address>",
    "traceroute": "<specify IP address>"
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

    server = $('#sl-server option:selected').text();
    tool = $('#sl-tool option:selected').text();
    parameters = $('#txt-parameters').val();

    var ip_pattern = '(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])'
    var ping_re = new RegExp("^" + ip_pattern + "$")
    var dig_re = new RegExp("^@" + ip_pattern + "+ (([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")
    var traceroute_re = new RegExp("^" + ip_pattern + "$")

    if (tool == "ping"){
        if (parameters == "" || ping_re.test(parameters) == false) {
            $('#lb-require').html("Invalid value. It must be a valid IPv4 address.")
            document.getElementById("txt-parameters").style.borderColor = "#cc0033"
        }
    } else if (tool == "dig"){
        if (parameters == "" || dig_re.test(parameters) == false) {
            $('#lb-require').html("You entered wrong dig format. Please check it again!")
            document.getElementById("txt-parameters").style.borderColor = "#cc0033"
        }
    } else {
        if (parameters == "" || traceroute_re.test(parameters) == false) {
            $('#lb-require').html("Invalid value. It must be a valid IPv4 address.")
            document.getElementById("txt-parameters").style.borderColor = "#cc0033"
        }
    }

    var is_check = document.getElementById('lb-require').textContent;
    if ( is_check == ""){
        $('#sl-configuration').prop('disabled', true);
        $('#sl-server').prop('disabled', true);
        $('#sl-tool').prop('disabled', true);
        $('#txt-parameters').prop('disabled', true);
        $('#submit').prop('disabled', true);
        $('#result').val('Connecting...')
        $.ajax({
            url: '/trouble_shooting_ui/submit',
            type: 'post',
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify({
                'server': server,
                'tool': tool,
                'parameters': parameters
            }),
            success: function (data) {
                $('#sl-configuration').prop('disabled', false);
                $('#sl-server').prop('disabled', false);
                $('#sl-tool').prop('disabled', false);
                $('#txt-parameters').prop('disabled', false);
                $('#submit').prop('disabled', false);
                $('#result').val(data['result'])
            },
        });
    }
})