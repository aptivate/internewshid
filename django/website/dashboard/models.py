from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
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
            MaxValueValidator(11, 'column must be between 0 and 11')
        ]
    )
    width = models.PositiveIntegerField(
        default=12,
        validators=[
            MinValueValidator(1, 'width must be between 1 and 12'),
            MaxValueValidator(12, 'width must be between 1 and 12')
        ]
    )
    height = models.CharField(
        max_length=6,
        default='medium',
        choices=(
            ('small', 'Small'),
            ('medium', 'Medium'),
            ('tall', 'Tall')
        )
    )
    settings = JSONField(blank=True)

    def __unicode__(self):
        return "Instance of {}".format(self.widget_type)
