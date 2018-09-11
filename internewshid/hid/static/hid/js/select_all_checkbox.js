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
        var selectors = {
            td_input : 'form td.select_item input[type="checkbox"]',
            th_select : 'form th.select_item'
        };

        function addCheckbox(selector, check_id_base) {
            $(selector).each(function(i, column_header) {
                var input_id = check_id_base + '-' + i;
                var check = $('<input>', {
                        type: 'checkbox',
                        id: input_id
                    });
                $(column_header).html("")
                           .append(check);
            });
        }

        function toggleSelection(e) {
            var checked = $(e.target).prop("checked");
            $(selectors.td_input).prop("checked", checked);
        }

        function setSelectAll(e) {
            var checked = $(selectors.td_input + ':checked').length,
                all = $(selectors.td_input).length,
                checked_all = all === checked;

            $(selectors.th_select + ' input').prop("checked", checked_all);
        }

        function init() {
            addCheckbox(selectors.th_select, 'select-all-items');

            $(selectors.th_select + ' input').on('change', toggleSelection);
            $(selectors.td_input).on('change', setSelectAll);
        }

        init();
    });
})(jQuery);
