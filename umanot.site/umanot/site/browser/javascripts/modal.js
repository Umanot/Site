$(document).ready(function () {

    /*
     $('.product-modal').magnificPopup({
     type: 'ajax',
     alignTop: false,
     overflowY: 'scroll'
     });
     */

    var ajaxModalInit = function () {

        //AJAX MODALS
        $ajaxModal = $('#follow-modal');

        $ajaxModalBody = $('.modal-body', $ajaxModal);

        $('.ajaxModalTrigger').on('click', function (e) {
            e.preventDefault();
            var modalType = $(this).attr('data-modaltype');

            var url = $(this).attr('href');

            $.ajax({
                url: url
            }).done(function (risultato_della_chiamata_ajax) {
                $ajaxModal.addClass(modalType);
                $ajaxModalBody.append(risultato_della_chiamata_ajax);
                $ajaxModal.modal('show');
            });

        });

        $('.modalClose', $ajaxModal).on('click', function () {
            $ajaxModal.modal('hide');
        });

        $ajaxModal.on('hidden.bs.modal', function (e) {
            $ajaxModalBody.empty();
            $ajaxModal.removeClass().addClass('modal fade');
        });
    };

    ajaxModalInit();

});