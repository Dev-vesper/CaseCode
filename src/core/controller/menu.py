import builtins

from src.core.controller.player import Player
from src.ui.buttons import make_round_button
from src.ui.windows import SideMenu, StartWindow


class Menu:
    def __init__(self):
        base = getattr(builtins, 'base', None)
        if base is None:
            raise RuntimeError('Menu requires a ShowBase instance to exist first.')

        self.start_window = StartWindow(on_play=self.start_game)
        self.side_menu = None
        self.hud_buttons = []

    def start_game(self):
        base.player = Player(base.world)
        self.start_window.hide()
        self.side_menu = SideMenu(on_quit=self.quit_to_menu)
        margin = 0.07
        spacing = 0.125
        row_y = -(margin + 0.045)
        self.hud_buttons = [
            make_round_button(base.a2dTopRight, (-(margin + 0.045), 0, row_y),
                              icon='hamburger', command=self.side_menu.toggle),
            make_round_button(base.a2dTopRight, (-(margin + 0.045) - spacing, 0, row_y),
                              icon='plus'),
            make_round_button(base.a2dTopRight, (-(margin + 0.045) - 2 * spacing, 0, row_y),
                              icon='grid'),
        ]

    def quit_to_menu(self):
        base.player.destroy()
        base.player = None
        for button in self.hud_buttons:
            button.destroy()
        self.hud_buttons = []
        self.side_menu.destroy()
        self.side_menu = None
        self.start_window.show()
