from data_layer import models


#TODO: delete all this
class Message(object):

    @classmethod
    def create(cls, message):
        models.Message(**message).save()

    @classmethod
    def list(cls):
        # TODO: I think we should probably use a DRF serializer here
        return models.Message.objects.values().iterator()

    @classmethod
    def delete(cls, message_id):
        models.Message.objects.filter(id=message_id).delete()

    @classmethod
    def delete_items(cls, message_ids):
        models.Message.objects.filter(id__in=message_ids).delete()

# TODO rename this class?
Item = Message
