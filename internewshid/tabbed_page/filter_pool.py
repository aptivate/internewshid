from django.utils.translation import ugettext_lazy as _

_pool = {}


class MissingFilterError(Exception):
    pass


def register_filter(name, tab):
    global _pool
    _pool[name] = tab


def get_filter(name):
    global _pool

    try:
        return _pool[name]
    except KeyError:
        message = _("Filter named '{0}' has not been registered").format(name)

        raise MissingFilterError(message)


def clear_filters():
    # Currently only used in test code
    global _pool

    _pool = {}
