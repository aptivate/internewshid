/**
 * Hide messages box after 5 seconds automatically with a 1 second fadeout
 */

jQuery(window).load(function(){
  setTimeout(function(){ 
      jQuery('.messages-box > ul').fadeOut(1000, 'swing');
      }, 5000);
});


