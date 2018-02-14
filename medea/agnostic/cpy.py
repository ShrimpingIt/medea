import os
import io
import socket
import ssl
import gc

SocketTimeoutError = socket.timeout


def const(val):
    return val


from time import sleep, time


def ticks_ms():
    return int(time() * 1000)


def ticks_diff(a, b):
    return a - b