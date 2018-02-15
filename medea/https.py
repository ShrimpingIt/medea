import sys
import gc
from medea import defaultBufferSize
from medea.agnostic import socket, ssl, SocketTimeoutError

def createByteGeneratorFactory(url, headers=None, timeout=1.0, buffer=None, bufferSize=defaultBufferSize):
    def byteGeneratorFactory():
        _, _, host, path = url.split('/', 3)
        nonlocal buffer, bufferSize
        if buffer is None:
            buffer = bytearray(bufferSize)
        bufferSize = len(buffer)
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
            msg = False

            remaining = None
            while True:
                if sys.implementation.name == "micropython":
                    if remaining is None or bufferSize < remaining:
                        count = s.readinto(buffer)
                    else: # read into memoryview shorter than backing buffer
                        count = s.readinto(memoryview(buffer)[:remaining])
                else:
                    if remaining is None or bufferSize < remaining:
                        count = s.read(bufferSize, buffer)
                    else:
                        count = s.read(remaining, memoryview(buffer)[:remaining])
                pos = 0
                if count > 0:
                    while pos < count:
                        nextByte = buffer[pos]
                        if msg:
                            pos += 1
                            if remaining is not None:
                                remaining -= 1
                        msg = yield nextByte
                        if msg is None:
                            msg = True
                        else:
                            if msg is True or msg is False:
                                pass
                            elif type(msg) is int: # allow signalling content length
                                remaining = msg
                                msg = False # byte will be replayed
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
        """
        finally:
            s.close()
        """
    return byteGeneratorFactory


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


def createContentByteGeneratorFactory(*a, **k):
    """Creates a HTTPS stream, parses the HTTP header to get the content-length,
    skips to the start of the HTTP content section, then returns a derived generator
    which stops iteration after the proper count of content bytes"""
    upstreamGeneratorFactory = createByteGeneratorFactory(*a, **k)
    def byteGeneratorFactory():
        """Yield+send delegation Based on answer shared at https://stackoverflow.com/questions/48584098/yield-based-equivalent-to-python3-yield-from-delegation-without-losing-send"""
        byteGenerator = upstreamGeneratorFactory()
        contentLength = processHttpHeaders(byteGenerator)
        try:
            value = byteGenerator.send(contentLength)  # signal byte count remaining
        except StopIteration:
            pass
        else:
            contentPos = 0
            while True:
                try:
                    sent = yield value
                    if sent is not False:
                        contentPos += 1
                        if contentPos >= contentLength:
                            break
                except GeneratorExit:
                    byteGenerator.close()
                    raise
                except BaseException:
                    try:
                        value = byteGenerator.throw(*sys.exc_info())
                    except StopIteration:
                        break
                else:
                    try:
                        value = byteGenerator.send(sent)
                    except StopIteration:
                        break
    return byteGeneratorFactory
