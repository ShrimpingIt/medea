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
    """Tokenizes a source of bytes, (e.g. a file, socket or byte array), as a JSON value (an object, array or primitive)

        A conformant byte generator accepts...
        * gen.send({not True})  READ the next character (next(gen) is equivalent to gen.send(None))
        * gen.send(True)        REPEAT the previous character

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

    def tokenizeValuesNamed(self, names, tokenGeneratorFactory, gen):
        try:
            """Tokenizes the value of each json key/value pair with key in ``names`` with provided tokenGeneratorFactory"""

            if type(names) == str:
                names = [names]

            names = [bytes(name, 'ascii') for name in names]
            namesLen = len(names)
            namesEnds = [len(name) - 1 for name in names]
            candidates = [True] * len(names)

            while True:
                delimiter = next(gen)
                if delimiter is singleQuoteByte or delimiter is doubleQuoteByte:
                    for namePos in range(namesLen):
                        candidates[namePos] = True # reset candidate keys
                    candidateCount = namesLen
                    charPos = 0
                    matchPos = None
                    while candidateCount > 0:
                        char = next(gen)
                        if char == delimiter:
                            break
                        else:
                            if matchPos is not None: # completed match, but not followed by delimiter
                                candidates[matchPos] = False # remove from candidates
                                candidateCount -= 1
                                matchPos = None
                            namePos = 0
                            for candidate in candidates:
                                if candidate:
                                    if names[namePos][charPos] == char:
                                        if namesEnds[namePos] == charPos:
                                            matchPos = namePos
                                    else:
                                        candidates[namePos] = False
                                        candidateCount -= 1
                                namePos += 1
                            charPos += 1
                    if matchPos is not None:
                        if (yield from self.skipSpace(gen)) == colonByte:
                            yield from self.skipSpace(gen)
                            yield from tokenGeneratorFactory(names[matchPos].decode('ascii'), gen)
        except StopIteration:
            return


    def tokenizeValue(self, gen, repeat=None):
        try:
            byte = gen.send(repeat)
            if byte is not None:
                if byte is openArrayByte:
                    return (yield from self.tokenizeArray(gen, True))
                elif byte is openObjectByte:
                    return (yield from self.tokenizeObject(gen, True))
                elif byte is singleQuoteByte or byte is doubleQuoteByte:
                    return (yield from self.tokenizeString(gen, True))
                elif byte in digitBytes or byte is minusByte:
                    return (yield from self.tokenizeNumber(gen, True))
                elif byte is firstTrueByte:
                    byte = (yield from self.skipLiteral(b"true", gen, True))
                    return (yield (BOOL, True))
                elif byte is firstFalseByte:
                    byte = (yield from self.skipLiteral(b"false", gen, True))
                    return (yield (BOOL, False))
                elif byte is firstNullByte:
                    byte = (yield from self.skipLiteral(b"null", gen, True))
                    return (yield (NUL, None))
                else:
                    raise AssertionError("Unexpected character {}".format(chr(gen.send(True))))
        except StopIteration:
            return

    def tokenizeArray(self, gen, repeat=None):
        try:
            if gen.send(repeat) != openArrayByte:
                raise AssertionError("Array should begin with [ not {}".format(chr(gen.send(True))))
            else:
                yield (OPEN, ARR)
            next(gen)
            while True:
                char = (yield from self.skipSpace(gen, repeat=True))
                if char is closeArrayByte:
                    yield (CLOSE, ARR)
                    next(gen)
                    return
                else:
                    yield from self.tokenizeValue(gen, repeat=True)
                char = (yield from self.skipSpace(gen, repeat=True))
                if char is commaByte:
                    char = next(gen)
                    continue
        except StopIteration:
            return

    def tokenizeObject(self, gen, repeat=None):
        try:
            if gen.send(repeat) != openObjectByte:
                raise AssertionError("Objects begin { not {}".format(chr(gen.send(True))))
            yield (OPEN, OBJ)
            byte = next(gen)
            while True:
                byte = (yield from self.skipSpace(gen, repeat=True))
                if byte is singleQuoteByte or byte is doubleQuoteByte:
                    yield from self.tokenizeKey(gen, repeat=True)
                    if (yield from self.skipSpace(gen, repeat=True)) is not colonByte:
                        raise AssertionError("Expecting : after key not {}".format(chr(gen.send(True))))
                    byte = (yield from self.skipSpace(gen)) # consume colon and following spaces
                    byte = (yield from self.tokenizeValue(gen, repeat=True))
                elif byte is closeObjectByte:
                    yield (CLOSE, OBJ)
                    return next(gen)
                else:
                    raise AssertionError("Expecting \" ' or ] not {}".format(chr(gen.send(True))))
                byte = (yield from self.skipSpace(gen, repeat=True))
                if byte is closeObjectByte:
                    yield (CLOSE, OBJ)
                    return next(gen)
                elif byte is commaByte:
                    next(gen)
                    continue
                else:
                    raise AssertionError("Pairs precede , or }} not {}".format(chr(gen.send(True))))
        except StopIteration:
            return

    def tokenizeString(self, gen, repeat=None):
        yield from self.tokenizeQuoted(STR, gen, repeat)

    def tokenizeQuoted(self, token, gen, repeat=None):
        try:
            delimiter = gen.send(repeat)
            if not (delimiter is singleQuoteByte or delimiter is doubleQuoteByte):
                raise AssertionError("{} starts with ' or \" not {}".format(token, chr(gen.send(True))))
            accumulator = bytearray()
            while True:
                byte = next(gen)
                if byte == delimiter:
                    yield (token, bytes(accumulator).decode('ascii'))
                    return next(gen)
                else:
                    accumulator.append(byte)
                    if byte is backslashByte:  # consume escaped char
                        accumulator.append(next(gen))
        except StopIteration:
            return

    def tokenizeKey(self, gen, repeat=None):
        yield from self.tokenizeQuoted(KEY, gen, repeat)

    def tokenizeNumber(self, gen, repeat=None):
        accumulator = []
        try:
            accumulator.append(gen.send(repeat))
            if accumulator[-1] is minusByte: # get next byte if prefixed with minus
                accumulator.append(next(gen))
            if not (accumulator[-1] in digitBytes):
                raise AssertionError("Numbers begin [0-9] after optional - sign not {}".format(chr(gen.send(True))))
            while True:
                byte = next(gen)
                if byte in digitBytes or byte in numberMetaBytes:
                    accumulator.append(byte)
                else:
                    break
        except StopIteration:
            pass
        finally:
            if len(accumulator):
                num = bytes(accumulator).decode('ascii')
                try:
                    num = int(num)
                except ValueError:
                    num = float(num)
                yield (NUM, num)
            else:
                raise AssertionError("Invalid number")
            return


    def skipSpace(self, gen, repeat=None):
        yield from ()
        try:
            byte = gen.send(repeat)
            while byte in spaceBytes:
                byte = next(gen)
            return byte
        except StopIteration:
            return

    def skipLiteral(self, bytesLike, gen, repeat=None):
        yield from ()
        try:
            byte = gen.send(repeat)
            for literalByte in bytesLike:
                if byte != literalByte:
                    raise AssertionError("No literal {}".format(bytesLike))
                byte = next(gen)
        except StopIteration:
            return byte
