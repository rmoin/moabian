# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Joystick Controller

Use joystick input to control the plate directly.
"""

from time import sleep
from typing import Dict

import time
import pymoab

from ..common import IController, IDevice, CircleFeature, Vector2


class JoystickController(IController):
    def __init__(self, config: IController.Config, device: IDevice):
        super().__init__(config, device)
        self.config = config
        self.joystick = Vector2(0, 0)

    def on_menu_down(self, sender: IDevice):
        sender.stop()

        # Hover the plate and deactivate the servos
        pymoab.hoverPlate()
        pymoab.sync()
        sleep(0.5)
        pymoab.disableServoPower()
        pymoab.sync()
        sleep(0.5)

    def on_joy_moved(self, sender: object, x: float, y: float):
        self.joystick = Vector2(-y, x)

    def getControlOutput(
        self,
        sender: IDevice,
        elapsedSec: float,
        detectorResults: Dict[str, CircleFeature],
        currPlateAngles: Vector2,
    ) -> Vector2:

        # Without this sleep (for 90% of our update period), input polling
        # will return zeros intermittently and the actuator will twitch
        update_timestep = 1.0 / sender.config.frequencyHz
        sleep(update_timestep - 0.1 * update_timestep)

        return self.joystick * self.config.maxAngle
