/**
 * Add a checkbox to select all entries to tables with a column containing
 * a checkbox.
 *
 * Usage:
 * - The th/td elements containing the checkbox must have
 *   a 'select_action' class. In Django tables this is done
 *   by naming the column select_action, eg.:
 *
 *   select_action = NamedCheckBoxColumn(accessor='id', verbose_name='Select')
 */
(function($) {
    $(document).ready(function() {

        // Select all rows
        $("#header-select").click(function(){
            var clicks = $(this).data('clicks');

            if (!clicks){
                // select all
                $( "tr" ).removeClass('selected');
                $(".select-item-id-checkbox input[type=checkbox]").prop( "checked", true );
                $( "tr" ).addClass('selected');
            }
            else{
                // select none
                $( "tr" ).removeClass('selected');
                $(".select-item-id-checkbox input[type=checkbox]").prop( "checked", false );
            }
            $(this).data("clicks", !clicks);
        });

        // Highlight single row on select
        $( ".select-item-id-checkbox input[type=checkbox]" ).click(function(e){
            $( e.target ).closest( "tr" ).toggleClass('selected');
        });

        // Table resizing
        var onDraggingCol = function(e){
            var thisTable = $(e.currentTarget); //reference to the resized table
            $(thisTable).find("th").addClass('resizing');
        }
        var onResized = function(e){
            $("th").removeClass('resizing');
        }
        $("table").colResizable({
            'postbackSafe':true,
            'liveDrag':true,
            'onDrag':onDraggingCol,
            'onResize':onResized,
            'minWidth':30
            }
        );

    });
})(jQuery);
