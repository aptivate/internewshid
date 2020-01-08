from mock import patch

from ..forms.item import AddEditItemForm


@patch.object(AddEditItemForm, '_get_category_choices')
@patch.object(AddEditItemForm, '_get_feedback_type_choices')
@patch.object(AddEditItemForm, '_get_age_range_choices')
def test_form_does_not_have_category_field_if_not_defined(
    age_range_choices,
    feedback_choices,
    category_choices
):
    category_choices.return_value = None
    feedback_choices.return_value = None
    age_range_choices.return_value = None

    form = AddEditItemForm()
    assert 'category' not in form.fields


@patch.object(AddEditItemForm, '_get_category_choices')
@patch.object(AddEditItemForm, '_get_feedback_type_choices')
@patch.object(AddEditItemForm, '_get_age_range_choices')
def test_form_has_category_field_if_categories_defined(
    age_range_choices,
    feedback_choices,
    category_choices
):
    age_range_choices.return_value = None
    feedback_choices.return_value = None

    category_choices.return_value = (('', '-----'), ('wash', 'WASH'),)
    form = AddEditItemForm()
    assert 'category' in form.fields


@patch.object(AddEditItemForm, '_get_category_choices')
@patch.object(AddEditItemForm, '_get_feedback_type_choices')
@patch.object(AddEditItemForm, '_get_age_range_choices')
def test_form_does_not_have_feedback_types_if_not_defined(
    age_range_choices,
    feedback_choices,
    category_choices
):
    age_range_choices.return_value = None
    category_choices.return_value = None
    feedback_choices.return_value = None
    form = AddEditItemForm()

    assert 'feedback_type' not in form.fields


@patch.object(AddEditItemForm, '_get_category_choices')
def test_form_has_feedback_types_if_defined(
    category_choices
):
    with patch('hid.forms.item.transport.terms.list') as term_list:
        term_list.return_value = [
            {
                'taxonomy': 'item-types',
                'name': 'rumour',
                'long_name': 'Rumour'
            },
            {
                'taxonomy': 'item-types',
                'name': 'question',
                'long_name': 'Question'
            },
            {
                'taxonomy': 'item-types',
                'name': 'concern',
                'long_name': 'Concern'
            },
        ]
        expected_choices = [
            ('', '-----'),
            ('concern', 'Concern'),
            ('question', 'Question'),
            ('rumour', 'Rumour')
        ]

        form = AddEditItemForm()

        assert 'feedback_type' in form.fields
        assert form.fields['feedback_type'].choices == expected_choices


@patch.object(AddEditItemForm, '_get_category_choices')
@patch.object(AddEditItemForm, '_get_feedback_type_choices')
@patch.object(AddEditItemForm, '_get_age_range_choices')
def test_form_does_not_have_age_ranges_if_not_defined(
    age_range_choices,
    feedback_choices,
    category_choices
):
    category_choices.return_value = None
    feedback_choices.return_value = None
    age_range_choices.return_value = None
    form = AddEditItemForm()

    assert 'age_ranges' not in form.fields


@patch.object(AddEditItemForm, '_get_category_choices')
def test_form_has_age_ranges_if_defined(
    category_choices
):
    with patch('hid.forms.item.transport.terms.list') as term_list:
        term_list.return_value = [
            {
                'taxonomy': 'age-ranges',
                'name': 'Age 11-14 yrs',
                'long_name': 'Age 11-14 yrs'
            },
            {
                'taxonomy': 'age-ranges',
                'name': 'Age 15-18 yrs',
                'long_name': 'Age 15-18 yrs'
            },
        ]
        expected_choices = [
            ('', '-----'),
            ('Age 11-14 yrs', 'Age 11-14 yrs'),
            ('Age 15-18 yrs', 'Age 15-18 yrs'),
        ]

        form = AddEditItemForm()

        assert 'age_range' in form.fields
        assert form.fields['age_range'].choices == expected_choices


@patch.object(AddEditItemForm, '_get_feedback_type_choices')
def test_form_category_has_expected_choices(feedback_choices):
    item_type_category = {
        'all': 'some-taxonomy'
    }
    with patch.dict('hid.forms.item.ITEM_TYPE_CATEGORY', item_type_category):
        with patch('hid.forms.item.transport.terms.list') as term_list:
            term_list.return_value = [
                {
                    'taxonomy': 'some-taxonomy',
                    'name': 'name1',
                    'long_name': 'long name one'
                },
                {
                    'taxonomy': 'some-taxonomy',
                    'name': 'name2',
                    'long_name': 'long name two'
                },
            ]
            expected_choices = [
                ('', '-----'),
                ('name1', 'long name one'),
                ('name2', 'long name two')
            ]
            form = AddEditItemForm()
            assert 'category' in form.fields
            assert form.fields['category'].choices == expected_choices


@patch.object(AddEditItemForm, '_get_category_choices')
@patch.object(AddEditItemForm, '_get_feedback_type_choices')
@patch.object(AddEditItemForm, '_get_age_range_choices')
def test_category_field_is_not_required(
    age_range_choices,
    feedback_choices,
    category_choices
):
    age_range_choices.return_value = None
    feedback_choices.return_value = None
    category_choices.return_value = (('', '-----'), ('wash', 'WASH'),)

    form = AddEditItemForm()

    assert not form.fields['category'].required
