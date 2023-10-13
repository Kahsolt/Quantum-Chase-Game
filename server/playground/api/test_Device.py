#!/usr/bin/env python3
# Author: Armit
# Create Time: 2023/09/07

from isq.device.device import Device

Device.run
Device.get_ir
Device.compile_to_ir
Device.compile_with_par
Device.simulate
Device.getargs
Device.draw_circuit

from isq.device.device import LocalDevice

LocalDevice.probs
