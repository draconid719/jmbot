$(document).ready(function () {
    function startThread(elem, actionType) {
        $.ajax({
            type: 'POST',
            url: '/admin/bot/thread/start_threads/',
            data: {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                action: actionType
            },
            success: function (data) {
                if (data.status) {
                    console.log(data.status);
                    window.location.reload();
                }
            },
            error: function (error) {
                console.log(error)
                $(elem).find('span').addClass('d-none')
                $(elem).attr("disabled", false)
            }
        })
    }

    $("#startThreads").click(function (e) {
        e.preventDefault();
        $(this).attr("disabled", true)
        $(this).find('span').removeClass('d-none')
        startThread(this, 'start');
    });

    $("#stopThreads").click(function (e) {
        e.preventDefault();
        $(this).attr("disabled", true)
        $(this).find('span').removeClass('d-none')
        startThread(this, 'stop');
    });

    $("#startTick").click(function (e) {
        e.preventDefault();
        $(this).attr("disabled", true)
        $(this).find('span').removeClass('d-none')
        startThread(this, 'start-tick');
    });

    $("#stopTick").click(function (e) {
        e.preventDefault();
        $(this).attr("disabled", true)
        $(this).find('span').removeClass('d-none')
        startThread(this, 'stop-tick');
    });
})