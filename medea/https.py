import sys
from medea import defaultBufferSize
from medea.agnostic import socket, ssl, SocketTimeoutError

def createHttpsByteGeneratorFactory(url, headers=None, timeout=1.0, buffer=None):
    def byteGeneratorFactory():
        _, _, host, path = url.split('/', 3)
        nonlocal buffer
        if buffer is None:
            buffer = bytearray(defaultBufferSize)
        addr = socket.getaddrinfo(host, 443)[0][-1]
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
            consumed = False

            while True:
                if sys.implementation.name == "micropython":
                    count = s.readinto(buffer)
                else:
                    count = s.read(len(buffer), buffer)
                pos = 0
                if count > 0:
                    while pos < count:
                        nextByte = buffer[pos]
                        if consumed:
                            pos += 1
                        consumed = yield nextByte
                        if consumed is None:
                            consumed = True
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
    return byteGeneratorFactory


def processHttpHeaders(stream):
    contentLength = None

    key = "content-length: "
    keyLen = len(key)
    keyPos = 0

    # extract content-length header
    while contentLength is None:
        byte = next(stream)
        while chr(byte) == key[keyPos]: # bytes continue to match
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


def createHttpsContentByteGeneratorFactory(*a, **k):
    """Creates a HTTPS stream, parses the HTTP header to get the content-length,
    skips to the start of the HTTP content section, then returns a derived generator
    which stops iteration after the proper count of content bytes"""
    upstreamGeneratorFactory = createHttpsByteGeneratorFactory(*a, **k)
    def byteGeneratorFactory():
        byteGenerator = upstreamGeneratorFactory()
        contentLength = processHttpHeaders(byteGenerator)
        try:
            value = next(byteGenerator)
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