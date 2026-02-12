#!/micropython
# -*- coding: utf-8 -*-
#
# Copyright 2020-2026 by Ichiro Furusato. All rights reserved. This file is part
# of the Robot Operating System project, released under the MIT License.
#
# author:   Ichiro Furusato
# created:  2026-02-09
# modified: 2026-02-12

import time
from machine import Pin
from controller import Controller
from colors import *

class PicoPixel:
    def __init__(self):
        self._led = Pin(25, Pin.OUT)
        # ready

    def on(self):
        self._led.value(1)

    def off(self):
        self._led.value(0)

    @property
    def pixel_count(self):
        return 1

    @property
    def brightness(self):
        return self._brightness

    def set_color(self, index=None, color=None):
        if color is None or color == COLOR_BLACK:
            self.off()
        else:
            self.on()

class PicoController(Controller):
    '''
    An implementation using a Raspberry Pi Pico.
    '''
    def __init__(self, config):
        super().__init__(config)
#       self._pixel_off_pending = False
        # ready

    def _create_pixel(self):
        _pixel = PicoPixel()
        _pixel.on()
        time.sleep_ms(100)
        _pixel.off()
        return _pixel

    def _create_pixel_timer(self):
        try:
            from machine import Timer

            self._pixel_timer = Timer()
            self._pixel_timer.init(freq=self._pixel_timer_freq_hz, callback=self._led_off)
        except Exception as e:
            sys.print_exception(e)

#EOF
