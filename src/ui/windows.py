import builtins
import math

from panda3d.core import ClockObject, PNMImage, TextNode, Texture, TransparencyAttrib
from direct.gui.DirectGui import DGG, DirectButton, DirectFrame
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText

_ACCENT = (0.0, 1.0, 0.96)
_REC_RED = (1.0, 0.23, 0.19)
_IDLE_TEXT = (0.55, 0.60, 0.69)
_FADE = 0.35

_FONT_PATHS = {
    'regular': 'assets/fonts/JetBrainsMono-Regular.ttf',
    'bold': 'assets/fonts/JetBrainsMono-Bold.ttf',
}
_FONT_CACHE = {}


def _font(name):
    if name not in _FONT_CACHE:
        try:
            _FONT_CACHE[name] = builtins.loader.loadFont(_FONT_PATHS[name])
        except Exception:
            _FONT_CACHE[name] = None
    return _FONT_CACHE[name]


_OVERLAY_CACHE = None


def _overlay_texture():
    global _OVERLAY_CACHE
    if _OVERLAY_CACHE is not None:
        return _OVERLAY_CACHE
    width, height = 400, 225
    image = PNMImage(width, height, 4)
    for y in range(height):
        ny = (y + 0.5) / height * 2.0 - 1.0
        for x in range(width):
            nx = (x + 0.5) / width * 2.0 - 1.0
            vignette = min(1.0, math.sqrt(nx * nx + ny * ny) / math.sqrt(2.0))
            grid = 0.028 if x % 25 == 0 or y % 25 == 0 else 0.0
            noise = (((x * 1234567 + y * 890123) % 1000) / 1000.0 - 0.5) * 0.016
            image.setXel(x, y,
                         max(0.0, 0.048 + grid + noise),
                         max(0.0, 0.054 + grid + noise),
                         max(0.0, 0.088 + grid + noise))
            image.setAlpha(x, y, 0.74 + 0.14 * vignette)
    texture = Texture('menu_overlay')
    texture.load(image)
    _OVERLAY_CACHE = texture
    return texture


