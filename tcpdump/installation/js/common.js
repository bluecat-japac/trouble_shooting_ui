// Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.

let BAM_NAME = $('#bamName').text();
let DEFAULT_CONTENT = "<div class='dialog-ovelay' id='wait'><i class='fa fa-spinner fa-spin' style='font-size: 60px; margin-left: 48%; margin-top: 20%;'></i></div>";

$(document).ready(function(){
    $(".footer").removeClass("row")

    $(document).ajaxStart(function () {
        var $content = DEFAULT_CONTENT;
        console.log($content)
        $('body').prepend($content);
    });

    $(document).ajaxStop(function () {
        $("#wait").remove();
    });
})

function definedErrorMessage(message) {
    $('#statusMsg').html('');
    $('#statusMsg').removeClass('succeed').removeClass('inform').addClass('flash');
    errorMessage = message
    if (message.responseText) {
        errorMessage = (message.responseText.includes('"')) ? message.responseText.replace(/"/g, ' ') : message.responseText;
    } else if (message.responseJSON) {
        errorMessage = message.responseJSON
    }
    $('#statusMsg').html(errorMessage);
}

function definedSuccessMessage(message){
    $('#statusMsg').html('');
    $('#statusMsg').removeClass('flash').removeClass('inform').addClass('succeed');
    $("#statusMsg").text(message);
}
