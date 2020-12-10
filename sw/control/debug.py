# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import cv2

import numpy as np

from .common import IDebugDecorator
import logging as log
import imagezmq
import os

SENSOR_IMG_ARG = "sensor_img"


class CallbackDecorator(IDebugDecorator):
    def __init__(self, config: dict):
        super().__init__(config)
        self.callbacks = []

    def addCallback(self, fn):
        self.callbacks.append(fn)

    def decorate(self, args):
        for callback in self.callbacks:
            callback(args)


class X11Decorator(CallbackDecorator):
    def __init__(self, config: dict):
        super().__init__(config)

        cv2.namedWindow(self.config["windowName"])

    def decorate(self, args):
        super().decorate(args)

        cv2.imshow(self.config["windowName"], args[SENSOR_IMG_ARG])
        cv2.waitKey(1) & 0xFF

    def __del__(self):
        cv2.destroyAllWindows()


class MQDecorator(CallbackDecorator):
    def __init__(self, config: dict):
        super().__init__(config)

        self.width = w = self.config["width"]
        self.height = h = self.config["height"]
        self.uri = uri = self.config["uri"]
        log.info(f"Starting camera streaming w={w} h={h}")
        log.info(f"Sending to {uri}")

        #self.queue = None
        self.queue = imagezmq.ImageSender(connect_to=self.uri)
        self.iteration = 0

    def decorate(self, args):
        super().decorate(args)

        if self.queue is not None:
            self.iteration = self.iteration + 1

            # slow this down
            if self.iteration % 1 == 0:

                try:
                    image = args[SENSOR_IMG_ARG]
                    ret, jpg = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                    self.queue.send_jpg("moab", jpg)

                    #cv2.imwrite('/tmp/image.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    #cv2.imwrite('/tmp/image.jpg', jpg, [cv2.IMWRITE_JPEG_QUALITY, 70])

                except Exception as ex:
                    log.error(ex)

        else:
            log.warn("queue is none")

import os
import pathlib

class FileDecorator(CallbackDecorator):
    def __init__(self, config: dict):
        super().__init__(config)

        self.filename = self.config["filename"]

        # Create path to filename in case it doesn't exist
        dirname = os.path.dirname(self.filename)
        pathlib.Path(dirname).mkdir(parents=True, exist_ok=True)

        log.info(f"Saving current camera frame to {self.filename}")

    def decorate(self, args):
        super().decorate(args)

        try:
            image = args[SENSOR_IMG_ARG]
            cv2.imwrite(self.filename, image, [cv2.IMWRITE_JPEG_QUALITY, 70])

        except Exception as ex:
            log.error(ex)
