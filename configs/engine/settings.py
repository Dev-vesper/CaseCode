import ctypes

FULLSCREEN = True


def screen_size():
    try:
        x11 = ctypes.cdll.LoadLibrary('libX11.so.6')
        x11.XOpenDisplay.restype = ctypes.c_void_p
        x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
        x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
        x11.XDefaultScreen.argtypes = [ctypes.c_void_p]
        x11.XDisplayWidth.argtypes = [ctypes.c_void_p, ctypes.c_int]
        x11.XDisplayHeight.argtypes = [ctypes.c_void_p, ctypes.c_int]
        display = x11.XOpenDisplay(None)
        if not display:
            return None
        screen = x11.XDefaultScreen(display)
        size = (x11.XDisplayWidth(display, screen), x11.XDisplayHeight(display, screen))
        x11.XCloseDisplay(display)
        return size
    except OSError:
        return None
