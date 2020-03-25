from django import forms

import transport
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
    sub_location = forms.CharField(
        widget=forms.Textarea,
        required=False
    )
    language = forms.CharField(
        widget=forms.Textarea,
        required=False
    )
    risk = forms.CharField(
        widget=forms.Textarea,
        required=False
    )
    gender = forms.CharField(
        widget=forms.Textarea,
        required=False
    )
    contributor = forms.CharField(
        widget=forms.Textarea,
        required=False
    )
    collection_type = forms.CharField(
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

    def __init__(self, *args, **kwargs):
        feedback_disabled = kwargs.pop('feedback_disabled', False)

        super(AddEditItemForm, self).__init__(*args, **kwargs)

        self.fields['body'].disabled = feedback_disabled

        self._maybe_add_category_field()
        self._maybe_add_feedback_type_field()
        self._maybe_add_age_range_field()

    def _maybe_add_category_field(self):
        # This used to be more flexible in that we had partial
        # support for per- item/feedback/message type categories
        # but it was never fully implemented and it was confusing
        # so for now we have one set of categories for all types
        choices = self._get_category_choices()

        if choices is not None:
            self.fields['category'] = forms.ChoiceField(
                choices=choices, required=False
            )

    def _get_category_choices(self):
        return self._get_term_choices(ITEM_TYPE_CATEGORY['all'])

    def _maybe_add_feedback_type_field(self):
        choices = self._get_feedback_type_choices()

        if choices is not None:
            self.fields['feedback_type'] = forms.ChoiceField(
                choices=choices,
                required=False,
                widget=forms.RadioSelect()
            )

    def _get_feedback_type_choices(self):
        return self._get_term_choices('item-types')

    def _maybe_add_age_range_field(self):
        choices = self._get_age_range_choices()

        if choices is not None:
            self.fields['age_range'] = forms.ChoiceField(
                choices=choices,
                required=False,
                widget=forms.RadioSelect()
            )

    def _get_age_range_choices(self):
        return self._get_term_choices('age-ranges')

    def _get_term_choices(self, taxonomy):
        terms = transport.terms.list(
            taxonomy=taxonomy
        )

        if len(terms) > 0:
            sorted_terms = sorted(terms, key=lambda k: k['long_name'])

            choices = (('', '-----'),)
            choices += tuple((t['name'], t['long_name']) for t in sorted_terms)

            return choices

        return None
