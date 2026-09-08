from direct.gui.DirectGui import DGG, DirectButton

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
