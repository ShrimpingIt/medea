from medea.agnostic import *

OPEN = b"open"
CLOSE = b"close"
OBJ = b"object"
ARR = b"array"
KEY = b"key"
STR = b"string"
NUM = b"number"
BOOL = b"boolean"
NUL = b"null"

singleQuoteByte = const(39)     # ord("'")
doubleQuoteByte = const(34)     # ord('"')
backslashByte = const(92)       # ord('\\')
openObjectByte = const(123)     # ord('{')
closeObjectByte = const(125)    # ord('}')
openArrayByte = const(91)       # ord('[')
closeArrayByte = const(93)      # ord(']')
colonByte = const(58)           # ord(':')
commaByte = const(44)           # ord(',')
firstTrueByte = const(116)      # ord('t')
firstFalseByte = const(102)     # ord('f')
firstNullByte = const(110)      # ord('n')
minusByte = const(45)           # ord('-')

numberMetaBytes = b'.xeEb' # non-digit characters allowable in numbers
spaceBytes = b' \n\t\r'
digitBytes = b'0123456789'

defaultBufferSize = 512

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
            print("Terminating byteGenerator with StopIteration")
            self.byteGenerator.throw(StopIteration)
            self.byteGenerator = None

    def resetStream(self):
        try:
            self.unsetStream()
            self.byteGenerator = self.byteGeneratorFactory()
            self.byteGenerator.send(None)
        except StopIteration:
            return

    def tokenize(self, gen=None):
        if gen is None:
            self.resetStream()
            gen = self.byteGenerator
        yield from self.tokenizeValue(gen)

    def generateFromNamed(self, names, tokenGeneratorFactory, gen=None):
        try:
            """For each json key/value pair with key in ``names``,
            tokenizes the value using tokenGeneratorFactory"""
            self.resetStream()
            if gen is None:
                gen = self.byteGenerator

            names = [bytes(name, 'ascii') for name in names]
            namesLen = len(names)
            namesEnds = [len(name) - 1 for name in names]

            while True:
                delimiter = gen.send(True)
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
                            elif candidates[candidatePos][charPos] != gen.send(False):  # TODO cache result of this call
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
                        gen.send(True)
                    else:  # either match found or candidates eliminated
                        if match is None:
                            continue
                    try:
                        if gen.send(False) is not delimiter:
                            continue
                    finally:
                        gen.send(True)
                    while gen.send(False) in spaceBytes:
                        gen.send(True)
                    try:
                        if gen.send(False) is not colonByte:
                            continue
                    finally:
                        gen.send(True)
                    while gen.send(False) in spaceBytes:
                        gen.send(True)
                    yield from tokenGeneratorFactory(match.decode('ascii'))
        except StopIteration:
            return

    def tokenizeValuesNamed(self, names, gen=None):
        if type(names) is str:
            names = [names]

        def generatorFactory(name):
            yield from self.tokenizeValue(gen)

        return self.generateFromNamed(names, generatorFactory)

    def dumpTokens(self, gen=None):
        for token in self.tokenize(gen):
            print(token)

    def tokenizeValue(self, gen=None):
        if gen is None:
            gen = self.byteGenerator
        self.skipSpace()
        byte = gen.send(False)
        if byte is not None:
            if byte is openArrayByte:
                return (yield from self.tokenizeArray(gen))
            elif byte is openObjectByte:
                return (yield from self.tokenizeObject(gen))
            elif byte is singleQuoteByte or byte is doubleQuoteByte:
                return (yield from self.tokenizeString(STR, gen))
            elif byte in digitBytes or byte is minusByte:
                return (yield from self.tokenizeNumber(gen))
            elif byte is firstTrueByte:
                self.skipLiteral(b"true")
                return (yield (BOOL, True))
            elif byte is firstFalseByte:
                self.skipLiteral(b"false")
                return (yield (BOOL, False))
            elif byte is firstNullByte:
                self.skipLiteral(b"null")
                return (yield (NUL, None))
            else:
                raise AssertionError("Unexpected character {}".format(byte))

    def tokenizeArray(self, gen=None):
        if gen is None:
            gen = self.byteGenerator
        if gen.send(True) != openArrayByte:
            raise AssertionError("Array should begin with [")
        yield (OPEN, ARR)
        while True:
            self.skipSpace()
            char = gen.send(False)
            if char is closeArrayByte:
                gen.send(True)
                return (yield (CLOSE, ARR))
            else:
                yield from self.tokenizeValue(gen)
                if gen.send(False) is commaByte:
                    gen.send(True)
                    continue

    def tokenizeObject(self, gen=None):
        if gen is None:
            gen = self.byteGenerator
        if gen.send(True) != openObjectByte:
            raise AssertionError("Objects begin {")
        else:
            yield (OPEN, OBJ)
        while True:
            self.skipSpace()
            peek = gen.send(False)
            if peek is closeObjectByte:
                gen.send(True)
                return (yield (CLOSE, OBJ))
            elif peek is singleQuoteByte or peek is doubleQuoteByte:
                yield from self.tokenizeKey(gen)
                self.skipSpace()
                if gen.send(True) is not colonByte:
                    raise AssertionError("Expecting : after key")
                self.skipSpace()
                yield from self.tokenizeValue(gen)
            else:
                raise AssertionError("Keys begin \" or '")

            self.skipSpace()
            peek = gen.send(False)
            if peek is closeObjectByte:
                pass
            elif peek is commaByte:
                gen.send(True)
            else:
                raise AssertionError("Pairs precede , or }")

    def tokenizeString(self, token, gen=None):
        if gen is None:
            gen = self.byteGenerator
        delimiter = gen.send(True)
        if not (delimiter is singleQuoteByte or delimiter is doubleQuoteByte):
            raise AssertionError("{} starts with ' or \"".format(token))
        accumulator = bytearray()
        peek = gen.send(False)
        while peek != delimiter:
            if peek is backslashByte:  # backslash escaping means consume two chars
                accumulator.append(gen.send(True))
            accumulator.append(gen.send(True))
            peek = gen.send(False)
        gen.send(True)  # drop delimiter
        yield (token, bytes(accumulator).decode('ascii'))

    def tokenizeKey(self, gen=None):
        return self.tokenizeString(KEY, gen)

    def tokenizeNumber(self, gen=None):
        if gen is None:
            gen = self.byteGenerator
        accumulator = []
        accumulator.append(gen.send(True))
        if accumulator[-1] is minusByte:
            accumulator.append(gen.send(True))
        if not (accumulator[-1] in digitBytes):
            raise AssertionError("Numbers begin [0-9] after optional - sign")
        while True:
            peek = gen.send(False)
            if peek in digitBytes or peek in numberMetaBytes:
                accumulator.append(gen.send(True))
            else:
                if len(accumulator):
                    yield (NUM, bytes(accumulator).decode('ascii'))
                    break
                else:
                    raise AssertionError("Invalid number")

    def skipSpace(self, gen=None):  # TODO CH make consistent with skipLiteral - eliminate empty yield syntax
        if gen is None:
            gen = self.byteGenerator
        while gen.send(False) in spaceBytes:
            gen.send(True)

    def skipLiteral(self, bytesLike, gen=None):
        if gen is None:
            gen = self.byteGenerator
        for literalByte in bytesLike:
            if gen.send(True) != literalByte:
                raise AssertionError("No literal {}".format(bytesLike))
