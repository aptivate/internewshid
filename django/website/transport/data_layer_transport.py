from data_layer.handlers import Message


def get_messages():
    return Message.list()


def create_message(message):
    Message.create(message)


def delete_item(message_id):
    Message.delete(message_id)


def delete_items(message_ids):
    Message.delete_items(message_ids)
