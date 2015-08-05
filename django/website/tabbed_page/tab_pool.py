_pool = {}


def register_tab(name, tab):
    global _pool
    _pool[name] = tab


def get_tab(name):
    global _pool

    return _pool[name]
