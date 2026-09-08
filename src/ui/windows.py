import builtins

from panda3d.core import TextNode
from direct.gui.DirectGui import DGG, DirectFrame
from direct.gui.OnscreenText import OnscreenText

from src.ui.buttons import make_button


class StartWindow:
    def __init__(self, on_play=None, on_settings=None, on_exit=None):
        base = getattr(builtins, 'base', None)
        if base is None:
            raise RuntimeError('StartWindow requires a ShowBase instance to exist first.')

        self._on_play = on_play or self.hide
        self._on_settings = on_settings or self._settings_placeholder
        self._on_exit = on_exit or base.userExit

        # Solid background covering the whole window (render2d ignores aspect ratio).
        self.background = DirectFrame(
            parent=base.render2d,
            frameSize=(-1, 1, -1, 1),
            frameColor=(0.07, 0.08, 0.11, 1),
            state=DGG.NORMAL,
        )

        # Everything else lives on aspect2d so it never stretches.
        self.title = OnscreenText(
            parent=base.aspect2d,
            text='CaseCode',
            pos=(0, 0.55),
            scale=0.16,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter,
            mayChange=False,
        )

        self.play_button = make_button(
            'Play', base.aspect2d, (0, 0, 0.05), command=self._on_play, style='primary')
        self.settings_button = make_button(
            'Settings', base.aspect2d, (0, 0, -0.2), command=self._on_settings, style='neutral')
        self.exit_button = make_button(
            'Exit', base.aspect2d, (0, 0, -0.45), command=self._on_exit, style='danger')

        self._nodes = [self.background, self.title, self.play_button,
                       self.settings_button, self.exit_button]

    def _settings_placeholder(self):
        print('[StartWindow] Settings pressed — no settings window yet.')

    def show(self):
        for node in self._nodes:
            node.show()

    def hide(self):
        for node in self._nodes:
            node.hide()

    def destroy(self):
        for node in self._nodes:
            node.destroy()
