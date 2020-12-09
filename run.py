import sys,os
import pygame as pg
from app import App
from services import classes


if __name__ == '__main__':
    pg.init()
    info = pg.display.Info()

    # text_background_color = (30,30,30,0) # RGBA, without background
    text_background_color = (30,30,30,250) # RGBA, with background

    # (info.current_w/2, info.current_h/2) - center of screen. 250 - shifts
    os.environ['SDL_VIDEO_WINDOW_POS'] = "{x},{y}".format(
        x=int(info.current_w/2) - 250,
        y=int(info.current_h/2) - 250
    )

    App(
        playing_as=classes.CLASS_MONK,
        text_background_color=text_background_color
    )
    pg.quit()
    sys.exit()
