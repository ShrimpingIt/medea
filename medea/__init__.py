from medea.agnostic import io, gc

OPEN="open"
CLOSE="close"
OBJECT="object"
ARRAY="object"
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

def dumpTokens(source):
    tokenizer = Tokenizer(source)
    tokenizer.dumpTokens()

def visit(source, callback):
    tokenizer = Tokenizer(source)
    for tok, val in tokenizer.tokenize():
        callback(tok, val)

def createFileFactory(path):
    def factory():
        return open(path, "rb")
    return factory

class Tokenizer():
    def __init__(self, sourceFactory, bufSize=512):
        self.sourceFactory = sourceFactory
        self.source = None
        self.bufPos = 0
        self.buf = bytearray(bufSize)

    def nextByte(self):
        byte = self.peekByte()
        self.bufPos += 1
        return byte

    def peekByte(self):
        if self.bufPos == len(self.buf):
            count = self.source.readinto(self.buf)
            if count == 0:
                return None
            else:
                self.bufPos = 0
        return self.buf[self.bufPos]

    def tokenize(self):
        self.source = self.sourceFactory()
        with self.source:
            yield from self.tokenizeValue()

    def generateFromNamed(self, names, generatorFactory):
        """Searches for the first item named 'key', tokenizes the
        value, then repeats the search from that point"""
        names = [bytes(name, 'ascii') for name in names]

        self.source = self.sourceFactory()
        with self.source:

            buf = self.buf
            bufPos = None
            bufLen = None

            namesLen = len(names)
            namesEnd = [len(name) - 1 for name in names]

            def refill():
                nonlocal buf, bufPos, bufLen
                count = self.source.readinto(buf)
                if count is 0:
                    raise StopIteration()
                else:
                    bufPos = 0
                    bufLen = len(buf)

            refill()

            while True:
                delimiter = buf[bufPos]
                bufPos += 1
                if bufPos == bufLen:
                    refill()
                if delimiter is singleQuoteByte or delimiter is doubleQuoteByte:
                    candidates = names
                    candidatesEnd = namesEnd
                    candidatesLen = namesLen
                    charPos = 0
                    match = None
                    while match is None and candidatesLen > 0:
                        candidatePos = candidatesLen
                        while match is None and candidatePos > 0:
                            candidatePos -= 1
                            if charPos == candidatesEnd[candidatePos]:
                                match = candidates[candidatePos]
                            elif candidates[candidatePos][charPos] != buf[bufPos]:
                                candidatesLen -= 1
                                if candidatesLen == 0:
                                    break
                                else:
                                    if candidates is names: # lazy duplicate list then excise candidate
                                        candidates = list(names)
                                        candidatesEnd = list(namesEnd)
                                    del candidates[candidatePos]
                                    del candidatesEnd[candidatePos]
                        charPos += 1
                        bufPos += 1
                        if bufPos == bufLen:
                            refill()
                    else: # either match found or candidates eliminated
                        if match is None:
                            continue
                    try:
                        if buf[bufPos] is not delimiter:
                            continue
                    finally:
                        bufPos += 1
                        if bufPos == bufLen:
                            refill()
                    while buf[bufPos] in spaceBytes:
                        bufPos += 1
                        if bufPos == bufLen:
                            refill()
                    try:
                        if buf[bufPos] is not colonByte:
                            continue
                    finally:
                        bufPos += 1
                        if bufPos == bufLen:
                            refill()
                    while buf[bufPos] in spaceBytes:
                        bufPos += 1
                        if bufPos == bufLen:
                            refill()
                    self.buf = buf
                    self.bufPos = bufPos
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