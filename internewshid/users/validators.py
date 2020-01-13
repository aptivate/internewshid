from datetime import date

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


def year_to_now(value):
    try:
        year = int(value)
    except ValueError:
        raise ValidationError(_('{0} is not a number').format(value))
    today = date.today()
    if year < 1900 or year >= today.year:
        raise ValidationError(
            _('{0} is not a number between 1900 and {1}').format(year, today.year))
