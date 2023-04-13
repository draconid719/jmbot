/*
Name: Main Js file for Crypterio Template
Date: 20 January 2019
Themeforest TopHive : https://themeforest.net/user/tophive
*/


'use strict';
jQuery(document).ready(function () {
    jQuery(document).on('click', '.crypt-header i.menu-toggle', function () {
        jQuery('.crypt-mobile-menu').toggleClass('show');
        jQuery(this).toggleClass('open')
    });

    jQuery(document).on('hover', '.crypt-mega-dropdown-toggle', function () {
        jQuery('.crypt-mega-dropdown-menu-block').toggleClass('shown');
    });
    jQuery(document).on('click', '.crypt-mega-dropdown-toggle', function (e) {
        e.preventDefault();
        jQuery('.crypt-mega-dropdown-menu-block').toggleClass('shown');
    });
    jQuery('[data-toggle="tooltip"]').tooltip();

    jQuery('#crypt-tab a').on('click', function (e) {

        e.preventDefault();

        var x = jQuery(this).attr('href');
        jQuery(this).parents().find('.crypt-tab-content .tab-pane').removeClass('active');
        jQuery(this).parents().find('.crypt-tab-content .tab-pane' + x).addClass('active');
    });

    jQuery(document).on('click', '.crypt-coin-select a', function (e) {
        e.preventDefault();
        var div = jQuery(this).attr('href');
        jQuery('.crypt-dash-withdraw').removeClass('d-block').addClass('d-none');
        jQuery(div).removeClass('d-none').addClass('d-block');
    });
    var path = window.location.href; // because the 'href' property of the DOM element is the absolute path

    jQuery('ul.crypt-heading-menu > li > a').each(function () {
        if (this.href === path) {
            jQuery(this).parent('li').addClass('active');
        } else {
            jQuery(this).parent('li').removeClass('active');
        }
        jQuery('.crypt-box-menu').removeClass('active');
    });

    // Notification
    function showNotification(user, message) {
        new Notification('New chat message', {
            body: user + ' : ' + message,
        })
    }

    function showBotNotification(user, message) {
        new Notification('New bot strategy', {
            body: user + ' : ' + message,
        })
    }

    function newShout() {
        jQuery.ajax({
            type: 'GET',
            url: '/shout/newmessage/',
            datatype: 'json',
            success: function (jsdata) {

                if (jsdata['new_mess']) {
                    console.log(Notification.permission);
                    if (Notification.permission === "granted") {
                        showNotification(jsdata['new_mess'][0], jsdata['new_mess'][1]);
                    } else if (Notification.permission !== "denied") {
                        Notification.requestPermission().then(permission => {
                            showNotification(jsdata['new_mess'][0], jsdata['new_mess'][1]);
                        });
                    }
                }
                if (jsdata['ping'] === 'true') {
                    document.getElementById('newchatnotif').innerHTML = '*'
                }
                if (jsdata['new_bot']) {
                    console.log(Notification.permission);
                    if (Notification.permission === "granted") {
                        showBotNotification(jsdata['new_bot'][0], jsdata['new_bot'][1]);
                    } else if (Notification.permission !== "denied") {
                        Notification.requestPermission().then(permission => {
                            showBotNotification(jsdata['new_bot'][0], jsdata['new_bot'][1]);
                        });
                    }
                }

                setTimeout(newShout, 10000)
            },
            error: function () {
                setTimeout(newShout, 10000)
            }
        })
    }

    /* Language Select */
    jQuery("#language-select").select2({
        minimumResultsForSearch: -1,
        width: '130px',
        height: '40px'
    });

    jQuery("#language-select").change(function () {
        jQuery("#language-select-form").submit();
    })

    newShout()
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}