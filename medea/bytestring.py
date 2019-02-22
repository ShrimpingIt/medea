"""Defines canonical behaviour for medea byteGenerators
This module creates a byteGenerator from a bytes byteString
"""

def generateStringBytes(byteString):
    """
    Invoke with gen.send(False) to read previous byte (NO increment ONLY read)
    Invoke with gen.send(non-False) e.g. next(gen) to move cursor to next byte (DO increment AND read)
    """
    if type(byteString) == str:
        byteString = byteString.encode("ascii")
    pos = 0
    count = len(byteString)
    while pos < count:
        if (yield byteString[pos]) is None:
            pos += 1
