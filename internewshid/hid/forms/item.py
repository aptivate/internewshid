from django import forms

import transport
from data_layer.models import Item
from hid.constants import ITEM_TYPE_CATEGORY


class AddEditItemForm(forms.Form):
    id = forms.CharField(
        widget=forms.HiddenInput,
        required=True
    )
    body = forms.CharField(
        widget=forms.Textarea,
        required=True
    )
    translation = forms.CharField(
        widget=forms.Textarea,
        required=False
    )
    location = forms.CharField(
        widget=forms.Textarea,
        required=False
    )
    gender = forms.CharField(
        widget=forms.Textarea,
        required=False
    )
    age = forms.CharField(
        widget=forms.Textarea,
        required=False
    )
    enumerator = forms.CharField(
        widget=forms.Textarea,
        required=False
    )
    source = forms.CharField(
        widget=forms.Textarea,
        required=False
    )
    timestamp = forms.DateTimeField(required=True)
    next = forms.CharField(
        widget=forms.HiddenInput,
        required=True
    )
    tags = forms.CharField(
        widget=forms.TextInput,
        required=False
    )

    def __init__(self, item_type, *args, **kwargs):
        """ Add extra fields depending on item_type """
        super(AddEditItemForm, self).__init__(*args, **kwargs)

        if item_type in ITEM_TYPE_CATEGORY:
            terms = transport.terms.list(
                taxonomy=ITEM_TYPE_CATEGORY[item_type]
            )
            choices = (('', '-----'),)
            choices += tuple((t['name'], t['name']) for t in terms)
            self.fields['category'] = forms.ChoiceField(
                choices=choices, required=False
            )

        choices = (('', '-----'),)
        choices += Item.FEEDBACK_TYPE_CHOICES
        self.fields['feedback_type'] = forms.ChoiceField(
            choices=choices,
            required=False,
            widget=forms.RadioSelect()
        )
