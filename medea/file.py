from medea import defaultBufferSize,Tokenizer

def generateFileBytes(path, buf=None):
    """
    Invoke with next(gen) or gen.send(True) to consume byte from stream (read AND increment)
    Invoke with gen.send(False) to peek at byte (read WITHOUT incrementing)
    """
    if buf is None:
        buf = bytearray(defaultBufferSize)
    with open(path, "rb") as f:
        while True:
            count = f.readinto(buf)
            pos = 0
            if count > 0:
                while pos < count:
                    if (yield buf[pos]) is not True:
                        pos += 1
            else:
                break


def tokenizeFile(path):
    tokenizer = Tokenizer()
    yield from tokenizer.tokenizeValue(generateFileBytes(path))

