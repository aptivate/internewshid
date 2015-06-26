from data_layer import models


class Message(object):

    @classmethod
    def create(cls, message):
        models.Message(**message).save()

    @classmethod
    def list(cls):
        # TODO: probably use a DRF serializer here instead of .values()?
        return models.Message.objects.values().iterator()


# TODO rename this class?
Item = Message
