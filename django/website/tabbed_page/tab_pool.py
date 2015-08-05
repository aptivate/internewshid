_pool = {}


class MissingTabError(Exception):
    pass


def register_tab(name, tab):
    global _pool
    _pool[name] = tab


def get_tab(name):
    global _pool

    try:
        return _pool[name]
    except KeyError:
        raise MissingTabError()


def clear_tabs():
    # Currently only used in test code
    global _pool

    _pool = {}
