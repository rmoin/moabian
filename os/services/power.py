#!/usr/bin/python3
# vim:filetype=python:

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import time
import threading as th
import RPi.GPIO as gpio

from sys import exit
from threading import Timer
from datetime import datetime
from signal import signal, SIGINT

power_pin = 3  # HAT puts button signal here https://pinout.xyz/pinout/pin5_gpio3
pressed = 0  # button is active low, so depressed is 0
countdown = 1  # two seconds; it's longer than you think

# countdown timer thread
T = None
too_late = False


def setupGPIO():
    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)
    gpio.setup(power_pin, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.add_event_detect(
        power_pin, edge=gpio.BOTH, callback=power_button_event, bouncetime=5
    )


def shutdown():
    global too_late
    too_late = True
    print("Shutting down", flush=True)

    os.system("docker kill control")
    print("> docker kill control", flush=True)

    os.system("oled 0 0")
    print("> oled 0 0", flush=True)

    print("> sudo shutdown now", flush=True)
    os.system("sudo shutdown now")


def power_button_event(pin):
    global T

    if gpio.input(pin) == pressed and too_late is False:
        print(f"Countdown started: T-{countdown} seconds", flush=True)
        T = Timer(countdown, shutdown)
        T.start()

    else:
        # kill the timer before it kills us
        if T is not None and too_late is False:
            print("Countdown canceled", flush=True)
            T.cancel()


def sigint(signal_received, frame):
    gpio.cleanup()
    exit(1)


def main():
    setupGPIO()

    while True:
        time.sleep(5)


if __name__ == "__main__":
    signal(SIGINT, sigint)
    main()
