from mock import Mock, patch
import pytest

from ..templatetags.render_upload_form import render_upload_form

render_to_string_method = 'hid.templatetags.render_upload_form.render_to_string'


@pytest.mark.django_db
@patch(render_to_string_method)
def test_upload_form_source_attribute_set(mock_render):
    request = Mock()
    context = {'request': request}
    render_upload_form(context, 'rapidpro', None, None)

    _, kwargs = mock_render.call_args
    form = kwargs['context']['upload_form']

    assert form.initial.get('source') == 'rapidpro'


@pytest.mark.django_db
@patch(render_to_string_method)
def test_upload_form_next_url_attribute_set(mock_render):
    request = Mock()
    context = {'request': request}
    render_upload_form(context, 'rapidpro', '/view-edit/main/feedback/', None)

    _, kwargs = mock_render.call_args
    form = kwargs['context']['upload_form']

    assert form.initial.get('next') == '/view-edit/main/feedback/'


@pytest.mark.django_db
@patch(render_to_string_method)
def test_no_upload_form_when_source_not_set(mock_render):
    request = Mock()
    context = {'request': request}
    render_upload_form(context, None, None, None)

    _, kwargs = mock_render.call_args
    form = kwargs['context']['upload_form']

    assert form is None


@pytest.mark.django_db
@patch(render_to_string_method)
def test_type_label_passed_to_template(mock_render):
    request = Mock()
    context = {'request': request}
    render_upload_form(context, None, None, 'Feedback')

    _, kwargs = mock_render.call_args
    type_label = kwargs['context']['type_label']

    assert type_label == 'Feedback'


@pytest.mark.django_db
@patch(render_to_string_method)
def test_request_passed_to_template(mock_render):
    request = Mock()
    context = {'request': request}
    render_upload_form(context, None, None, None)

    _, kwargs = mock_render.call_args
    assert kwargs['request'] == request


@pytest.mark.django_db
@patch(render_to_string_method)
def test_template_used(mock_render):
    request = None
    context = {'request': request}
    render_upload_form(context, None, None, None)

    args, _ = mock_render.call_args
    assert args[0] == 'hid/upload_form.html'
