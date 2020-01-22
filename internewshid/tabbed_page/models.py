from django.db import models

from jsonfield import JSONField


class TabbedPage(models.Model):
    name = models.SlugField(
        max_length=128,
        unique=True
    )

    def __unicode__(self):
        return self.name


class TabInstance(models.Model):
    settings = JSONField(blank=True)
    tab_type = models.CharField(max_length=128)
    page = models.ForeignKey(TabbedPage, related_name='tabs',
                             on_delete=models.CASCADE)
    name = models.SlugField(max_length=128, unique=False)
    default = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)
    label = models.CharField(max_length=128)

    def __unicode__(self):
        return self.label

    class Meta:
        unique_together = ('name', 'page')
