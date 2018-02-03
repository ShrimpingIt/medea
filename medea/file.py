from medea import defaultBufferSize


def createFileByteGeneratorFactory(path, buffer=None):
    """
    Invoke with next(gen) or gen.send(True) to consume byte from stream (read AND increment)
    Invoke with gen.send(False) to peek at byte (read WITHOUT incrementing)
    """
    def byteGeneratorFactory():
        nonlocal buffer
        if buffer is None:
            buffer = bytearray(defaultBufferSize)
        with open(path, "rb") as f:
            consumed = False
            while True:
                count = f.readinto(buffer)
                pos = 0
                if count > 0:
                    while pos < count:
                        nextByte = buffer[pos]
                        if consumed is not False:
                            pos += 1
                        consumed = yield nextByte
                else:
                    break
    return byteGeneratorFactory