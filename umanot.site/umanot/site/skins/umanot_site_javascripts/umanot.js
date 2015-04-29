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
  
  //MASONRY INIT
  var container = document.querySelector('#article-section .isotope');
  var msnry;
  // initialize Masonry after all images have loaded
  imagesLoaded( container, function() {
    msnry = new Masonry( container , {
      // options
      gutter: 10,
      itemSelector: '.articleItem'
    });
  });

  //TOOLTIP
  $('[data-toggle="tooltip"]').tooltip();
  
  //NAV
  $('#nav-switch').on('click', function(){
    $body.toggleClass('mobileMenuOn');
  });
  
});