// Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.
$(document).ready(function () {
    $('#deleteSelected').prop('disabled', true)
    getBackupData();
});


function getBackupData(isSkipCheck) {
    $.ajax({
        url: `/api/v1/bam_backup/backup_file`,
        type: 'get',
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
            var bkDataHTML = [];
            if (data.length == 0 & !isSkipCheck) {
                $('#statusMsg').addClass('inform');
                $("#statusMsg").text('BAM Backup Data not found.');
                return false
            }

            for (var i = 0; i < data.length; i++) {
                bkDataHTML.push(`<tr><td>
                                    <input type="checkbox" id="ck_${data[i]['name']}" class="input-track" onclick="checkDeleteSelected()">
                                    <div style="margin-top: 5px;">${data[i]['name']}</div>
                                </td>
                                <td>${data[i]['date']}</td>
                                <td>${data[i]['size']}</td>
                                <td>
                                    <i class="fa fa-download" aria-hidden="true" id='downBackup_${data[i].name}' onclick='downBackupFile("${data[i].name}")'></i>
                                </td></tr>`)
            }
            $('#bkDataTable > tbody').html(bkDataHTML);
            $('#runBackup').prop("disabled", false);
            if (data.length >= MAX_COUNT_FILE) {
                definedErrorMessage(`The number of backup files have reached the maximum file count (${MAX_COUNT_FILE}). Please delete to continue run backup.`)
                $('#runBackup').prop("disabled", true);
            }
        },
        error: function (message) {
            definedErrorMessage(message)
        }
    });
}


function downBackupFile(bkName) {
    var $content = DEFAULT_CONTENT;
    $('body').prepend($content);
    var href = window.location.origin + '/api/v1/bam_backup/local_backup_path/' + bkName
    window.location.href = href;
    setTimeout(
        function () {
            $("#wait").remove();
        }, 3500);

}


function checkDeleteSelected() {
    ($("input[type=checkbox][id^='ck_']:checked").length > 0) ? $('#deleteSelected').prop('disabled', false): $('#deleteSelected').prop('disabled', true);
}


function runBackup() {
    $.ajax({
        url: `/api/v1/bam_backup/run`,
        type: 'post',
        dataType: 'json',
        contentType: 'application/json',
        success: function (result) {
            getBackupData(true);
            (result.includes('successfully') ? definedSuccessMessage(result) : definedErrorMessage(result));
        },
        error: function (message) {
            definedErrorMessage(message)
        }
    });
}


function checkBackupStatus() {
    $.ajax({
        url: `/api/v1/bam_backup/check_status`,
        type: 'get',
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
            (data.length > 0) ? $('#checkBKStatus').show(): $('#checkBKStatus').hide();
            var bkStatusHTML = [];
            for (var i = 0; i < data.length; i++) {
                bkStatusHTML.push(`<tr>
                                    <td>${data[i]['name']}</td>
                                    <td>${data[i]['start_time']}</td>
                                    <td>${data[i]['end_time']}</td>
                                    <td>${data[i]['status']}</td>
                                </tr>`)
            }
            $('#bkStatusTable > tbody').html(bkStatusHTML);
            definedSuccessMessage('Check backup status successfully.');

        },
        error: function (message) {
            definedErrorMessage(message)
        }
    });
}



function deleteBackupFile(bkName) {
    var bkList = [bkName];
    if (!bkName) {
        var bkList = [];
        $("input[type=checkbox][id^='ck_']:checked").each(function (element, index) {
            var bkName = $(this).attr("id").replace('ck_', '');
            bkList.push(bkName);
        })
    }

    var bkListHTML = '';
    for (var j =0;j<bkList.length;j++){
        bkListHTML += `<li style='margin-left:30px'>${bkList[j]}</li>`
    }

    var $content = `<div class='dialog-ovelay'>
                        <div class='dialog'>
                            <header>
                                <h3>Confirm Delete Backup File(s)</h3><i class='fa fa-close'></i>
                            </header>
                            <div class='dialog-msg' style='margin-bottom:5px;'>
                                <p>Backup File(s): <br> 
                                <ul style="list-style-type:square">${bkListHTML}</ul> will be deleted!</p>
                                <p>Do you still want to continue ?</p>
                            </div>
                            <footer>
                                <div class='controls' style='margin-left:5px'>
                                    <button class='button button-default btn-primary doAction' style='margin-right:10px!important'>Yes</button>
                                    <button class='button button-danger btn-default cancelAction' style='float: unset!important;'>No</button>
                                </div>
                            </footer>
                        </div>
                    </div>`;
    $('body').prepend($content);
    $('.doAction').click(function () {
        $(this).parents('.dialog-ovelay').fadeOut(500, function () {
            $(this).remove();
        });

        $.ajax({
            url: `/api/v1/bam_backup/backup_file`,
            type: 'delete',
            dataType: 'json',
            data: JSON.stringify({
                'backup_files_name': bkList
            }),
            contentType: 'application/json',
            success: function (result) {
                getBackupData(true);
                (result.includes('successfully') ? definedSuccessMessage(result) : definedErrorMessage(result));
            },
            error: function (message) {
                definedErrorMessage(message)
            }
        });

    });
    $('.cancelAction, .fa-close').click(function () {
        $(this).parents('.dialog-ovelay').fadeOut(500, function () {
            $(this).remove();
        });
    });


}
