from data_layer.handlers import Message


def get_messages():
    return Message.list()


def store_message(message):
    Message.create(message)
