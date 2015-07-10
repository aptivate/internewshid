(function($) {
    /**
     * Class used to display flot charts.
     *
     * Flot charts are displayed in the specified element,
     * which should contain two data properties:
     *
     * - data-data: Containing the chart data
     * - data-options: Containing the chart options
     */
    function HidFlotChart(element) {
        var self = this;

        self.initialize = function() {
            // Set up the element
            self.$element = $(element);
            self.$container = self.$element.closest('.panel-body');

            // Read the element's data
            var data_values = self.$element.data();
            self.data = data_values['data'];
            self.options = data_values['options'];

            // Setup event handling
            $(window).resize(function(){
                self.resize();
            });
            self.resize();

            // And plot
            $.plot(self.$element, self.data, self.options);
        };

        /*
         * Resize the chart to the container's size.
         */
        self.resize = function() {
            self.$element.width(self.$container.width());
            self.$element.height(self.$container.height());
        };


        self.initialize();
    }

    $(document).ready(function() {
        $('.flot-chart').each(function() {
            HidFlotChart($(this));
        });
    });
})(jQuery);
