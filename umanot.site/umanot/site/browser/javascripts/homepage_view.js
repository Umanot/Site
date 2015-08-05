        var $introSection = $('#intro-section');
        var $introText = $introSection.find('.introText');
      
        $introSection.find('.owl-carousel').owlCarousel({
            loop:true,
            items:1,
            navText: ['<i class="fa fa-angle-left"></i>','<i class="fa fa-angle-right"></i>'],
            autoplay:true,
            autoplayTimeout:5000,
            autoplayHoverPause:false,
            responsive:{
                999:{
                  nav: false
                },
                1000: {
                  nav : true
                }
            },
        });
        
        var $newsSection = $('#news-carousel');
        
        if ($newsSection.find('.newsItem').length > 1) {
          
          $newsSection.find('.owl-carousel').owlCarousel({
              loop:true,
              items:1,
              nav: false,
              dots: true,
              navText: ['<i class="fa fa-angle-left"></i>','<i class="fa fa-angle-right"></i>'],
              autoplay:true,
              autoplayTimeout:5000,
              autoplayHoverPause:false
          });
      
        } else {
          $newsSection.find('.owl-carousel').show();
        }
      

      
  //      $("#ca-container").contentcarousel();
