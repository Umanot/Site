$(function(){
  
  var $window = $(window);
  var $header = $('#portal-header');
  var $backtotop =  $('#backtotop');
  var $body = $('body');
  
  //Scroll BEHAVIORs
  $window.on('scroll', function(){
    
    if ($(this).scrollTop() > 100) {
  		$header.addClass('white');
      $backtotop.fadeIn();    
    } else {
  		$header.removeClass('white');
      $backtotop.fadeIn();    
    }
  
  });
  
  //BACK TO TOP
  $backtotop.click(function () {
    $('body,html').animate({
    	scrollTop: 0
    }, 1000);
    return false;
  });
  
  //PREVENT SCROLL DOWN ON REFRESH
  window.onload = function () {
      window.scrollTo(0, 0);
  };
  
/*
  var $container = $('.isotope').isotope({
                      itemSelector: '.articleItem',
                      layoutMode: 'masonry',
                      masonry : {
                        gutter : 30
                      }
                   });
*/
  
  //TOOLTIP
  $('[data-toggle="tooltip"]').tooltip();
  
  //NAV
  $('#nav-switch').on('click', function(){
    $body.toggleClass('mobileMenuOn');
  });
  
});