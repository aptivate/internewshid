$(document).ready(function() {
    $('#age-range-selector').multiselect({
        nonSelectedText: gettext('All Ages'),
        buttonClass: 'form-control',
        includeResetOption: true,
        numberDisplayed: 1
    });
    $('#feedback_type').multiselect({
        nonSelectedText: gettext('none'),
        buttonClass: 'form-control',
        includeResetOption: true,
        numberDisplayed: 2
    });



/* Disable for now, as multiple types in the Filter
   will need changes to the filtering search backend
    $('#feedback-type-selector').multiselect({
        nonSelectedText: gettext('All Types'),
        buttonClass: 'form-control',
        includeResetOption: true,
        numberDisplayed: 1
    });
*/
});
