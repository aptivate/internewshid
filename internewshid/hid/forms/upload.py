from django import forms

from chn_spreadsheet.models import get_spreadsheet_choices


class UploadForm(forms.Form):
    source = forms.ChoiceField(choices=get_spreadsheet_choices,
                               widget=forms.HiddenInput,
                               required=True)
    next = forms.CharField(widget=forms.HiddenInput,
                           required=True)
    file = forms.FileField()
