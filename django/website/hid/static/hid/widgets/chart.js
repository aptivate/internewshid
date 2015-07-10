(function($) {
    /**
     * FlotChart model
     *
     * This contains the data and options of a
     * single flot chart.
     *
     */
    var FlotChart = Backbone.Model.extend({
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
    var FlotChartView = Backbone.View.extend({
        /* Create the view */
        initialize: function(options) {
            this.chart = options.chart;
            this.$container = this.$el.closest('.panel-body');
            $(window).on('resize', _.bind(this.resize, this));
        },

        /* Remove the view */
        remove: function() {
            $(window).off('resize', this.resize);
            this.$el.remove();
        },

        /* Render the chart */
        render: function() {
            this.resize();
            $.plot(
                this.$el,
                this.chart.get('data'), 
                this.chart.get('options')
            );
            return this;
        },

        /* Resize the chart */
        resize: function() {
            this.$el.width(this.$container.width());
            this.$el.height(this.$container.height());
        },
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
    $(document).ready(function() {
        $('.flot-chart').each(function() {
            var flot_chart = new FlotChart($(this).data());
            var flot_chart_view = new FlotChartView({
                el: this,
                chart: flot_chart
            });
            flot_chart_view.render();
        });
    });
})(jQuery);
