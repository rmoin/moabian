#!/usr/bin/env python3
import cv2
import imagezmq
import numpy as np


##
## Code based on https://github.com/jeffbass/imagezmq/blob/master/docs/advanced-pub-sub.rst
##

# Incoming
hub = imagezmq.ImageHub(open_port='tcp://*:5555')       # listen on port 5555
#hub = imagezmq.ImageHub()

# Outgoing
to_web_server = imagezmq.ImageSender(connect_to='tcp://*:5566', REQ_REP = False)

i = 0;

while True:
    i = i + 1

    if i % 10 == 0:
        print(f'{i:3d} ', end='', flush=True)

    if i % 100 == 0:
        print("", flush=True)

    name, jpg= hub.recv_jpg()
    hub.send_reply(b'OK')
    jpgn = np.frombuffer(jpg, dtype='uint8')
    to_web_server.send_jpg(name, jpg)


