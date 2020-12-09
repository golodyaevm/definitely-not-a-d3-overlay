from services import classes
import math
from helpers.txt import draw_text, draw_under
from helpers.surface import create_wrapper

ELEMENT_FROST = 'frost'
ELEMENT_FIRE = 'fire'
ELEMENT_LIGHT = 'light'
ELEMENT_LIGHTNING = 'lightning'
ELEMENT_PHYS = 'phys'

ELEMENTAL_COLORS = {
    ELEMENT_FROST: (84, 160, 255),
    ELEMENT_FIRE: (255, 159, 67),
    ELEMENT_LIGHT: (246, 229, 141),
    ELEMENT_LIGHTNING: (108, 92, 231),
    ELEMENT_PHYS: (170, 166, 157)
}

ROTATIONS = {
    # classes.CLASS_MONK: [ELEMENT_FROST, ELEMENT_FIRE, ELEMENT_LIGHT, ELEMENT_LIGHTNING, ELEMENT_PHYS],
    classes.CLASS_MONK: [ELEMENT_LIGHTNING, ELEMENT_FROST, ELEMENT_FIRE, ELEMENT_LIGHT, ELEMENT_PHYS]
}


PHASE_DURATIONS = {
    classes.CLASS_MONK: 4 * 1000
}


class BuffCoe:
    def __init__(self, playing_as, text_background_color):
        self.playing_as = playing_as
        self.text_background_color = text_background_color
        self.phase_duration = PHASE_DURATIONS[playing_as]
        self.rotation = ROTATIONS[playing_as]
        self.rotation_size = len(self.rotation)
        self.update_every = 10 # frames
        self.timer = self.update_every
        self.time_left = 0
        self.phase = self.rotation[0]
        self.next_phase = self.rotation[1]

    def frame(self, ticks, screen):
        self.draw_status(ticks, screen)

    def draw_status(self, ticks, screen):
        surface = create_wrapper(width=240, height=80)
        self.timer -= 1

        # Do maths every self.update_every
        if self.timer <= 0:
            self.timer = self.update_every

            phases_passed = math.floor(ticks / self.phase_duration)
            phase_number = int(phases_passed % self.rotation_size)

            phase_start = phases_passed * self.phase_duration
            phase_end = phase_start + self.phase_duration

            self.time_left = math.ceil((phase_end - ticks) / 10) / 100
            self.phase = self.rotation[phase_number]
            self.next_phase = self.rotation[(phase_number + 1) % self.rotation_size]

        time_left_txt = draw_text(
            message=self.time_left,
            size=36,
            left=2,
            color=ELEMENTAL_COLORS[self.phase],
            background_color=self.text_background_color,
            surface=surface
        )
        phase_txt = draw_under(
            message=self.phase.upper(),
            size=48,
            color=ELEMENTAL_COLORS[self.phase],
            background_color=self.text_background_color,
            under=time_left_txt,
            margin_left=-2,
            margin_top=-2,
            surface=surface
        )
        next_phase_txt = draw_under(
            message=self.next_phase,
            size=36,
            color=ELEMENTAL_COLORS[self.next_phase],
            background_color=self.text_background_color,
            under=phase_txt,
            margin_top=-4,
            margin_left=2,
            surface=surface
        )
        screen.blit(surface, (0, 0))
