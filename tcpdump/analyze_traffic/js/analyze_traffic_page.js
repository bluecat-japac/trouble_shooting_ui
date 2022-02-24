// Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.
$(document).ready(function () {
    getConfigurations();
    checkEnableButton();
});


function getConfigurations() {
    $.ajax({
        url: `/api/v1/analyze_traffic/configurations`,
        type: 'get',
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
            var result = [];
            result.push(`<option value='Please Select'>Please Select</option>`)
            for (i = 0; i < data.length; i++) {
                result.push(`<option value='${data[i]['name']}'>${data[i]['name']}</option>`)
            }
            $('#configuration').html(result);
            getServers();

        },
        error: function (message) {
            definedErrorMessage(message)
        }
    });
}


function getServers() {
    var configName = $('#configuration').val();
    $('#server').html(`<option value='Please Select'>Please Select</option>
                       <option value='${BAM_NAME}(${BAM_IP})'>${BAM_NAME}(${BAM_IP})</option>`)
    if (configName.includes('Please Select')) {
        $('#server').val(BAM_NAME + '(' + BAM_IP + ')');
        getInterface();
        return false
    } else {
        $('#interfaceName').val("Please Select")
    }

    $.ajax({
        url: `/api/v1/analyze_traffic/configurations/${configName}/servers`,
        type: 'get',
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
            var result = [];
            for (i = 0; i < data.length; i++) {
                serverIp = getProperty(data[i], 'defaultInterfaceAddress')
                result.push(`<option value='${data[i]['name']}(${serverIp})'>${data[i]['name']}(${serverIp})</option>`)
            }
            $('#server').html($('#server').html() + result);
        },
        error: function (message) {
            definedErrorMessage(message)
        }
    });
}


function checkEnableButton() {
    var interfaceName = $("#interfaceName").val();
    var packageToCapture = $("#packageToCapture").val();
    var maxCaptureFile = $("#maxCaptureFile").val();
    var maxCaptureTime = $("#maxCaptureTime").val().trim();
    disabledButton();

    if ((interfaceName != "Please Select" && packageToCapture && maxCaptureTime) || (interfaceName != "Please Select" && maxCaptureFile && maxCaptureTime)){
        enabledButton();
    }
}

function getInterface() {
    var configName = $('#configuration').val();
    if (configName.includes('Please Select')){
        configName = '';
    }
    var server = $('#server').val();
    if (server.includes('Please Select')){
        return
    }
    server_ip = server.substring(server.indexOf('(') + 1,server.indexOf(')'))
    $.ajax({
        url: `/api/v1/analyze_traffic/interfaces?configuration_name=${configName}&server_ip=${server_ip}`,
        type: 'get',
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
                var result = [];
                result.push(`<option value='Please Select'>Please Select</option>`)
                for (i = 0; i < data.length; i++) {
                    result.push(`<option value='${data[i]}'>${data[i]}</option>`)
                }
                $('#interfaceName').html(result);
        },
        error: function (message) {
            definedErrorMessage(message)
        }
    });
}

function startTCPDump() {
    var configName = $('#configuration').val();
    if (configName.includes('Please Select')){
        configName = '';
    }
    var server = $('#server').val();
    server_ip = server.substring(server.indexOf('(') + 1,server.indexOf(')'));
    var interface = $('#interfaceName').val();
    var port = $('#port').val().trim();
    if (port == "") {
        port = $('#port').val(null)
    }
    var packetsToCapture = $('#packageToCapture').val().trim();
    if (packetsToCapture == "") {
        packetsToCapture = $('#packageToCapture').val(null)
    }
    var optional = $('#Optional').val().trim();
    var maxCaptureFile = $('#maxCaptureFile').val().trim();
    if (maxCaptureFile == "") {
        maxCaptureFile = $('#maxCaptureFile').val(null)
    }
    var maxCaptureTime = $('#maxCaptureTime').val().trim();
    var data = {
        "configuration_name": configName,
        "server_ip": server_ip,
        "interface": interface,
        "port": Number(port),
        "packets_to_capture": Number(packetsToCapture),
        "max_capture_file": Number(maxCaptureFile),
        "max_capture_time": Number(maxCaptureTime),
        "optional": optional
    }
    $.ajax({
        url: `/api/v1/analyze_traffic/start`,
        type: 'post',
        data: JSON.stringify(data),
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
            definedSuccessMessage(data)
        },
        error: function (message) {
            definedErrorMessage(message)
        }
    });
}

