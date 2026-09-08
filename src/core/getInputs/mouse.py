import builtins

_scroll = 0
_bound = False


def init():
    global _bound
    base = getattr(builtins, 'base', None)
    if base is None or _bound:
        return
    base.accept('wheel_up', _on_wheel, [1])
    base.accept('wheel_down', _on_wheel, [-1])
    _bound = True


def _on_wheel(direction):
    global _scroll
    _scroll += direction


def scroll_delta():
    global _scroll
    delta = _scroll
    _scroll = 0
    return delta
