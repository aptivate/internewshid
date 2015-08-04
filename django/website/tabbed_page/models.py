from django.db import models
from jsonfield import JSONField


class TabbedPage(models.Model):
    name = models.CharField(
        max_length=128,
        unique=True
    )

    def __unicode__(self):
        return self.name


class Tab(models.Model):
    settings = JSONField(blank=True)
    view_name = models.CharField(max_length=128)
    page = models.ForeignKey(TabbedPage)
    name = models.CharField(max_length=128)
    default = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)
    label = models.CharField(max_length=128)

    def __unicode__(self):
        return self.label

    class Meta:
        unique_together = ('name', 'page')
