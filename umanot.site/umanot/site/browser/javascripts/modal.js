$(document).ready(function() {

/*
	$('.product-modal').magnificPopup({
		type: 'ajax',
		alignTop: false,
		overflowY: 'scroll' 
	});
*/
	
	var ajaxModalInit = function () {

    //AJAX MODALS
    $ajaxModal = $('#ajax-modal');
    $ajaxModalBody = $('.modal-body', $ajaxModal);
    $('.ajaxModalTrigger', '#page').on('click', function (e) {
        e.preventDefault();
        var modalType = $(this).attr('data-modaltype');
        var url = $(this).attr('href');

        $.ajax({
            url: url
        }).done(function (data) {
            $ajaxModal.addClass(modalType);
            $ajaxModalBody.append(data);
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
	
	
});