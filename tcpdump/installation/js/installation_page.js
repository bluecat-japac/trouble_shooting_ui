// Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.
var dataHTML = []

$(document).ready(function () {
    getConfigurations();
    loadServer();
    resetDataTable();
});


function getConfigurations() {
    $.ajax({
        url: `/api/v1/installation/configurations`,
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
    $('#server').html(`<option value='${BAM_NAME}(${BAM_IP})'>${BAM_NAME}(${BAM_IP})</option>`)
    if (configName.includes('Please Select')) {
        $('#server').val(BAM_NAME + '(' + BAM_IP + ')');
//        $('#install').removeAttr('disabled', 'disabled');
//        $('#uninstall').removeAttr('disabled', 'disabled');
        $('#remove').removeAttr('disabled', 'disabled');
        return false
    } else {
        loadServer();
//        $('#install').attr('disabled', true);
//        $('#uninstall').attr('disabled', true);
        $('#remove').attr('disabled', true);
    }

    $.ajax({
        url: `/api/v1/installation/configurations/${configName}/servers`,
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
//
//function installTCPDump() {
//    var configName = $('#configuration').val();
//    if (configName.includes('Please Select')){
//        configName = '';
//    }
//    var element = '';
//    var servers = [];
//    var listServerIp = [];
//    servers = $('#server').val();
//    for (var i = 0; i < servers.length; i++) {
//        serverIp = servers[i].substring(servers[i].indexOf('(') + 1,servers[i].indexOf(')'))
//        listServerIp.push(serverIp)
//    }
//    var data = {
//        "configuration_name": configName,
//        "server_ips": listServerIp
//    }
//    $.ajax({
//        url: `/api/v1/installation/package/install`,
//        type: 'post',
//        data: JSON.stringify(data),
//        dataType: 'json',
//        contentType: 'application/json',
//        success: function (data) {
//            dataHTML = []
//            for (i = 0; i < data.length; i++) {
//                if (data[i].status == true) {
//                    dataHTML.push(`<tr class="rowTable"><td>${data[i].server_name}</td>
//                                 <td style="color:#76CE66;">${data[i].message}</td></tr>`)
//                } else {
//                    dataHTML.push(`<tr class="rowTable"><td>${data[i].server_name}</td>
//                                 <td style="color:#FF0000;">${data[i].message}</td></tr>`)
//                }
//                $('#dataTable > #bodyTable').html(dataHTML);
//            }
//        },
//        error: function (message) {
//            definedErrorMessage(message)
//        }
//    });
//}
//
//function uninstallTCPDump() {
//    var configName = $('#configuration').val();
//    if (configName.includes('Please Select')){
//        configName = '';
//    }
//    var element = '';
//    var servers = [];
//    var listServerIp = [];
//    servers = $('#server').val();
//    for (var i = 0; i < servers.length; i++) {
//        serverIp = servers[i].substring(servers[i].indexOf('(') + 1,servers[i].indexOf(')'))
//        listServerIp.push(serverIp)
//    }
//    var data = {
//        "configuration_name": configName,
//        "server_ips": listServerIp
//    }
//    $.ajax({
//        url: `/api/v1/installation/package/uninstall`,
//        type: 'post',
//        data: JSON.stringify(data),
//        dataType: 'json',
//        contentType: 'application/json',
//        success: function (data) {
//            for (i = 0; i < data.length; i++) {
//                if (data[i].status == true) {
//                    element = '<div class="row" data-region-id="' + 'regionName' + '" style="margin-bottom: 10px;">' +
//                               '<div class="col-xs-4" style="padding-left: 14px;width:30%;overflow-wrap: break-word;">' +
//                               data[i].server_name+
//                              '</div>' +
//                              '<div class="col-xs-6" style="color:#76CE66;margin-left:-21px;overflow-wrap: break-word">' +
//                               data[i].message+
//                              '</div>'+
//                              '</div>'
//                } else {
//                    element = '<div class="row" data-region-id="' + 'regionName' + '" style="margin-bottom: 10px;">' +
//                               '<div class="col-xs-4" style="padding-left: 14px;width:30%;overflow-wrap: break-word;">' +
//                               data[i].server_name+
//                              '</div>' +
//                              '<div class="col-xs-6" style="color:#FF0000;margin-left:-21px;overflow-wrap: break-word">' +
//                               data[i].message+
//                              '</div>'+
//                              '</div>'
//                }
//                $('#tcpdump-table-body').append(element)
//            }
//        },
//        error: function (message) {
//            definedErrorMessage(message)
//        }
//    });
//}

function removeTCPDump() {
    var configName = $('#configuration').val();
    if (configName.includes('Please Select')){
        configName = '';
    }
    var element = '';
    var servers = [];
    var listServerIp = [];
    servers = $('#server').val();
    for (var i = 0; i < servers.length; i++) {
        serverIp = servers[i].substring(servers[i].indexOf('(') + 1,servers[i].indexOf(')'))
        listServerIp.push(serverIp)
    }
    var data = {
        "configuration_name": configName,
        "server_ips": listServerIp
    }
    $.ajax({
        url: `/api/v1/installation/package/uninstall`,
        type: 'post',
        data: JSON.stringify(data),
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
            dataHTML = []
            for (i = 0; i < data.length; i++) {
                if (data[i].status == true) {
                    dataHTML.push(`<tr class="rowTable"><td>${data[i].server_name}</td>
                                 <td style="color:#76CE66;">${data[i].message}</td></tr>`)
                } else {
                    dataHTML.push(`<tr class="rowTable"><td>${data[i].server_name}</td>
                                 <td style="color:#FF0000;">${data[i].message}</td></tr>`)
                }
                $('#dataTable > #bodyTable').html(dataHTML);
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

function loadServer() {
    $('#server').select2({
        placeholder: 'Please Select',
        minimumResultsForSearch: -1,
        allowClear: true,
        templateResult: hideSelected,
        createTag: function () {
            return null;
        }
    });
}

function hideSelected(value) {
    if (value && !value.selected) {
        return $('<span>' + value.text + '</span>');
    }
}

function disabledButton(){
    servers = $('#server').val();
    if (servers.length > 0) {
//        $('#install').removeAttr('disabled', 'disabled');
//        $('#uninstall').removeAttr('disabled', 'disabled');
        $('#remove').removeAttr('disabled', 'disabled');
    } else {
//        $('#install').attr('disabled', true);
//        $('#uninstall').attr('disabled', true);
        $('#remove').attr('disabled', true);
        resetDataTable();
    }
}

function resetDataTable(){
    dataHTML = []
    dataHTML.push(`<tr class="noData"><td colspan="2" style="font-weight:bold">There is no data in this table</td></tr>`);
    $('#dataTable > #bodyTable').html(dataHTML);
}