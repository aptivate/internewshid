from django.db import models


class DataLayerModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Message(DataLayerModel):
    body = models.TextField()
    timestamp = models.DateTimeField(null=True)

    def __unicode__(self):
        return "{}: '{}' @{}".format(
            self.id,
            self.body,
            self.timestamp
        )

# TODO: rename this class
Item = Message
