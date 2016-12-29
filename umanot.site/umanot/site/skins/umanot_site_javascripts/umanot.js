$(function () {

    var $window = $(window);
    var $header = $('#portal-header');
    var $backtotop = $('#backtotop');
    var $body = $('body');


    //Scroll BEHAVIORs
    $window.on('scroll', function () {

        if ($(this).scrollTop() > 100) {
            $header.addClass('white');
            $backtotop.fadeIn();
        } else {
            $header.removeClass('white');
            $backtotop.fadeIn();
        }

    });

    // MESSAGE COOKIE

    jQuery.cookie = function (key, value, options) {

        if (arguments.length > 1 && String(value) !== "[object Object]") {
            options = jQuery.extend({}, options);

            if (value === null || value === undefined) {
                options.expires = -1;
            }

            if (typeof options.expires === 'number') {
                var days = options.expires, t = options.expires = new Date();
                t.setDate(t.getDate() + days);
            }

            value = String(value);

            return (document.cookie = [
                encodeURIComponent(key), '=',
                options.raw ? value : encodeURIComponent(value),
                options.expires ? '; expires=' + options.expires.toUTCString() : '',
                options.path ? '; path=' + options.path : '',
                options.domain ? '; domain=' + options.domain : '',
                options.secure ? '; secure' : ''
            ].join(''));
        }

        options = value || {};
        var result, decode = options.raw ? function (s) {
            return s;
        } : decodeURIComponent;
        return (result = new RegExp('(?:^|; )' + encodeURIComponent(key) + '=([^;]*)').exec(document.cookie)) ? decode(result[1]) : null;
    };


    //MESSAGE BOX
    var $messageBox = $('#message-box');

    $window.on('scroll', function () {

        if ($(this).scrollTop() > 100) {

            if (jQuery.cookie('messageCookieCheck') != 'checked') {
                $messageBox.addClass('active');
            }

        } else {
            $messageBox.removeClass('active');
        }

    });

    $('#message-box-close').on('click', function () {
        $messageBox.remove();
        jQuery.cookie('messageCookieCheck', 'checked', {path: '/'});
    });

    //BACK TO TOP
    $backtotop.click(function () {
        $('body,html').animate({
            scrollTop: 0
        }, 1000);
        return false;
    });

    //PREVENT SCROLL DOWN ON REFRESH
    //window.onload = function () {
    //    window.scrollTo(0, 0);
    //};

    //MASONRY INIT

    if ($('#article-section').length != 0) {

        var container = document.querySelector('#article-section .isotope');
        var msnry;
        // initialize Masonry after all images have loaded
        imagesLoaded(container, function () {
            msnry = new Masonry(container, {
                // options
                gutter: 10,
                itemSelector: '.articleItem'
            });
        });

    }

    //TOOLTIP
    $('[data-toggle="tooltip"]').tooltip();

    //NAV
    $('#nav-switch').on('click', function () {
        $body.toggleClass('mobileMenuOn');
    });


    //FOLLOW MODAL TRIGGER
    var $followModal = $('#follow-modal');
    $('.followModalTrigger').on('click', function (e) {
        e.preventDefault();
        $.ajax({url: $(this).attr('href')}).done(function (data) {
            $followModal.find('.modal-content').empty().append(data);
            $followModal.modal('show');
        });
    });

    // ANCHOR
    var anchorOnClick = function () {
        $('a[href*=#]').on('click', function (event) {
            var target = $(this.hash);

            if (target.length == 0) {
                target = $('[name="' + $.attr(this, 'href').substr(1) + '"]');
            }

            if (target.length > 0) {
                event.preventDefault();
                $('html,body').animate({scrollTop: target.offset().top - 81}, 500);
            }
            else {

            }
        });
    };

    anchorOnClick();

    var $elem = $('#' + window.location.hash.replace('#', ''));
    if($elem.length > 0) {
        $('html,body').animate({scrollTop: $elem.offset().top - 81}, 500);
    }

    $('#form.actions.shutdown').hide()
});