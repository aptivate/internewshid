import collections

from django.db import models
from jsonfield import JSONField

UPLOAD_CHOICES = (
    ('geopoll', 'Geopoll'),
)


def get_spreadsheet_choices():
    return [(p.profile['label'], p.profile['name']) for p
            in SheetProfile.objects.all()]


class SheetProfile(models.Model):
    label = models.CharField(max_length=256)
    profile = JSONField(
        load_kwargs={'object_pairs_hook': collections.OrderedDict})
