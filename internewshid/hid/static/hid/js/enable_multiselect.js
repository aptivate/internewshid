$(document).ready(function() {
    $('#age-range-selector').multiselect({
        nonSelectedText: gettext('All Ages'),
        buttonClass: 'form-control',
        includeResetOption: true,
        numberDisplayed: 1
    });
});
