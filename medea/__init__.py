from medea.agnostic import io, gc, socket, ssl

OPEN="open"
CLOSE="close"
OBJECT="object"
ARRAY="array"
KEY="key"
STRING="string"
NUMBER="number"
BOOLEAN="boolean"
NULL="null"

singleQuoteByte = ord("'")
doubleQuoteByte = ord('"')
backslashByte = ord("\\")
openObjectByte = ord('{')
closeObjectByte = ord('}')
openArrayByte = ord('[')
closeArrayByte = ord(']')
colonByte = ord(':')
commaByte = ord(',')
firstTrueByte = ord('t')
firstFalseByte = ord('f')
firstNullByte = ord('n')
minusByte = ord('-')

numberMetaBytes = b'.xeEb'
spaceBytes = b' \n\t\r'
digitBytes = b'0123456789'

class MedeaError(AssertionError):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)

def dumpTokens(streamGenerator):
    tokenizer = Tokenizer(streamGenerator)
    tokenizer.dumpTokens()

def visit(streamGenerator, callback):
    tokenizer = Tokenizer(streamGenerator)
    for tok, val in tokenizer.tokenize():
        callback(tok, val)

defaultBufferSize = 512


def createFileStreamGenerator(path, buffer=None):
    "A generator you can send False to peek (read without incrementing), None or True increments by default"
    def fileStreamGenerator():
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
                        if consumed:
                            pos += 1
                        consumed = yield nextByte
                        if consumed is None:
                            consumed = True
                else:
                    break
    return fileStreamGenerator

def createHttpsStreamGenerator(url, headers=None, timeout=1.0, buffer=None):
    def httpsStreamGenerator():
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
            s.write('GET /{} HTTP/1.1\r\nHost: {}\r\nUser-Agent: Cockle\r\n'.format(path, host).encode('ascii'))
            #s.write(b'GET /{} HTTP/1.1\r\nHost: {}\r\nUser-Agent: Cockle\r\n'.format(path, host))
            if headers is not None:
                s.write(headers)
            s.write(b'\r\n')
            consumed = False

            while True:
                #count = s.readinto(buffer)
                count = s.read(len(buffer), buffer=buffer)
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
        finally:
            s.close()
    return httpsStreamGenerator

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

def createHttpsContentStreamGenerator(*a, **k):
    rawStreamGenerator = createHttpsStreamGenerator(*a, **k)
    def httpsContentStreamGenerator():
        rawStream = rawStreamGenerator()
        contentLength = processHttpHeaders(rawStream)
        # TODO consider terminating rawStream as below based on known content length
        # TODO however, might be a bug in the send/next behaviour if 'relaying' yield
        """
        def streamFactory():
            for pos in range(contentLength):
                yield next(rawStream)
            rawStream.throw(StopIteration)
        return streamFactory()
        """
        return rawStream
    return httpsContentStreamGenerator

twitterBaseUrl = "https://api.twitter.com/1.1/"

def createTwitterHeaders():
    from medea.auth import bearerHeader
    return bearerHeader

def createTwitterUrl(apiPath, getParams):
    url = twitterBaseUrl + apiPath + "?"
    url += "&".join(["{}={}".format(key, value) for key,value in getParams.items()])
    gc.collect()
    return url

def createTwitterTimelineUrl(screen_name, count=1, **k):
    params = dict(
        screen_name=screen_name,
        count=count,
        include_rts = "false",
    )
    params.update(k)
    return createTwitterUrl("statuses/user_timeline.json", params)

def createTwitterSearchUrl(text, count=1, extraGetParams=None, *a, **k):
    params = dict(
        q=text,
        count=count,
        include_entities = "false",
    )
    params.update(k)
    return createTwitterUrl("search/tweets.json", params)


