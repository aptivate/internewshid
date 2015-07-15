/**
 * Hide messages box after 3 seconds automatically
 */

jQuery(window).load(function(){
  setTimeout(function(){ 
      jQuery('.messages-box > ul').fadeOut(3000, 'swing');
      }, 3000);
});


