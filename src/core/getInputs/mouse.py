import builtins

from panda3d.core import MouseButton

_scroll = 0
_bound = False
_middle_last = None


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


def middle_down():
    base = getattr(builtins, 'base', None)
    if base is None or base.mouseWatcherNode is None:
        return False
    return base.mouseWatcherNode.isButtonDown(MouseButton.two())


def middle_drag_delta():
    global _middle_last
    base = getattr(builtins, 'base', None)
    if base is None or base.mouseWatcherNode is None:
        return 0.0, 0.0
    watcher = base.mouseWatcherNode
    if not middle_down() or not watcher.hasMouse():
        _middle_last = None
        return 0.0, 0.0
    x, y = watcher.getMouseX(), watcher.getMouseY()
    if _middle_last is None:
        _middle_last = (x, y)
        return 0.0, 0.0
    delta = (x - _middle_last[0], y - _middle_last[1])
    _middle_last = (x, y)
    return delta
