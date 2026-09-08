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
        self._on_settings = on_settings
        self._on_exit = on_exit or base.userExit

        self._t = 0.0
        self._task = None
        self._hover = [False, False, False]
        self._k = [0.0, 0.0, 0.0]

        self._x = -0.348 * base.getAspectRatio()
        self._item_x = self._x + 0.02
        self._bar_x = self._x - 0.01

        self.overlay = OnscreenImage(image=_overlay_texture(), parent=base.render2d)
        self.overlay.setTransparency(TransparencyAttrib.MAlpha)

        self.title = OnscreenText(
            parent=base.aspect2d,
            text='CASECODE',
            font=_font('bold'),
            pos=(self._x, 0.35),
            scale=0.105,
            fg=(0.93, 0.95, 0.98, 1),
            align=TextNode.ALeft,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.008, 0.008),
            mayChange=True,
        )

        cursor_x = self._x + self.title.textNode.getWidth() * 0.105 + 0.022
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
            pos=(self._x, 0.275),
            scale=0.026,
            fg=(0.42, 0.47, 0.56, 1),
            align=TextNode.ALeft,
            mayChange=False,
        )

        self.rec_dot = DirectFrame(
            parent=base.aspect2d,
            frameSize=(-0.012, 0.012, -0.012, 0.012),
            frameColor=(_REC_RED[0], _REC_RED[1], _REC_RED[2], 1),
            pos=(self._x + 0.012, 0, 0.74),
            relief=DGG.FLAT,
        )
        self.rec_dot.setTransparency(TransparencyAttrib.MAlpha)
        self.rec_text = OnscreenText(
            parent=base.aspect2d,
            text='REC',
            font=_font('bold'),
            pos=(self._x + 0.045, 0.74),
            scale=0.03,
            fg=(_REC_RED[0], _REC_RED[1], _REC_RED[2], 1),
            align=TextNode.ALeft,
            mayChange=False,
        )

        self.version = OnscreenText(
            parent=base.aspect2d,
            text='v0.1.0',
            font=_font('regular'),
            pos=(self._x, -0.84),
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
                pos=(self._bar_x, 0, z),
                relief=DGG.FLAT,
            )
            bar.setTransparency(TransparencyAttrib.MAlpha)
            bar.setSx(0.001)

            item = DirectButton(
                parent=base.aspect2d,
                pos=(self._item_x, 0, z),
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
                pos=(self._item_x, z),
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
            self._bars[index].setX(self._bar_x + shift)
            self._items[index].setX(self._item_x + shift)
            self._labels[index].setX(self._item_x + shift)
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
            self._hover = [False, False, False]
            self._k = [0.0, 0.0, 0.0]
            self._task = builtins.base.taskMgr.add(self._update, 'start_menu_anim')

    def _stop_task(self):
        if self._task is not None:
            builtins.base.taskMgr.remove(self._task)
            self._task = None


class SettingsWindow:
    def __init__(self, on_back=None, on_change=None, values=None):
        base = getattr(builtins, 'base', None)
        if base is None:
            raise RuntimeError('SettingsWindow requires a ShowBase instance to exist first.')

        self._on_back = on_back or self.hide
        self._on_change = on_change
        self._values = dict(values) if values else {}

        self._t = 0.0
        self._task = None
        self._back_hover = False
        self._back_k = 0.0
        self._row_hover = []
        self._row_k = []

        self._x = -0.348 * base.getAspectRatio()
        self._item_x = self._x + 0.02
        self._bar_x = self._x - 0.01
        self._meter_x = self._x + 0.44

        self.overlay = OnscreenImage(image=_overlay_texture(), parent=base.render2d)
        self.overlay.setTransparency(TransparencyAttrib.MAlpha)

        self.title = OnscreenText(
            parent=base.aspect2d,
            text='SETTINGS',
            font=_font('bold'),
            pos=(self._x, 0.35),
            scale=0.105,
            fg=(0.93, 0.95, 0.98, 1),
            align=TextNode.ALeft,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.008, 0.008),
            mayChange=True,
        )

        cursor_x = self._x + self.title.textNode.getWidth() * 0.105 + 0.022
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
            text='SYSTEM CONFIGURATION',
            font=_font('regular'),
            pos=(self._x, 0.275),
            scale=0.026,
            fg=(0.42, 0.47, 0.56, 1),
            align=TextNode.ALeft,
            mayChange=False,
        )

        self._specs = [('CAMERA SPEED', 'camera_speed', 'meter', 5, 0.10),
                       ('ZOOM SPEED', 'zoom_speed', 'meter', 5, -0.02),
                       ('INVERT DRAG Y', 'invert_drag_y', 'toggle', False, -0.14)]
        self._keys = []
        self._kinds = []
        self._row_starts = []
        self._row_nodes = []
        self._cells = {}
        self._value_texts = {}
        self._toggles = {}
        for index, (label_text, key, kind, default, z) in enumerate(self._specs):
            self._keys.append(key)
            self._kinds.append(kind)
            self._row_starts.append(0.16 + index * 0.08)
            self._row_hover.append(False)
            self._row_k.append(0.0)
            value = self._values.get(key, default)
            self._values[key] = value

            label = OnscreenText(
                parent=base.aspect2d,
                text=label_text,
                font=_font('regular'),
                pos=(self._item_x, z),
                scale=0.042,
                fg=(_IDLE_TEXT[0], _IDLE_TEXT[1], _IDLE_TEXT[2], 1),
                align=TextNode.ALeft,
                mayChange=True,
            )
            nodes = [label]

            if kind == 'meter':
                cells = []
                for i in range(10):
                    cell = DirectButton(
                        parent=base.aspect2d,
                        pos=(self._meter_x + i * 0.026, 0, z - 0.012),
                        relief=DGG.FLAT,
                        frameSize=(0, 0.016, 0, 0.05),
                        frameColor=self._cell_colors(i < value),
                        pressEffect=0,
                        command=self._set_value,
                        extraArgs=[key, i + 1],
                    )
                    cell.setTransparency(TransparencyAttrib.MAlpha)
                    cells.append(cell)
                    nodes.append(cell)
                self._cells[key] = cells
            else:
                toggle = DirectButton(
                    parent=base.aspect2d,
                    pos=(self._meter_x, 0, z),
                    relief=DGG.FLAT,
                    frameSize=(0.0, 0.14, -0.045, 0.055),
                    frameColor=(1, 1, 1, 0),
                    pressEffect=0,
                    command=self._toggle_value,
                    extraArgs=[key],
                )
                toggle.setTransparency(TransparencyAttrib.MAlpha)
                toggle.bind(DGG.ENTER, self._row_enter, extraArgs=[index])
                toggle.bind(DGG.EXIT, self._row_exit, extraArgs=[index])

                value_text = OnscreenText(
                    parent=base.aspect2d,
                    text='OFF',
                    font=_font('regular'),
                    pos=(self._meter_x, z),
                    scale=0.042,
                    fg=(_ACCENT[0], _ACCENT[1], _ACCENT[2], 1),
                    align=TextNode.ALeft,
                    mayChange=True,
                )
                self._value_texts[key] = value_text
                self._toggles[key] = toggle
                nodes.append(toggle)
                nodes.append(value_text)
                self._refresh_row(key)
            self._row_nodes.append(nodes)

        self.back_bar = DirectFrame(
            parent=base.aspect2d,
            frameSize=(0, 0.016, -0.012, 0.030),
            frameColor=(_ACCENT[0], _ACCENT[1], _ACCENT[2], 1),
            pos=(self._bar_x, 0, -0.34),
            relief=DGG.FLAT,
        )
        self.back_bar.setTransparency(TransparencyAttrib.MAlpha)
        self.back_bar.setSx(0.001)

        self.back_button = DirectButton(
            parent=base.aspect2d,
            pos=(self._item_x, 0, -0.34),
            relief=DGG.FLAT,
            frameSize=(0.0, 0.30, -0.045, 0.055),
            frameColor=(1, 1, 1, 0),
            pressEffect=0,
            command=self._on_back,
        )
        self.back_button.setTransparency(TransparencyAttrib.MAlpha)
        self.back_button.bind(DGG.ENTER, self._back_enter)
        self.back_button.bind(DGG.EXIT, self._back_exit)

        self.back_label = OnscreenText(
            parent=base.aspect2d,
            text='BACK',
            font=_font('regular'),
            pos=(self._item_x, -0.34),
            scale=0.042,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=True,
        )

        self.version = OnscreenText(
            parent=base.aspect2d,
            text='v0.1.0',
            font=_font('regular'),
            pos=(self._x, -0.84),
            scale=0.026,
            fg=(0.42, 0.47, 0.56, 1),
            align=TextNode.ALeft,
            mayChange=False,
        )

        self._nodes = [self.overlay, self.title, self.cursor, self.tagline,
                       *(node for nodes in self._row_nodes for node in nodes),
                       self.back_bar, self.back_button, self.back_label, self.version]

        for node in self._nodes:
            node.setAlphaScale(0.0)
        self.hide()

    def _cell_colors(self, filled):
        if filled:
            return ((0.0, 1.0, 0.96, 0.80), (0.0, 0.78, 0.75, 0.85),
                    (0.35, 1.0, 0.98, 0.95), (0.0, 1.0, 0.96, 0.80))
        return ((0.13, 0.16, 0.23, 0.55), (0.13, 0.16, 0.23, 0.55),
                (0.24, 0.30, 0.40, 0.90), (0.13, 0.16, 0.23, 0.55))

    def _set_value(self, key, value):
        self._values[key] = value
        self._refresh_row(key)
        if self._on_change:
            self._on_change(key, value)

    def _toggle_value(self, key):
        self._set_value(key, not self._values[key])

    def _refresh_row(self, key):
        index = self._keys.index(key)
        if self._kinds[index] == 'meter':
            level = self._values[key]
            for i, cell in enumerate(self._cells[key]):
                cell['frameColor'] = self._cell_colors(i < level)
        else:
            on = self._values[key]
            text = self._value_texts[key]
            text.setText('ON' if on else 'OFF')
            color = _ACCENT if on else _IDLE_TEXT
            text.textNode.setTextColor(color[0], color[1], color[2], 1)

    def _row_enter(self, index, event=None):
        self._row_hover[index] = True

    def _row_exit(self, index, event=None):
        self._row_hover[index] = False

    def _back_enter(self, event=None):
        self._back_hover = True

    def _back_exit(self, event=None):
        self._back_hover = False

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
            self._fade_node(self.version, 0.50)

        self.cursor.setAlphaScale(
            self._fade_amount(0.0) * (0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 4))))

        for index in range(len(self._row_nodes)):
            fade = self._fade_amount(self._row_starts[index])
            nodes = self._row_nodes[index]
            if self._kinds[index] == 'toggle':
                target = 1.0 if self._row_hover[index] else 0.0
                k = self._row_k[index]
                if k != target:
                    k = k + (target - k) * min(1.0, dt * 14)
                    if abs(target - k) < 0.002:
                        k = target
                    self._row_k[index] = k
                if k != target or t < 1.2:
                    r = _IDLE_TEXT[0] + (1.0 - _IDLE_TEXT[0]) * k
                    g = _IDLE_TEXT[1] + (1.0 - _IDLE_TEXT[1]) * k
                    b = _IDLE_TEXT[2] + (1.0 - _IDLE_TEXT[2]) * k
                    nodes[0].setColorScale(r, g, b, fade)
            elif t < 1.2:
                nodes[0].setAlphaScale(fade)
            if t < 1.2:
                for node in nodes[1:]:
                    node.setAlphaScale(fade)

        fade = self._fade_amount(0.42)
        k = self._back_k
        target = 1.0 if self._back_hover else 0.0
        if k != target:
            k = k + (target - k) * min(1.0, dt * 14)
            if abs(target - k) < 0.002:
                k = target
            self._back_k = k
        if k != target or t < 1.2:
            shift = 0.012 * k
            r = _IDLE_TEXT[0] + (1.0 - _IDLE_TEXT[0]) * k
            g = _IDLE_TEXT[1] + (1.0 - _IDLE_TEXT[1]) * k
            b = _IDLE_TEXT[2] + (1.0 - _IDLE_TEXT[2]) * k
            self.back_label.setColorScale(r, g, b, fade)
            self.back_bar.setColorScale(1, 1, 1, fade)
            self.back_bar.setSx(max(k, 0.001))
            self.back_bar.setX(self._bar_x + shift)
            self.back_button.setX(self._item_x + shift)
            self.back_label.setX(self._item_x + shift)
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
            self._back_hover = False
            self._back_k = 0.0
            self._row_hover = [False] * len(self._row_nodes)
            self._row_k = [0.0] * len(self._row_nodes)
            self._task = builtins.base.taskMgr.add(self._update, 'settings_menu_anim')

    def _stop_task(self):
        if self._task is not None:
            builtins.base.taskMgr.remove(self._task)
            self._task = None


class SideMenu:
    def __init__(self, on_resume=None, on_restart=None, on_quit=None):
        base = getattr(builtins, 'base', None)
        if base is None:
            raise RuntimeError('SideMenu requires a ShowBase instance to exist first.')

        self._on_resume = on_resume or self.hide
        self._on_restart = on_restart or self._restart_placeholder
        self._on_quit = on_quit or base.userExit

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
        self.quit_button = self._entry('Quit', 2, self._on_quit)

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

    def destroy(self):
        if self._task is not None:
            builtins.base.taskMgr.remove(self._task)
            self._task = None
        self.title.destroy()
        self.resume_button.destroy()
        self.restart_button.destroy()
        self.quit_button.destroy()
        self.panel.destroy()

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
