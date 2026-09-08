import json
import os

DEFAULTS = {
    'camera_speed': 5,
    'zoom_speed': 5,
    'invert_drag_y': False,
}

_values = dict(DEFAULTS)
_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')


def get(key):
    return _values[key]


def set(key, value):
    _values[key] = value


def load():
    global _values
    if not os.path.exists(_path):
        return
    try:
        with open(_path) as file:
            stored = json.load(file)
    except (OSError, ValueError):
        return
    for key in DEFAULTS:
        if key in stored:
            _values[key] = stored[key]


def save():
    try:
        with open(_path, 'w') as file:
            json.dump(_values, file, indent=2)
    except OSError:
        pass
