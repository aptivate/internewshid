/* shows loading spinner at the top of the page and is activated when 
 * user clicks on any link or button. This is needed for low bandwidth/slow 
 * connections where loading can take time */

jQuery(function(){
    jQuery('a, button, .btn').click(function() {
        jQuery('.spinner').toggleClass('active');
    });
});