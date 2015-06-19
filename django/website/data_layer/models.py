from django.db import models


class DataLayerModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class Message(DataLayerModel):
    body = models.TextField()
    timestamp = models.DateTimeField(null=True)
