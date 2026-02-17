#!/micropython
# -*- coding: utf-8 -*-
#
# Copyright 2020-2026 by Ichiro Furusato. All rights reserved. This file is part
# of the Robot Operating System project, released under the MIT License. Please
# see the LICENSE file included as part of this package.
#
# author:   Ichiro Furusato
# created:  2026-01-27
# modified: 2026-02-17

import time
from machine import Pin, I2C

from i2c_scanner import I2CScanner
from device import Device

class RadiozoaConfig:
    '''
    Configures all VL53L0X sensors on the Radiozoa sensor board to their unique
    I2C addresses by toggling XSHUT pins and setting addresses as specified in
    the Device pseudo-enum.
    '''
    def __init__(self, i2c_bus=1):
        self._i2c_bus_number = i2c_bus
        self._default_i2c_address = 0x29
        self._i2c = None
        self._i2c_baud_rate = 400_000 # default 100,000
        self._xshut_pins = {}
        self._setup_i2c()
        self._setup_pins()
        self._i2c_scanner = I2CScanner(i2c_bus=self._i2c_bus_number)
        print('ready.')

    def configure(self):
        self._shutdown_all_sensors()
        self._configure_sensor_addresses()
        print('all sensor addresses configured.')

    def reset(self):
        from device import N0
        device = N0
        print("reset: temporarily shutting down sensor {} at XSHUT pin {}…".format(device.label, device.xshut))
        self._set_xshut(device.index, False)
        time.sleep_ms(250)
        self._set_xshut(device.index, True)
        print('radiozoa reset.\n')

    def _setup_i2c(self):
        self._i2c = I2C(self._i2c_bus_number, freq=self._i2c_baud_rate)
        print('I2C{} open.'.format(self._i2c_bus_number))

    def _setup_pins(self):
        '''
        Configure all XSHUT pins as outputs based on Device pseudo-enum.
        '''
        for device in Device.all():
            if device:
                pin = Pin(device.xshut, Pin.OUT) # on pyb, OUT_PP
                self._xshut_pins[device.index] = pin
                print("configured XSHUT pin {} for sensor {} on 0x{:02X} as output.".format(device.xshut, device.label, device.i2c_address))

    def close(self):
        '''
        Cleanup if necessary.
        '''
        print('closing radiozoa config.')

    def _shutdown_all_sensors(self):
        '''
        Shuts down all sensors by setting their XSHUT pins LOW.
        '''
        for device in Device.all():
            if device:
                print("shutting down sensor {} at XSHUT pin {}…".format(device.label, device.xshut))
                self._set_xshut(device.index, False)
                time.sleep_ms(50)
        print('all sensors shut down.\n')

    def _configure_sensor_addresses(self):
        '''
        Sequentially brings up each sensor, sets its I2C address, leaving it enabled.
        '''
        needs_scan = True
        for device in Device.all():
            if device:
                print("configuring sensor {} at XSHUT pin {}…".format(device.label, device.xshut))
                self._set_xshut(device.index, True)
                found = False
                for i in range(5):
                    time.sleep_ms(750)
                    self._i2c_scanner.scan()
                    found = self._i2c_scanner.has_hex_address(0x29)
                    if found:
                        print("[{}] sensor appeared at 0x29.".format(i))
                        break
                    else:
                        print("[{}] waiting for sensor…".format(i))
                if not found:
                    print("WARNING: sensor {} did not appear at 0x29.".format(device.label))
                    continue
                try:
                    self._set_i2c_address(0x29, device.i2c_address)
                    print("set address for sensor {} to 0x{:02X}".format(device.label, device.i2c_address))
                except Exception as e:
                    print("ERROR: {} raised setting address for sensor {}: {}".format(type(e), device.label, e))
                time.sleep_ms(50)

    def _set_xshut(self, device_index, value):
        '''
        Set the XSHUT pin state for a given device.
        '''
        pin = self._xshut_pins.get(device_index)
        if pin:
            if value:
                pin.on() # pin.high()
#               print("set device {} pin HIGH.".format(device_index))
            else:
                pin.off() # pin.low()
#               print("set device {} pin LOW.".format(device_index))
        else:
            raise RuntimeError('pin not available for device {}.'.format(device_index))

    def _set_i2c_address(self, current_addr, new_addr):
        '''
        Change VL53L0X I2C address from current_addr to new_addr.
        Assumes sensor is up at current_addr.
        '''
        reg = 0x8A
        self._i2c.writeto_mem(current_addr, reg, bytes([new_addr]))
#       self._i2c.mem_write(new_addr, current_addr, reg)
        time.sleep_ms(50)

#EOF
