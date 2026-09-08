import builtins

from panda3d.core import KeyboardButton


def is_down(key):
    base = getattr(builtins, 'base', None)
    if base is None or base.mouseWatcherNode is None:
        return False
    return base.mouseWatcherNode.isButtonDown(KeyboardButton.ascii_key(key.encode()))


def w_down():
    return is_down('w')


def a_down():
    return is_down('a')


def s_down():
    return is_down('s')


def d_down():
    return is_down('d')
