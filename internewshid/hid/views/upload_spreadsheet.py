from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import gettext, ungettext
from django.views.generic import FormView

from chn_spreadsheet.importer import Importer, SheetImportException

from ..forms.upload import UploadForm


class UploadSpreadsheetView(FormView):
    form_class = UploadForm
    template_name = "hid/upload.html"

    def get_success_url(self):
        return self.request.POST.get('next')

    def form_valid(self, form):
        data = form.cleaned_data
        source = data['source']
        uploaded_file = data['file']

        try:
            importer = Importer()
            (saved, skipped) = importer.store_spreadsheet(
                source, uploaded_file
            )
            all_messages = [
                gettext("Upload successful!"),
                ungettext("{0} entry has been added.",
                          "{0} entries have been added.",
                          saved).format(saved)
            ]

            if skipped > 0:
                all_messages.append(
                    ungettext("{0} duplicate entry was skipped.",
                              "{0} duplicate entries were skipped.",
                              skipped).format(skipped)
                )

            messages.success(self.request, ' '.join(all_messages))
        except SheetImportException as exc:
            msg = exc.message
            messages.error(self.request, msg)

        return HttpResponseRedirect(self.get_success_url())
