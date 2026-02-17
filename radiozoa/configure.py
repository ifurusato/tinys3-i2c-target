#!/micropython
# -*- coding: utf-8 -*-
#
# Copyright 2020-2026 by Ichiro Furusato. All rights reserved. This file is part
# of the Robot Operating System project, released under the MIT License. Please
# see the LICENSE file included as part of this package.
#
# author:   Ichiro Furusato
# created:  2026-01-27
# modified: 2026-02-04

import sys
import time
from colorama import Fore, Style

from i2c_scanner import I2CScanner
from radiozoa_config import RadiozoaConfig
from device import Device

class Configure:
    '''
    Performs the action of scanning for VL53 devices and coordinating the
    RadiozoaConfig handling of their disabling/enabling, and setting their
    I2C addresses.
    '''
    def __init__(self):
        self._scanner = I2CScanner(i2c_id=1)
        self._default_i2c_address = 0x29
        self._devices = []
        self._radiozoa_config = None
        print('ready.')

    @property
    def radiozoa_config(self):
        return self._radiozoa_config

    def get_devices(self):
        return self._devices

    def configure(self, force=False):
        '''
        Returns True if successful.
        '''
        try:
            if force:
                print(Fore.GREEN + "radiozoa sensor configuration… " + Style.BRIGHT + '(forced)' + Style.RESET_ALL)
            else:
                print(Fore.GREEN + "radiozoa sensor configuration…" + Style.RESET_ALL)
            for device in Device.all():
                print("device '{}'; impl: {}; I2C address: 0x{:02X}; xshut: {}".format(device.label, device.impl, device.i2c_address, device.xshut))
            # scan for existing sensors
            self._devices = self._scanner.scan()
            for device in self._devices:
                print(Style.DIM + '  device: 0x{:02X}'.format(device))
            _sensor_addresses = [ dev.i2c_address for dev in Device.all() ]
            print("checking for default address and missing sensors…")
            _has_default = self._scanner.has_hex_address(self._default_i2c_address)
            _missing = [ addr for addr in _sensor_addresses if not self._scanner.has_hex_address(addr) ]
            if force or _has_default or _missing:
                self._scanner.i2cdetect(Fore.WHITE)
                if _has_default:
                    print(Fore.YELLOW + "found default 0x{:02X} device; reassigning radiozoa addresses…".format(self._default_i2c_address) + Style.RESET_ALL)
                if _missing:
                    print(Fore.YELLOW + "missing sensor addresses: {}".format([ "0x{:02X}".format(addr) for addr in _missing ]) + Style.RESET_ALL)
                try:
                    self._radiozoa_config = RadiozoaConfig(i2c_bus=1)
                    self._radiozoa_config.configure()
#                   self._radiozoa_config.close()
                except Exception as e:
                    print("ERROR: {} raised during RadiozoaConfig configuration: {}".format(type(e), e))
                    raise
                # re-scan after configuration
                print("re-scanning for radiozoa sensor addresses…")
                time.sleep_ms(1000)
                self._devices = self._scanner.scan()
                _has_default = self._scanner.has_hex_address(self._default_i2c_address)
                _missing = [ addr for addr in _sensor_addresses if not self._scanner.has_hex_address(addr) ]
                if _has_default:
                    print("WARNING: default address 0x{:02X} is still present after configuration.".format(self._default_i2c_address))
                    self._scanner.i2cdetect(Fore.RED)
                    return False
                if _missing:
                    print("ERROR: missing sensor addresses after configuration: {}".format([ "0x{:02X}".format(addr) for addr in _missing ]))
                    self._scanner.i2cdetect(Fore.RED)
                    return False
                else:
                    print(Fore.GREEN + "radiozoa sensor addresses configured successfully." + Style.RESET_ALL)
                    self._scanner.i2cdetect(Fore.GREEN)
            else:
                print(Fore.GREEN + "radiozoa already configured." + Style.RESET_ALL)
                self._scanner.i2cdetect(Fore.CYAN)
            print('complete.')
            return True
        except Exception as e:
            print('ERROR: {} raised during configuration: {}'.format(type(e), e))
        return False

#EOF