class StartWindow:
    def __init__(self, on_play=None, on_settings=None, on_exit=None):
        base = getattr(builtins, 'base', None)
        if base is None:
            raise RuntimeError('StartWindow requires a ShowBase instance to exist first.')

        self._on_play = on_play or self.hide
        self._on_settings = on_settings or self._settings_placeholder
        self._on_exit = on_exit or base.userExit

        self._t = 0.0
        self._task = None
        self._hover = [False, False, False]
        self._k = [0.0, 0.0, 0.0]

        self.overlay = OnscreenImage(image=_overlay_texture(), parent=base.render2d)
        self.overlay.setTransparency(TransparencyAttrib.MAlpha)

        self.title = OnscreenText(
            parent=base.aspect2d,
            text='CASECODE',
            font=_font('bold'),
            pos=(-0.62, 0.35),
            scale=0.105,
            fg=(0.93, 0.95, 0.98, 1),
            align=TextNode.ALeft,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.008, 0.008),
            mayChange=True,
        )

        cursor_x = -0.62 + self.title.textNode.getWidth() * 0.105 + 0.022
        self.cursor = DirectFrame(
            parent=base.aspect2d,
            frameSize=(0, 0.05, 0, 0.095),
            frameColor=(_ACCENT[0], _ACCENT[1], _ACCENT[2], 1),
            pos=(cursor_x, 0, 0.3025),
            relief=DGG.FLAT,
        )
        self.cursor.setTransparency(TransparencyAttrib.MAlpha)

        self.tagline = OnscreenText(
            parent=base.aspect2d,
            text='A GOD-VIEW PROGRAMMING PUZZLE',
            font=_font('regular'),
            pos=(-0.62, 0.275),
            scale=0.026,
            fg=(0.42, 0.47, 0.56, 1),
            align=TextNode.ALeft,
            mayChange=False,
        )

        self.rec_dot = DirectFrame(
            parent=base.aspect2d,
            frameSize=(-0.012, 0.012, -0.012, 0.012),
            frameColor=(_REC_RED[0], _REC_RED[1], _REC_RED[2], 1),
            pos=(-0.608, 0, 0.74),
            relief=DGG.FLAT,
        )
        self.rec_dot.setTransparency(TransparencyAttrib.MAlpha)
        self.rec_text = OnscreenText(
            parent=base.aspect2d,
            text='REC',
            font=_font('bold'),
            pos=(-0.575, 0.74),
            scale=0.03,
            fg=(_REC_RED[0], _REC_RED[1], _REC_RED[2], 1),
            align=TextNode.ALeft,
            mayChange=False,
        )

        self.version = OnscreenText(
            parent=base.aspect2d,
            text='v0.1.0',
            font=_font('regular'),
            pos=(-0.62, -0.84),
            scale=0.026,
            fg=(0.42, 0.47, 0.56, 1),
            align=TextNode.ALeft,
            mayChange=False,
        )

        self._items = []
        self._labels = []
        self._bars = []
        specs = [('PLAY', self._on_play, 0.09),
                 ('SETTINGS', self._on_settings, -0.02),
                 ('EXIT', self._on_exit, -0.13)]
        for index, (label, command, z) in enumerate(specs):
            bar = DirectFrame(
                parent=base.aspect2d,
                frameSize=(0, 0.016, -0.012, 0.030),
                frameColor=(_ACCENT[0], _ACCENT[1], _ACCENT[2], 1),
                pos=(-0.63, 0, z),
                relief=DGG.FLAT,
            )
            bar.setTransparency(TransparencyAttrib.MAlpha)
            bar.setSx(0.001)

            item = DirectButton(
                parent=base.aspect2d,
                pos=(-0.60, 0, z),
                relief=DGG.FLAT,
                frameSize=(0.0, 0.45, -0.045, 0.055),
                frameColor=(1, 1, 1, 0),
                pressEffect=0,
                command=command,
            )
            item.setTransparency(TransparencyAttrib.MAlpha)
            item.bind(DGG.ENTER, self._enter, extraArgs=[index])
            item.bind(DGG.EXIT, self._exit, extraArgs=[index])

            text = OnscreenText(
                parent=base.aspect2d,
                text=label,
                font=_font('regular'),
                pos=(-0.60, z),
                scale=0.042,
                fg=(1, 1, 1, 1),
                align=TextNode.ALeft,
                mayChange=True,
            )

            self._items.append(item)
            self._labels.append(text)
            self._bars.append(bar)

        self.play_button = self._items[0]
        self.settings_button = self._items[1]
        self.exit_button = self._items[2]

        self._nodes = [self.overlay, self.title, self.cursor, self.tagline,
                       self.rec_dot, self.rec_text, self.version,
                       *self._items, *self._labels, *self._bars]

        for node in self._nodes:
            node.setAlphaScale(0.0)

        self._start_task()

    def _settings_placeholder(self):
        print('[StartWindow] Settings pressed — no settings window yet.')

    def _enter(self, index, event=None):
        self._hover[index] = True

    def _exit(self, index, event=None):
        self._hover[index] = False

    def _fade_amount(self, start):
        x = max(0.0, min(1.0, (self._t - start) / _FADE))
        return 1.0 - (1.0 - x) ** 3

    def _fade_node(self, node, start):
        node.setAlphaScale(self._fade_amount(start))

    def _update(self, task):
        dt = min(ClockObject.getGlobalClock().getDt(), 0.05)
        t = self._t = self._t + dt

        if t < 1.2:
            self._fade_node(self.overlay, 0.0)
            self._fade_node(self.title, 0.0)
            self._fade_node(self.tagline, 0.10)
            self._fade_node(self.rec_dot, 0.50)
            self._fade_node(self.rec_text, 0.50)
            self._fade_node(self.version, 0.55)

        self.cursor.setAlphaScale(
            self._fade_amount(0.0) * (0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 4))))

        rec_pulse = 0.5 + 0.5 * math.sin(t * 2.6)
        self.rec_dot.setAlphaScale(self._fade_amount(0.50) * (0.45 + 0.55 * rec_pulse))
        self.rec_text.setAlphaScale(
            self._fade_amount(0.50) * (0.70 + 0.30 * (0.5 + 0.5 * math.sin(t * 2.6 + 0.9))))

        starts = (0.16, 0.24, 0.32)
        for index in range(3):
            k = self._k[index]
            target = 1.0 if self._hover[index] else 0.0
            if k != target:
                k = k + (target - k) * min(1.0, dt * 14)
                if abs(target - k) < 0.002:
                    k = target
                self._k[index] = k
            fade = self._fade_amount(starts[index])
            if k == target and fade >= 1.0:
                continue
            shift = 0.012 * k
            r = _IDLE_TEXT[0] + (1.0 - _IDLE_TEXT[0]) * k
            g = _IDLE_TEXT[1] + (1.0 - _IDLE_TEXT[1]) * k
            b = _IDLE_TEXT[2] + (1.0 - _IDLE_TEXT[2]) * k
            self._labels[index].setColorScale(r, g, b, fade)
            self._bars[index].setColorScale(1, 1, 1, fade)
            self._bars[index].setSx(max(k, 0.001))
            self._bars[index].setX(-0.63 + shift)
            self._items[index].setX(-0.60 + shift)
            self._labels[index].setX(-0.60 + shift)
        return task.cont

    def show(self):
        for node in self._nodes:
            node.show()
        self._start_task()

    def hide(self):
        for node in self._nodes:
            node.hide()
        self._stop_task()

    def destroy(self):
        self._stop_task()
        for node in self._nodes:
            node.destroy()

    def _start_task(self):
        if self._task is None:
            self._t = 0.0
            self._task = builtins.base.taskMgr.add(self._update, 'start_menu_anim')

    def _stop_task(self):
        if self._task is not None:
            builtins.base.taskMgr.remove(self._task)
            self._task = None


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
