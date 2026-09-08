import builtins

from panda3d.core import ClockObject, TextNode, TransparencyAttrib
from direct.gui.DirectGui import DGG, DirectButton, DirectFrame
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


class SideMenu:
    def __init__(self, on_resume=None, on_restart=None, on_exit=None):
        base = getattr(builtins, 'base', None)
        if base is None:
            raise RuntimeError('SideMenu requires a ShowBase instance to exist first.')

        self._on_resume = on_resume or self.hide
        self._on_restart = on_restart or self._restart_placeholder
        self._on_exit = on_exit or base.userExit

        self.width = 0.55
        self.hidden_x = -self.width - 0.01
        self.panel = DirectFrame(
            parent=base.a2dLeftCenter,
            frameSize=(0.0, self.width, -0.85, 0.85),
            frameColor=(0.06, 0.08, 0.12, 0.88),
            relief=DGG.FLAT,
            state=DGG.NORMAL,
        )
        self.panel.setTransparency(TransparencyAttrib.MAlpha)
        self.panel.setPos(self.hidden_x, 0, 0)

        self.title = OnscreenText(
            parent=self.panel,
            text='CaseCode',
            pos=(0.06, 0.72),
            scale=0.07,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=False,
        )
        self.resume_button = self._entry('Resume', 0, self._on_resume)
        self.restart_button = self._entry('Restart', 1, self._on_restart)
        self.exit_button = self._entry('Exit', 2, self._on_exit)

        self._target_x = self.hidden_x
        self._task = None

    def _entry(self, label, index, command):
        button = DirectButton(
            parent=self.panel,
            pos=(0.0, 0, 0.45 - index * 0.2),
            text=label,
            text_scale=0.05,
            text_align=TextNode.ALeft,
            text_fg=(0.78, 0.81, 0.88, 1),
            relief=DGG.FLAT,
            frameSize=(0.0, 0.47, -0.06, 0.07),
            frameColor=(1, 1, 1, 0),
            command=command,
        )
        button.setTransparency(TransparencyAttrib.MAlpha)
        return button

    def _restart_placeholder(self):
        print('[SideMenu] Restart pressed — no restart logic yet.')

    def toggle(self):
        if self._target_x < 0.0:
            self.show()
        else:
            self.hide()

    def show(self):
        self._animate_to(0.0)

    def hide(self):
        self._animate_to(self.hidden_x)

    def _animate_to(self, target):
        self._target_x = target
        if self._task is None:
            self._task = builtins.base.taskMgr.add(self._update, 'side_menu_slide')

    def _update(self, task):
        dt = min(ClockObject.getGlobalClock().getDt(), 0.05)
        current = self.panel.getX()
        moved = current + (self._target_x - current) * min(1.0, dt * 10)
        if abs(self._target_x - moved) < 0.001:
            self.panel.setX(self._target_x)
            self._task = None
            return task.done
        self.panel.setX(moved)
        return task.cont
