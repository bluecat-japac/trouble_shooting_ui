// Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.
$(document).ready(function () {
    // Show more (simple toggle) JS implementation
    // how to set it up
    // add to an 'a' element the class show-more
    // params:
    // + data-target: the div you want to toggle
    // + data-default: 'open' or 'close' (default state of the toggle)
    //                 will be open if not specified
    // for example:
    // <a class="fas show-more" data-target="#aliasHostDiv" data-default="open">

    $(".show-more").each(function () {
        var default_state = $(this).data("default");

        if (default_state == "close") {
            $(this).removeClass("fa-angle-down")
            $(this).addClass("fa-angle-right");
            var target_element = $(this).data("target");
            $(target_element).css("display", "none");
        } else if (default_state == "open" || default_state === undefined) {
            $(this).addClass("fa-angle-down")
            $(this).removeClass("fa-angle-right");
            var target_element = $(this).data("target");
            $(target_element).css("display", "block");
        }

    })
    // assign callback
    $(".show-more").on('click', function () {
        var openStatus = $(this).hasClass("fa-angle-down");
        var target_element = $(this).data("target");
        if (openStatus) {
            $(target_element).css("display", "none");
            $(this).removeClass("fa-angle-down")
            $(this).addClass("fa-angle-right");
        } else {
            $(target_element).css("display", "block");
            $(this).removeClass("fa-angle-right")
            $(this).addClass("fa-angle-down");
        }
    })
})