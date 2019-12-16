from django import forms

from chn_spreadsheet.models import get_spreadsheet_choices


class UploadForm(forms.Form):
    collection_type = forms.ChoiceField(
        choices=get_spreadsheet_choices,
        required=True,
        widget=forms.RadioSelect,
    )
    next = forms.CharField(
        widget=forms.HiddenInput,
        required=True
    )
    file = forms.FileField()