class Tokenizer():
    """This class wraps a source of bytes, like a file or a socket, and can tokenize it as a JSON value, (object, array or primitive)
        on each call to tokenize, the sourceFactory is called to initialise a new source, which must implement the 'readinto()' method.
        Bytes are then read in buffers of up to bufSize characters, which are traversed for JSON symbols, triggering JSON value events
        pairs composed of (token, value) pairs as follows.
        (OPEN, OBJECT)          : a new object, to be followed by a sequence of zero or more pairs like (KEY, keybytes) <JSON VALUE EVENTS>
        (CLOSE, OBJECT)         : completion of all the key/value pairs of previously opened object
        (OPEN, ARRAY)           : a new array, to be followed by a sequence of zero or more <JSON VALUE EVENTS>
        (CLOSE, ARRAY)
        (KEY, keyBytes)         : the next value which follows is a value embedded in an object
        (NUMBER, numberBytes)
        (BOOLEAN, booleanBytes)
        (STRING, stringBytes)
        (NULL, nullBytes)
    """

    def __init__(self, streamGenerator):
        self.streamGenerator = streamGenerator
        self.stream = None

    def unsetStream(self):
        if self.stream is not None:
            self.stream.throw(StopIteration)
            self.stream = None

    def resetStream(self):
        self.unsetStream()
        self.stream = self.streamGenerator()
        self.stream.send(None)

    def nextByte(self):
        return self.stream.send(True) # get byte, increment position by 1

    def peekByte(self):
        return self.stream.send(False) # get byte, do not change position

    def tokenize(self):
        self.resetStream()
        yield from self.tokenizeValue()

    def generateFromNamed(self, names, generatorFactory):
        """Searches for the first item named 'key', tokenizes the
        value, then repeats the search from that point"""
        self.resetStream()

        names = [bytes(name, 'ascii') for name in names]
        namesLen = len(names)
        namesEnds = [len(name) - 1 for name in names]

        while True:
            delimiter = self.nextByte()
            if delimiter is singleQuoteByte or delimiter is doubleQuoteByte:
                candidates = names
                candidatesEnds = namesEnds
                candidatesLen = namesLen
                charPos = 0
                match = None
                while match is None and candidatesLen > 0:
                    candidatePos = candidatesLen
                    while match is None and candidatePos > 0:
                        candidatePos -= 1
                        if charPos == candidatesEnds[candidatePos]:
                            match = candidates[candidatePos]
                        elif candidates[candidatePos][charPos] != self.peekByte(): # TODO cache result of this call
                            candidatesLen -= 1
                            if candidatesLen == 0:
                                break
                            else:
                                if candidates is names: # lazy duplicate list then excise candidate
                                    candidates = list(names)
                                    candidatesEnds = list(namesEnds)
                                del candidates[candidatePos]
                                del candidatesEnds[candidatePos]
                    charPos += 1
                    self.nextByte()
                else: # either match found or candidates eliminated
                    if match is None:
                        continue
                try:
                    if self.peekByte() is not delimiter:
                        continue
                finally:
                    self.nextByte()
                while self.peekByte() in spaceBytes:
                    self.nextByte()
                try:
                    if self.peekByte() is not colonByte:
                        continue
                finally:
                    self.nextByte()
                while self.peekByte() in spaceBytes:
                    self.nextByte()
                yield from generatorFactory(match.decode('ascii'))

    def tokenizeValuesNamed(self, names):
        if type(names) is str:
            names = [names]
        def generatorFactory(name):
            yield from self.tokenizeValue()
        return self.generateFromNamed(names, generatorFactory)

    def dumpTokens(self):
        for token in self.tokenize():
            print(token)

    def tokenizeValue(self):
        self.skipSpace()
        byte = self.peekByte()
        if byte is not None:
            if byte is openArrayByte:
                return (yield from self.tokenizeArray())
            elif byte is openObjectByte:
                return (yield from self.tokenizeObject())
            elif byte is singleQuoteByte or byte is doubleQuoteByte:
                return (yield from self.tokenizeString())
            elif byte in digitBytes or byte is minusByte:
                return (yield from self.tokenizeNumber())
            elif byte is firstTrueByte:
                self.skipLiteral(b"true")
                return (yield (BOOLEAN, True))
            elif byte is firstFalseByte:
                self.skipLiteral(b"false")
                return (yield (BOOLEAN, False))
            elif byte is firstNullByte:
                self.skipLiteral(b"null")
                return (yield (NULL, None))
            else:
                raise MedeaError("Unexpected character {}".format(byte))

    def tokenizeArray(self):
        if self.nextByte() != openArrayByte:
            raise MedeaError("Array should begin with [")
        yield (OPEN,ARRAY)
        while True:
            self.skipSpace()
            char = self.peekByte()
            if char is closeArrayByte:
                self.nextByte()
                return (yield (CLOSE, ARRAY))
            else:
                yield from self.tokenizeValue()
                if self.peekByte() is commaByte:
                    self.nextByte()
                    continue

    def tokenizeObject(self):
        if self.nextByte() != openObjectByte:
            raise MedeaError("Objects begin {")
        else:
            yield (OPEN,OBJECT)
        while True:
            self.skipSpace()
            peek = self.peekByte()
            if peek is closeObjectByte:
                self.nextByte()
                return (yield (CLOSE,OBJECT))
            elif peek is singleQuoteByte or peek is doubleQuoteByte:
                yield from self.tokenizeKey()
                self.skipSpace()
                if self.nextByte() is not colonByte:
                    raise MedeaError("Expecting : after key")
                self.skipSpace()
                yield from self.tokenizeValue()
            else:
                raise MedeaError("Keys begin \" or '")

            self.skipSpace()
            peek = self.peekByte()
            if peek is closeObjectByte:
                pass
            elif peek is commaByte:
                self.nextByte()
            else:
                raise MedeaError("Pairs precede , or }")

    def tokenizeString(self, token=STRING):
        delimiter = self.nextByte()
        if not(delimiter is singleQuoteByte or delimiter is doubleQuoteByte):
            raise MedeaError("{} starts with ' or \"".format(token))
        accumulator = bytearray()
        peek = self.peekByte()
        while peek != delimiter:
            if peek is backslashByte: # backslash escaping means consume two chars
                accumulator.append(self.nextByte())
            accumulator.append(self.nextByte())
            peek = self.peekByte()
        self.nextByte() # drop delimiter
        yield (token, bytes(accumulator).decode('ascii'))

    def tokenizeKey(self):
        return self.tokenizeString(KEY)

    def tokenizeNumber(self):
        accumulator = []
        accumulator.append(self.nextByte())
        if accumulator[-1] is minusByte:
            accumulator.append(self.nextByte())
        if not(accumulator[-1] in digitBytes):
            raise MedeaError("Numbers begin [0-9] after optional - sign")
        while True:
            peek = self.peekByte()
            if peek in digitBytes or peek in numberMetaBytes:
                accumulator.append(self.nextByte())
            else:
                if len(accumulator):
                    yield (NUMBER, bytes(accumulator).decode('ascii'))
                    break
                else:
                    raise MedeaError("Invalid number")

    def skipSpace(self):  # TODO CH make consistent with skipLiteral - eliminate empty yield syntax
        while self.peekByte() in spaceBytes:
            self.nextByte()

    def skipLiteral(self, bytesLike):
        for literalByte in bytesLike:
            if self.nextByte() != literalByte:
                raise MedeaError("Expecting keyword {}" + bytesLike)