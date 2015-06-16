from django import forms


UPLOAD_CHOICES = (
    ('geopoll', 'Geopoll'),
)


def get_spreadsheet_choices():
    return UPLOAD_CHOICES


class UploadForm(forms.Form):
    source = forms.ChoiceField(choices=get_spreadsheet_choices,
                               widget=forms.HiddenInput,
                               required=True)
    file = forms.FileField()
