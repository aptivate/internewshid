from data_layer import models


class Message(object):

    @classmethod
    def create(cls, message):
        models.Message(**message).save()


# TODO rename this class?
Item = Message
