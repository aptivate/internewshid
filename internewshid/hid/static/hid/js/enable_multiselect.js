$(document).ready(function() {
    $('#age-range-selector').multiselect({
        nonSelectedText: gettext('All Ages'),
        buttonClass: 'form-control',
        includeResetOption: true,
        numberDisplayed: 1
    });
    $('#feedback-type-selector').multiselect({
        nonSelectedText: gettext('All Types'),
        buttonClass: 'form-control',
        includeResetOption: true,
        numberDisplayed: 1
    });
});
