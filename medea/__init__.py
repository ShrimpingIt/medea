OPEN = "open"
CLOSE = "close"
OBJECT = "object"
ARRAY = "array"
KEY = "key"
STRING = "string"
NUMBER = "number"
BOOLEAN = "boolean"
NULL = "null"

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

defaultBufferSize = 512


class MedeaError(AssertionError):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)


def dumpTokens(byteGeneratorFactory):
    tokenizer = Tokenizer(byteGeneratorFactory)
    tokenizer.dumpTokens()


def visit(byteGeneratorFactory, callback):
    tokenizer = Tokenizer(byteGeneratorFactory)
    for tok, val in tokenizer.tokenize():
        callback(tok, val)


class Tokenizer():
    """This class wraps a source of bytes, like a file or a socket, and can tokenize it as a JSON value, (object, array or primitive)
        on each call to tokenize, the byteGeneratorFactory is called to create a byteGenerator.
        A conformant byte generator accepts...
        * send(True) get a byte AND increment the stream position
        * send(False) to get a byte WITHOUT incrementing (a peek).

        Bytes are traversed for JSON symbols, triggering
        JSON VALUE EVENTS; pairs composed of (token, value) as follows.
        (OPEN, OBJECT)          : a new object, to be followed by a sequence of zero or more pairs like (KEY, keybytes) <JSON VALUE EVENTS>
        (CLOSE, OBJECT)         : completion of all the key/value pairs of previously opened object
        (OPEN, ARRAY)           : a new array, to be followed by a sequence of zero or more <JSON VALUE EVENTS>
        (CLOSE, ARRAY)
        (KEY, keyBytes)         : the next value which follows is a value embedded in an object with the given KEY
        (NUMBER, numberBytes)
        (BOOLEAN, booleanBytes)
        (STRING, stringBytes)
        (NULL, nullBytes)
    """

    def __init__(self, byteGeneratorFactory):
        self.byteGeneratorFactory = byteGeneratorFactory
        self.byteGenerator = None

    def unsetStream(self):
        if self.byteGenerator is not None:
            self.byteGenerator.throw(StopIteration)
            self.byteGenerator = None

    def resetStream(self):
        self.unsetStream()
        self.byteGenerator = self.byteGeneratorFactory()
        self.byteGenerator.send(None)

    # TODO inline calls, replacing with stream send instead
    def nextByte(self):
        return self.byteGenerator.send(True)  # get byte, increment position by 1

    # TODO inline calls, replacing with stream send instead
    def peekByte(self):
        return self.byteGenerator.send(False)  # get byte, do not change position

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
                        elif candidates[candidatePos][charPos] != self.peekByte():  # TODO cache result of this call
                            candidatesLen -= 1
                            if candidatesLen == 0:
                                break
                            else:
                                if candidates is names:  # lazy duplicate list then excise candidate
                                    candidates = list(names)
                                    candidatesEnds = list(namesEnds)
                                del candidates[candidatePos]
                                del candidatesEnds[candidatePos]
                    charPos += 1
                    self.nextByte()
                else:  # either match found or candidates eliminated
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
        yield (OPEN, ARRAY)
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
            yield (OPEN, OBJECT)
        while True:
            self.skipSpace()
            peek = self.peekByte()
            if peek is closeObjectByte:
                self.nextByte()
                return (yield (CLOSE, OBJECT))
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
        if not (delimiter is singleQuoteByte or delimiter is doubleQuoteByte):
            raise MedeaError("{} starts with ' or \"".format(token))
        accumulator = bytearray()
        peek = self.peekByte()
        while peek != delimiter:
            if peek is backslashByte:  # backslash escaping means consume two chars
                accumulator.append(self.nextByte())
            accumulator.append(self.nextByte())
            peek = self.peekByte()
        self.nextByte()  # drop delimiter
        yield (token, bytes(accumulator).decode('ascii'))

    def tokenizeKey(self):
        return self.tokenizeString(KEY)

    def tokenizeNumber(self):
        accumulator = []
        accumulator.append(self.nextByte())
        if accumulator[-1] is minusByte:
            accumulator.append(self.nextByte())
        if not (accumulator[-1] in digitBytes):
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
