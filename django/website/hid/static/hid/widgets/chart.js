FlotChart = {
    models: [],
    views: []
};
(function($) {
    /**
     * FlotChart model
     *
     * This contains the data and options of a
     * single flot chart.
     *
     */
    FlotChart.model = Backbone.Model.extend({
        defaults: {
            data: [],
            options: {}
        }
    });

    /**
     * FlotChartView view
     *
     * Displays a single FlotChart model
     */
    FlotChart.view = Backbone.View.extend({
        /* Create the view */
        initialize: function(options) {
            this.chart = options.chart;
            this.$container = this.$el.closest('.panel-body');
            $(window).on('resize', _.bind(this.resize, this));
            this.$el.on('plothover', _.bind(this.tooltip, this));
        },

        /* Remove the view */
        remove: function() {
            $(window).off('resize', this.resize);
            this.$el.remove();
        },

        /* Render the chart */
        render: function() {
            var options = this.chart.get('options');
            var $legend_container = this.$el.siblings('.flot-legend');
            if ($legend_container.length > 0 && options['legend']) {
                options['legend']['container'] = $legend_container;
            }
            this.resize();
            $.plot(
                this.$el,
                this.chart.get('data'), 
                options
            );

            return this;
        },

        /* Resize the chart */
        resize: function() {
            if (this.$container.length == 0) {
                return;
            }
            var new_width = this.$container.width();
            var chart_parent_offset = this.$el.offset().top - this.$container.offset().top;
            var new_height = this.$container.height() - chart_parent_offset;
            this.$el.width(new_width);
            this.$el.height(new_height);
        },

        /* Display tooltip */
        tooltip: function(event, pos, item) {
            if (this.$tooltip) {
                this.$tooltip.remove();
                this.$tooltip = null;
            }
            if (item) {
                this.$tooltip = $('<div>');
                this.$tooltip.html(item.datapoint[0])
                    .addClass('flot-chart-tooltip')
                    .css({
                        position: 'absolute',
                        top: item.pageY - 10,
                        left: item.pageX + 10
                     });
                this.$tooltip.appendTo('body').fadeIn('fast');
            }
        }
    });

    /**
     * Create a flot chart for every matching element.
     *
     * The elements are execpted to have a class 'flot-chart'
     * and two data attributes:
     *
     *     data: flot data
     *     options: flot options
     */
    FlotChart.initialize = function() {
        $('.flot-chart').each(function() {
            var flot_chart = new FlotChart.model($(this).data());
            var flot_chart_view = new FlotChart.view({
                el: this,
                chart: flot_chart
            });
            flot_chart_view.render();
            FlotChart.models.push(flot_chart);
            FlotChart.views.push(flot_chart_view);
        });
    };
})(jQuery);
jQuery(document).ready(FlotChart.initialize);
