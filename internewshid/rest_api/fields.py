from django.utils import six
from django.utils.dateparse import parse_datetime

from rest_framework import serializers


class IgnoreMicrosecondsDateTimeField(serializers.DateTimeField):
    def to_internal_value(self, value):
        """Truncate microseconds from the timestamp field

        MySQL < 5.6 does not store microseconds for the
        timestamp field so we need to remove these for the
        UniqueTogether validator in the ItemSerializer to
        work properly.

        This will not be required when we're using MySQL >= 5.6
        everywhere.
        """
        if isinstance(value, six.string_types):
            try:
                parsed = parse_datetime(value)
                value = parsed.replace(microsecond=0)

            except (ValueError, TypeError):
                pass

        return super(IgnoreMicrosecondsDateTimeField, self).to_internal_value(value)
