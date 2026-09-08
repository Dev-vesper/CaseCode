import builtins

from configs.game import settings as game_settings
from src.ui.windows import SettingsWindow


class SettingsMenu:
    def __init__(self, on_close=None):
        base = getattr(builtins, 'base', None)
        if base is None:
            raise RuntimeError('SettingsMenu requires a ShowBase instance to exist first.')

        game_settings.load()
        self._on_close = on_close
        self.window = SettingsWindow(
            on_back=self.close,
            on_change=self._change,
            values={key: game_settings.get(key) for key in game_settings.DEFAULTS},
        )

    def _change(self, key, value):
        game_settings.set(key, value)

    def open(self):
        self.window.show()

    def close(self):
        game_settings.save()
        self.window.hide()
        if self._on_close:
            self._on_close()
