import win32api
import win32con
import win32gui
import pygame as pg
from services.buffs.coe import BuffCoe
import sys
from helpers.surface import create_wrapper

class App:
    def __init__(self, playing_as, text_background_color):
        self.playing_as = playing_as
        self.text_background_color = text_background_color
        self.transparency_color = (1, 1, 1)
        self.screen = pg.display.set_mode((200, 80), pg.NOFRAME)
        self.hwnd = pg.display.get_wm_info()["window"]

        # self.diablo_hwnd = win32gui.FindWindow(None, "Diablo III")

        self.make_window_transparent()

        self.frame_observers = [
            BuffCoe(playing_as=self.playing_as, text_background_color=text_background_color)
        ]

        self.clock = pg.time.Clock()
        self.done = False

        while not self.done:
            self.handle_default_key_binds()
            self.frameloop()

    def make_window_transparent(self):
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOACTIVATE | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
        # Set window transparency color
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        win32gui.SetLayeredWindowAttributes(self.hwnd, win32api.RGB(*self.transparency_color), 0, win32con.LWA_COLORKEY)
        # win32gui.SetLayeredWindowAttributes(self.hwnd, win32api.RGB(*self.transparency_color), 150, win32con.LWA_ALPHA)

    def handle_default_key_binds(self):
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.done = True
                    for observer in self.frame_observers:
                        observer.stop()

    def frameloop(self):
        ticks = pg.time.get_ticks()
        self.screen.fill(self.transparency_color)

        for observer in self.frame_observers:
            observer.frame(ticks, self.screen)

        pg.display.flip()
        self.clock.tick(1000)
