import math
import cv2 as cv
import numpy as np
import imutils
import d3dshot
from time import time
from services import classes
from helpers.txt import draw_text, draw_under
from helpers.surface import create_wrapper
from helpers.threads import StoppableThread

ELEMENT_FROST = 'frost'
ELEMENT_FIRE = 'fire'
ELEMENT_HOLY = 'holy'
ELEMENT_LIGHTNING = 'lightning'
ELEMENT_PHYS = 'phys'
ELEMENT_ARCANE = 'arcane'
ELEMENT_POISON = 'poison'

ELEMENTAL_COLORS = {
    ELEMENT_ARCANE: (217, 128, 250),
    ELEMENT_FROST: (84, 160, 255),
    ELEMENT_FIRE: (255, 159, 67),
    ELEMENT_HOLY: (246, 229, 141),
    ELEMENT_LIGHTNING: (108, 92, 231),
    ELEMENT_PHYS: (170, 166, 157),
    ELEMENT_POISON: (46, 213, 115)
}

ROTATIONS = {
    classes.CLASS_MONK: [ELEMENT_FROST, ELEMENT_FIRE, ELEMENT_HOLY, ELEMENT_LIGHTNING, ELEMENT_PHYS],
    classes.CLASS_WIZARD: [ELEMENT_ARCANE, ELEMENT_FROST, ELEMENT_FIRE, ELEMENT_LIGHTNING],
    classes.CLASS_CRUSADER: [ELEMENT_FIRE, ELEMENT_HOLY, ELEMENT_LIGHTNING, ELEMENT_PHYS],
    classes.CLASS_DEMON_HUNTER: [ELEMENT_FROST, ELEMENT_FIRE, ELEMENT_LIGHTNING, ELEMENT_PHYS],
    classes.CLASS_WITCH_DOCTOR: [ELEMENT_FROST, ELEMENT_FIRE, ELEMENT_LIGHTNING, ELEMENT_POISON],
    classes.CLASS_BARBARIAN: [ELEMENT_FROST, ELEMENT_FIRE, ELEMENT_LIGHTNING, ELEMENT_PHYS],
    classes.CLASS_NECROMANCER: [ELEMENT_FROST, ELEMENT_PHYS, ELEMENT_POISON],
}


PHASE_DURATIONS = {
    classes.CLASS_MONK: 4 * 1000,
    classes.CLASS_WIZARD: 4 * 1000,
    classes.CLASS_CRUSADER: 4 * 1000,
    classes.CLASS_DEMON_HUNTER: 4 * 1000,
    classes.CLASS_WITCH_DOCTOR: 4 * 1000,
    classes.CLASS_BARBARIAN: 4 * 1000,
    classes.CLASS_NECROMANCER: 4 * 1000,
}


class BuffCoe:
    def __init__(self, playing_as, text_background_color):
        self.playing_as = playing_as
        self.text_background_color = text_background_color
        self.phase_duration = PHASE_DURATIONS[playing_as]
        self.rotation = ROTATIONS[playing_as]
        self.rotation_size = len(self.rotation)
        self.rotation_millis = self.rotation_size * 4000
        self.update_every = 5 # frames
        self.timer = self.update_every
        self.time_left = 0
        self.phase = self.rotation[0]
        self.next_phase = self.rotation[1]
        self.rotation_start_ticks = 0
        self.tick = 0
        self.show = False

        screenshoter = d3dshot.create(capture_output="numpy")
        screenshoter.display = screenshoter.displays[0]
        width, height = screenshoter.display.resolution
        self.screenshoter = screenshoter
        self.screenshoter_region = round(width*33/96), round(height*5/6), round(width*63/96), round(height*32/36)
        self.templates = self.get_buff_templates()

        self.recognition_thread = StoppableThread(target=self.recognise_loop)
        self.recognition_thread.start()

    def frame(self, ticks, screen):
        t = ticks - self.rotation_start_ticks
        self.tick = ticks
        if self.show:
            self.draw_status(t, screen)

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

    def recognise_loop(self):
        prev_defined_phase = None
        last_defined_buff_at = self.tick
        while not self.recognition_thread.stopped():
            phase, time_started, buff_index = self.recognise_buff()
            if phase is not None:
                self.show = True
                last_defined_buff_at = time_started
                if prev_defined_phase != phase:
                    prev_defined_phase = phase
                    new_rotation_start_ticks = time_started - buff_index * 4000
                    if new_rotation_start_ticks < self.rotation_start_ticks or (
                            buff_index == 0 and
                            self.rotation_start_ticks - self.rotation_millis * 1000 < self.rotation_start_ticks
                    ):
                        self.rotation_start_ticks = time_started - buff_index * 4000
            elif time_started - last_defined_buff_at > 3000:
                self.show = False

    def recognise_buff(self):
        time_started = self.tick
        crop_img = self.screenshoter.screenshot(region=self.screenshoter_region)

        crop_img = cv.cvtColor(crop_img, cv.COLOR_RGB2BGR)
        crop_img = cv.cvtColor(crop_img, cv.COLOR_BGR2GRAY)

        best_found = [None, 0, None]

        all_found = {}
        for buff_index, buff_tuple in enumerate(self.templates):
            buff_img = buff_tuple[1]
            buff = buff_tuple[0]

            res = cv.matchTemplate(crop_img, buff_img, cv.TM_CCOEFF_NORMED)
            threshold = 0.75

            loc = np.where(res >= threshold)
            found = np.size(loc)

            all_found[buff] = found
            if found > best_found[1]:
                best_found = (buff, found, buff_index)

        return best_found[0], time_started, best_found[2]

    def get_buff_templates(self):
        buffs_images = {
            ELEMENT_ARCANE: 'assets/buffs/coe_arcane.png',
            ELEMENT_FIRE: 'assets/buffs/coe_fire.png',
            ELEMENT_FROST: 'assets/buffs/coe_frost.png',
            ELEMENT_HOLY: 'assets/buffs/coe_holy.png',
            ELEMENT_LIGHTNING: 'assets/buffs/coe_lightning.png',
            ELEMENT_PHYS: 'assets/buffs/coe_phys.png',
            ELEMENT_POISON: 'assets/buffs/coe_poison.png'
        }

        templates = []
        for buff in self.rotation:
            template_path = buffs_images[buff]
            buff_img = cv.imread(template_path, 0)
            templates.append((buff, imutils.resize(buff_img, width=100)))

        return templates

    def stop(self):
        self.recognition_thread.stop()

    # def open_image(img):
    #     winname = "Test"
    #     cv.namedWindow(winname)  # Create a named window
    #     cv.moveWindow(winname, 40, 30)  # Move it to (40,30)
    #     cv.imshow(winname, img)
    #     cv.waitKey(0)
    #     cv.waitKey(1000)
    #     cv.destroyAllWindows()
