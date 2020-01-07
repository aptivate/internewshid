from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from jsonfield import JSONField


class Dashboard(models.Model):
    """ Model to represent a dashboard.

    A Dashboard is defined by its name, and
    a list of widget instances.
    """
    name = models.CharField(
        max_length=128,
        unique=True
    )

    def __unicode__(self):
        return self.name


class WidgetInstance(models.Model):
    """ Model to represent an instance of a widget.

    A WidgetInstance is defined by its widget type,
    widget settings (stored as a JSON string),
    the dashboard the instance is associated with,
    and the position within that dashboard (row,
    column, width)
    """
    dashboard = models.ForeignKey(Dashboard)
    widget_type = models.CharField(max_length=128)
    row = models.PositiveIntegerField(default=0)
    column = models.PositiveIntegerField(
        default=0,
        validators=[
            MaxValueValidator(11, _("column must be between 0 and 11"))
        ]
    )
    width = models.PositiveIntegerField(
        default=12,
        validators=[
            MinValueValidator(1, _("width must be between 1 and 12")),
            MaxValueValidator(12, _("width must be between 1 and 12"))
        ]
    )
    height = models.CharField(
        max_length=6,
        default='medium',
        choices=(
            ('small', _("Small")),
            ('medium', _("Medium")),
            ('tall', _("Tall"))
        )
    )
    settings = JSONField(blank=True)

    def __unicode__(self):
        return _("Instance of {}").format(self.widget_type)