function stopTCPDump() {
    var configName = $('#configuration').val();
    if (configName.includes('Please Select')){
        configName = '';
    }
    var server = $('#server').val();
    server_ip = server.substring(server.indexOf('(') + 1,server.indexOf(')'));
    var data = {
        "configuration_name": configName,
        "server_ip": server_ip
    }
    $.ajax({
        url: `/api/v1/analyze_traffic/stop`,
        type: 'post',
        data: JSON.stringify(data),
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
            definedSuccessMessage(data)
        },
        error: function (message) {
            definedErrorMessage(message)
        }
    });
}

function downloadCapture() {
    var configName = $('#configuration').val();
    if (configName.includes('Please Select')){
        configName = '';
    }
    var server = $('#server').val();
    server_ip = server.substring(server.indexOf('(') + 1,server.indexOf(')'));
    var $content = DEFAULT_CONTENT;
    $('body').prepend($content);
    var href = window.location.origin + '/api/v1/analyze_traffic/download?' + `configuration_name=${configName}&server_ip=${server_ip}`
    window.location.href = href;
    setTimeout(
        function () {
            $("#wait").remove();
        }, 3500);
}

function checkStatus() {
    var configName = $('#configuration').val();
    if (configName.includes('Please Select')){
        configName = '';
    }
    var server = $('#server').val();
    server_ip = server.substring(server.indexOf('(') + 1,server.indexOf(')'));
    $.ajax({
        url: `/api/v1/analyze_traffic/status?configuration_name=${configName}&server_ip=${server_ip}`,
        type: 'get',
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
            if ('Running'.includes(data) || 'Stopped'.includes(data)){
                definedSuccessMessage(`Tcpdump status is ${data}`)
            }
        },
        error: function (message) {
            definedErrorMessage(message)
        }
    });
}
    
function getProperty(entity, name) {
    var result = "";
    var properties = entity['properties'].split("|");
    for (p = 0; p < properties.length; p++) {
        if (properties[p].includes(`${name}`)) {
            result = properties[p].split("=")[1];
        }
    }
    return result
}

function validateInputField() {
    var port = $('#port').val().trim();
    if (port < 0 || port > 65535){
        definedSmallErrorMessage('errorPort', "Invalid Port. It's must be integer, between 0 and 65535.");
        disabledButton();
    } else {
        $('#errorPort').html('');
    }
    var packetsToCapture = $('#packageToCapture').val().trim();
    if (packetsToCapture == ''){
        $('#errorPackageToCapture').html('');
    } else if (packetsToCapture <= 0 || packetsToCapture >= 1000){
        definedSmallErrorMessage('errorPackageToCapture', "Invalid Packets To Capture. It's must be integer, between 1 and 999.");
        disabledButton();
    } else {
        $('#errorPackageToCapture').html('');
    }
    var maxCaptureFile = $('#maxCaptureFile').val().trim();
    if (maxCaptureFile == ''){
        $('#errorMaxCaptureFile').html('');
    } else if (maxCaptureFile <= 0 || maxCaptureFile >= 20){
        definedSmallErrorMessage('errorMaxCaptureFile', "Invalid Max Capture File Size. It's must be integer, between 1 and 19.");
        disabledButton();
    } else {
        $('#errorMaxCaptureFile').html('');
    }
    var maxCaptureTime = $('#maxCaptureTime').val().trim();
    if (maxCaptureTime == ''){
        $('#errorMaxCaptureTime').html('');
    } else if (maxCaptureTime <= 0 || maxCaptureTime >= 300){
        definedSmallErrorMessage('errorMaxCaptureTime', "Invalid Max Capture Time. It's must be integer, between 1 and 299.");
        disabledButton();
    } else {
        $('#errorMaxCaptureTime').html('');
    }
}

function disabledButton(){
    $("#start").prop("disabled", true);
    $("#stop").prop("disabled", true);
    $("#download").prop("disabled", true);
    $("#checkStatus").prop("disabled", true);
}

function enabledButton(){
    $("#start").prop("disabled", false);
    $("#stop").prop("disabled", false);
    $("#download").prop("disabled", false);
    $("#checkStatus").prop("disabled", false);
}

function clearField(){
    $("#interfaceName").val('Please Select');
    $("#port").val('');
    $("#packageToCapture").val('');
    $("#maxCaptureFile").val('');
    $("#maxCaptureTime").val('');
}