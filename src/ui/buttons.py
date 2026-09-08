from direct.gui.DirectGui import DGG, DirectButton
from panda3d.core import PNMImage, Texture, TransparencyAttrib

_STYLES = {
    'primary': [(0.16, 0.42, 0.27, 1), (0.11, 0.30, 0.19, 1), (0.22, 0.55, 0.35, 1), (0.12, 0.14, 0.13, 1)],
    'neutral': [(0.22, 0.26, 0.33, 1), (0.15, 0.18, 0.23, 1), (0.30, 0.35, 0.44, 1), (0.12, 0.13, 0.16, 1)],
    'danger': [(0.50, 0.16, 0.16, 1), (0.36, 0.11, 0.11, 1), (0.64, 0.22, 0.22, 1), (0.16, 0.12, 0.12, 1)],
}


def make_button(text, parent, pos, command=None, extra_args=(), style='neutral',
                width=2.2, height=0.12):
    if style not in _STYLES:
        raise ValueError(f'unknown button style: {style}')
    return DirectButton(
        parent=parent,
        pos=pos,
        text=text,
        text_scale=0.05,
        text_fg=(1, 1, 1, 1),
        frameSize=(-width / 2, width / 2, -height / 2, height / 2),
        frameColor=_STYLES[style],
        relief=DGG.FLAT,
        command=command,
        extraArgs=list(extra_args),
    )


def _in_superellipse(x, y, exponent):
    return abs(x) ** exponent + abs(y) ** exponent <= 1.0


def _in_icon(icon, x, y):
    if icon == 'hamburger':
        return (abs(x / 0.52) ** 8 + abs((y + 0.44) / 0.11) ** 8 <= 1.0
                or abs(x / 0.52) ** 8 + abs(y / 0.11) ** 8 <= 1.0
                or abs(x / 0.52) ** 8 + abs((y - 0.44) / 0.11) ** 8 <= 1.0)
    if icon == 'plus':
        return (abs(x / 0.50) ** 8 + abs(y / 0.13) ** 8 <= 1.0
                or abs(y / 0.50) ** 8 + abs(x / 0.13) ** 8 <= 1.0)
    if icon == 'grid':
        return ((x + 0.25) ** 2 + (y + 0.25) ** 2 <= 0.16 ** 2
                or (x - 0.25) ** 2 + (y + 0.25) ** 2 <= 0.16 ** 2
                or (x + 0.25) ** 2 + (y - 0.25) ** 2 <= 0.16 ** 2
                or (x - 0.25) ** 2 + (y - 0.25) ** 2 <= 0.16 ** 2)
    return False


_SHAPE_CACHE = {}


def _shape_map(icon, exponent, size):
    key = (icon, exponent, size)
    if key in _SHAPE_CACHE:
        return _SHAPE_CACHE[key]
    half = size / 2.0
    xpos, xpow = [], []
    for px in range(size):
        for sx in (0.25, 0.75):
            x = (px + sx - half) / half
            xpos.append(x)
            xpow.append(abs(x) ** exponent)
    ypos, ypow = [], []
    for py in range(size):
        for sy in (0.25, 0.75):
            y = 1.0 - 2.0 * (py + sy) / size
            ypos.append(y)
            ypow.append(abs(y) ** exponent)
    maps = []
    for py in range(size):
        for px in range(size):
            coverage = 0.0
            icon_hits = 0.0
            col = px * 2
            row = py * 2
            for iy in (0, 1):
                for ix in (0, 1):
                    if xpow[col + ix] + ypow[row + iy] <= 1.0:
                        coverage += 0.25
                        if icon and _in_icon(icon, xpos[col + ix], ypos[row + iy]):
                            icon_hits += 0.25
            maps.append((coverage, icon_hits / coverage if coverage else 0.0))
    _SHAPE_CACHE[key] = maps
    return maps


_TEXTURE_CACHE = {}


def _round_texture(color, icon, lighten):
    key = (color, icon, lighten)
    if key in _TEXTURE_CACHE:
        return _TEXTURE_CACHE[key]
    exponent = 4.0
    opacity = 0.7
    size = 96
    maps = _shape_map(icon, exponent, size)
    image = PNMImage(size, size, 4)
    base = [min(1.0, c + lighten * (1.0 - c)) for c in color]
    for py in range(size):
        for px in range(size):
            coverage, mix = maps[py * size + px]
            if coverage <= 0.0:
                image.setAlpha(px, py, 0.0)
                continue
            image.setXel(px, py,
                         base[0] + (1.0 - base[0]) * mix,
                         base[1] + (1.0 - base[1]) * mix,
                         base[2] + (1.0 - base[2]) * mix)
            image.setAlpha(px, py, coverage * opacity)
    texture = Texture('superellipse')
    texture.load(image)
    _TEXTURE_CACHE[key] = texture
    return texture


def make_round_button(parent, pos, icon=None, command=None, extra_args=(),
                      color=(0.18, 0.22, 0.32), size=0.14):
    normal = _round_texture(color, icon, 0.0)
    press = _round_texture(color, icon, 0.25)
    hover = _round_texture(color, icon, 0.12)
    button = DirectButton(
        parent=parent,
        pos=pos,
        relief=DGG.FLAT,
        frameSize=(-size / 2, size / 2, -size / 2, size / 2),
        frameColor=(1, 1, 1, 0),
        image=(normal, press, hover, press),
        image_scale=(size, 1, size),
        state=DGG.NORMAL,
        command=command,
        extraArgs=list(extra_args),
    )
    button.setTransparency(TransparencyAttrib.MAlpha)
    return button
