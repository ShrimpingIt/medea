import sys
import gc
from medea import defaultBufferSize
from medea.agnostic import socket, ssl, SocketTimeoutError

def generateResponseBytes(url, headers=None, timeout=1.0, buf=None, bufferSize=defaultBufferSize):
    _, _, host, path = url.split('/', 3)
    buf, bufferSize
    if buf is None:
        buf = bytearray(bufferSize)
    bufferSize = len(buf)
    try:
        addr = socket.getaddrinfo(host, 443)[0][-1]
    except IndexError:
        raise Exception("No Wifi")
    s = socket.socket()
    s.connect(addr)
    if hasattr(s, 'settimeout'):
        s.settimeout(timeout)
    try:
        s = ssl.wrap_socket(s)
        s.write(b'GET /')
        s.write(path.encode('ascii'))
        s.write(b' HTTP/1.1\r\nHost: ')
        s.write(host.encode('ascii'))
        s.write(b'\r\nUser-Agent: Cockle\r\n')
        if headers is not None:
            for header in headers:
                s.write(header)
        s.write(b'\r\n')
        remaining = None
        while True:
            if sys.implementation.name == "micropython":
                if remaining is None or bufferSize < remaining:
                    count = s.readinto(buf)
                else: # read into memoryview shorter than backing buffer
                    count = s.readinto(memoryview(buf)[:remaining])
            else:
                if remaining is None or bufferSize < remaining:
                    count = s.read(bufferSize, buf)
                else:
                    count = s.read(remaining, memoryview(buf)[:remaining])
            pos = 0
            if count > 0:
                while pos < count:
                    msg = yield buf[pos]
                    if type(msg) is int: # allow signalling content length
                        remaining = msg + 1 # CH mystifying off-by-one error
                        msg = True # byte will be replayed
                    if msg is not True:
                        pos += 1
                        if remaining is not None:
                            remaining -= 1
            else:
                break
    except StopIteration:
        pass # this is OK, expected
    except GeneratorExit:
        pass  # this is OK, expected
    except SocketTimeoutError:
        pass  # gave up awaiting for more from the socket
    except BaseException as e:
        print("Unexpected exception")
        print(e)
        raise
    finally:
        s.close()

def processHttpHeaders(stream):
    contentLength = None

    key = b"content-length: "
    keyLen = len(key)
    keyPos = 0

    # extract content-length header
    while contentLength is None:
        byte = next(stream)
        while chr(byte).lower() == chr(key[keyPos]): # bytes continue to match
            byte = next(stream)
            keyPos += 1
            if keyPos == keyLen:
                char = chr(byte)
                numberString = ""
                while not char.isspace():
                    numberString += char
                    char = chr(next(stream))
                contentLength = int(numberString)
                break
        else:
            keyPos = 0

    # consume bytes until double newline (end of header)
    newlineCount = 0
    while True:
        if next(stream) == ord('\r') and next(stream) == ord('\n'):
            newlineCount += 1
        else:
            newlineCount = 0
        if newlineCount == 2:
            break

    return contentLength

def generateContentBytes(*a, **k):
    """Creates a HTTPS stream, parses the HTTP header to get the content-length,
    skips to the start of the HTTP content section, then returns a derived generator
    which stops iteration after the proper count of content bytes"""
    byteGenerator = generateResponseBytes(*a, **k)
    contentLength = processHttpHeaders(byteGenerator)
    byteGenerator.send(contentLength)
    yield from byteGenerator
