from data_layer.handlers import Message


def get_messages():
    return Message.list()


def create_message(message):
    Message.create(message)
