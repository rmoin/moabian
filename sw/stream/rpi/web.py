#!/usr/bin/env python3
import os
import cv2
import sys
import socket
import imagezmq
from werkzeug.wrappers import Request, Response
from werkzeug.datastructures import Headers
from werkzeug.serving import run_simple

# 0MQ #1: source --> hub
# 0MQ #2: hub --> web server
# web server (on GET request) --> send JPG frames

import numpy as np

def sendImagesToWeb():
    receiver = imagezmq.ImageHub(open_port='tcp://127.0.0.1:5566', REQ_REP = False)

    while True:
        (name, jpg_buffer) = receiver.recv_jpg()

        length = len(jpg_buffer)
        s = 'Content-Type: image/jpeg\r\n'
        s = s + f'Content-Length: {length}\r\n'
        s = s + '\r\n'
        s = s.encode('UTF-8')

        yield b'--frame\r\n' + s + jpg_buffer + b'\r\n'

        # https://github.com/jacksonliam/mjpg-streamer/blob/master/mjpg-streamer-experimental/plugins/output_http/httpd.c
        #yield b'--frame\r\nContent-Type:image/jpeg\r\n\r\n'+jpg_buffer+b'\r\n'

@Request.application
def application(request):
    print("got request")
    d = Headers()
    d.add('Connection', 'close')
    d.add('Age', 0)
    d.add('Cache-Control', 'no-cache,no-store,must-revalidate,pre-check=0,post-check=0,max-age=0')
    d.add('Pragma', 'no-cache')
    d.add('Server', 'Moab v2.5')
    #d.add('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
    #return Response(sendImagesToWeb(), headers=d)
    return Response(sendImagesToWeb(), headers=d, mimetype='multipart/x-mixed-replace; boundary=frame')

def getHostIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('1.1.1.1', 1))
    local_ip = s.getsockname()[0]
    return local_ip

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    hostname = socket.gethostname()

    ip = getHostIP()
    print(f"Open browser to http://{ip}:{port}")
    run_simple(ip, port, application)

# source.py (MQDecorator in Control) -->
# sink.py ==> web container: listening to everyone (
# web container publishes the data on index.html (via mpeg) over port 8000
