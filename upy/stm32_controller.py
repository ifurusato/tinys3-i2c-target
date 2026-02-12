#!/micropython
# -*- coding: utf-8 -*-
#
# Copyright 2020-2026 by Ichiro Furusato. All rights reserved. This file is part
# of the Robot Operating System project, released under the MIT License.
#
# author:   Ichiro Furusato
# created:  2026-02-09
# modified: 2026-02-11

import sys
from controller import Controller
from colors import *
from pixel import Pixel

class PixelState:
    def __init__(self, color=COLOR_BLACK, phase=0.0):
        self.base_color = color
        self.color = color.rgb
        self.phase = phase
        self._pixel_off_pending = False

    def is_active(self):
        return self.base_color != COLOR_BLACK

    def reset(self):
        self.base_color = COLOR_BLACK
        self.color = self.base_color.rgb
        self.phase = 0.0

class STM32Controller(Controller):
    STRIP_PIN = 'B12'
    '''
    An implementation using a WeAct STM32F405 optionally connected to a NeoPixel
    strip and a 24 pixel NeoPixel ring.
    '''
    def __init__(self, config):
        super().__init__(config)
        self._pixel_off_pending = False
        # ready

    def _create_pixel(self):
        from pixel import Pixel

        _pixel_pin = self._config['pixel_pin']
        _pixel = Pixel(pin=_pixel_pin, pixel_count=1, color_order=self._config['color_order'])
        print('NeoPixel configured on pin {}'.format(_pixel_pin))
        _pixel.set_color(0, COLOR_CYAN)
        time.sleep_ms(100)
        _pixel.set_color(0, COLOR_BLACK)
        return _pixel

    def _create_pixel_timer(self):
        from pyb import Timer

        self._pixel_timer = Timer(4)
        self._pixel_timer.init(freq=self._pixel_timer_freq_hz, callback=self._timer_irq)

    def _timer_irq(self, timer):
        self._pixel_off_pending = True
        self._pixel_timer.deinit()  # stop after first trigger

    def _led_off(self, timer=None):
        # override to use deferred execution via flag
        self._pixel_off_pending = True

    def tick(self, delta_ms):
        # handle deferred pixel updates first
        if self._pixel_off_pending:
            self._pixel_off_pending = False
            self._pixel.set_color(0, COLOR_BLACK)
        # then do normal tick processing
        super().tick(delta_ms)

    def pre_process(self, cmd, arg0, arg1, arg2, arg3, arg4):
        '''
        Pre-process the arguments, returning a response and color if a match occurs.
        Such a match precludes further processing.
        '''
        print("🦊 pre-process command '{}' with arg0: '{}'; arg1: '{}'; arg2: '{}'; arg3: '{}'; arg4: '{}'".format(cmd, arg0, arg1, arg2, arg3, arg4))
        if arg0 == "__extend_here__":
            return None, None
        else:
            return None, None
    
    def post_process(self, cmd, arg0, arg1, arg2, arg3, arg4):
        '''
        Post-process the arguments, returning a NACK and color if no match on arg0 occurs.
        '''
        print("🦊 post-process command '{}' with arg0: '{}'; arg1: '{}'; arg2: '{}'; arg3: '{}'; arg4: '{}'".format(cmd, arg0, arg1, arg2, arg3, arg4))
        if arg0 == "__extend_here__":
            return None, None
        else:
            return None, None

#EOF
