import pygame as pg


def draw_text(message, surface, top=0, left=0, color=(0, 0, 0), background_color=(30, 30, 30, 0), size=36):
    txt = render_txt(message, color, size)
    srfc = surface.subsurface(pg.Rect(left, top, txt.get_rect().width, txt.get_rect().height))
    srfc.fill(background_color)
    srfc.blit(txt, (0, 0))

    return srfc


def draw_under(message, surface, under, margin_top=0, margin_left=0, color=(0, 0, 0), background_color=(30, 30, 30, 0), size=36):
    txt = render_txt(message, color, size)

    left = under.get_abs_offset()[0] + margin_left
    top = under.get_abs_offset()[1] + under.get_rect().height + margin_top

    srfc = surface.subsurface(pg.Rect(left, top, txt.get_rect().width, txt.get_rect().height))
    srfc.fill(background_color)
    srfc.blit(txt, (0, 0))
    return srfc


def render_txt(message, color=(0, 0, 0), size=36):
    font = pg.font.Font(None, size)
    txt = font.render(str(message), True, color)
    return txt