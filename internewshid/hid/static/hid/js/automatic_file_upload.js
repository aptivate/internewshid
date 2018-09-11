/**
 * Modify file upload button behaviour to allow us to:
 * - Use own markup for file buttons (eg. a tags);
 * - Auto-submit form on file selection.
 *
 * Usage:
 * - The form element should have a 'auto-upload-file' class;
 * - The upload button replacement should have an 'upload-button' class
 *   (optional, we can also use the normal upload button).
 * - The file input tag should be a descendant of a .form-group element
 *   (optional, this will be hidden if we have a button replacement).
 *
 * This is progressive enhancement, so the upload-button should be hidden
 * to be begin with, and will only be displayed if the javascript executes.
 *
 * Note that this will only work if the form has one file upload element.
 *
 */
(function($){
    $(document).ready(function() {
        $('.auto-upload-file').each(function() {
            var $form = $(this);
            var $button = $('.upload-button', $form);
            var $file_input = $('[type="file"]', $form);
            var $input_group = $file_input.closest('.form-group');

            // Hide the file input group and show the alternative button.
            if ($button.length > 0) {
                $input_group.hide();
                $button.show();
            }

            // Auto-submit
            $file_input.on('change', function(e) {
                e.preventDefault();
                $form.submit();
            });

            // Alternative upload button
            $button.on('click', function(e) {
                e.preventDefault();
                $file_input.click();
            });
        });
    });
})(jQuery);
