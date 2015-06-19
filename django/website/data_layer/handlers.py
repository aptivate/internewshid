from data_layer import models


class Message(object):

    @classmethod
    def create(cls, message):
        models.Message(**message).save()

    @classmethod
    def list(cls):
        # TODO: I think we should probably use a DRF serializer here
        return models.Message.objects.values().iterator()
