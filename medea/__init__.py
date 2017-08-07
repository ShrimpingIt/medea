from medea.agnostic import io, gc

OPEN="open"
CLOSE="close"
KEY="key"
STRING="string"
NUMBER="number"
BOOLEAN="boolean"
NULL="null"

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

class Tokenizer():
    def __init__(self, source):
        self.source = source
        self.bufSize = 512
        self.bufPos = 0
        self.buf = ""

    def nextChar(self):
        char = self.peekChar()
        self.bufPos += 1
        return char

    def peekChar(self):
        if self.bufPos == len(self.buf):
            self.buf = self.source.read(self.bufSize)
            if self.buf is "":
                return None
            else:
                self.bufPos = 0
        return self.buf[self.bufPos]

    def tokenize(self):
        yield from self.tokenizeValue()

    def tokenizeValuesNamed(self, key):
        """Searches for the first item named 'key', tokenizes the
        value, then repeats the search from that point"""
        buf = None
        bufPos = None
        bufLen = None

        def refill():
            nonlocal buf, bufPos, bufLen
            buf = self.source.read(self.bufSize)
            if buf is "":
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
            if delimiter is '"' or delimiter is "'":
                for char in key:
                    try:
                        if buf[bufPos] != char:
                            break
                        else:
                            pass
                    finally:
                        bufPos += 1
                        if bufPos == bufLen:
                            refill()
                else:
                    try:
                        if buf[bufPos] is not delimiter:
                            continue
                    finally:
                        bufPos += 1
                        if bufPos == bufLen:
                            refill()
                    while buf[bufPos].isspace():
                        bufPos += 1
                        if bufPos == bufLen:
                            refill()
                    try:
                        if buf[bufPos] is not ":":
                            continue
                    finally:
                        bufPos += 1
                        if bufPos == bufLen:
                            refill()
                    while buf[bufPos].isspace():
                        bufPos += 1
                        if bufPos == bufLen:
                            refill()
                    self.buf = buf
                    self.bufPos = bufPos
                    yield from self.tokenizeValue()

    def dumpTokens(self):
        for token in self.tokenize():
            print(token)

    def tokenizeValue(self):
        self.skipSpace()
        char = self.peekChar()
        if char is not None:
            if char is "[":
                return (yield from self.tokenizeArray())
            elif char is "{":
                return (yield from self.tokenizeObject())
            elif char is '"' or char is "'":
                return (yield from self.tokenizeString())
            elif char.isdigit() or char is "-":
                return (yield from self.tokenizeNumber())
            elif char is "t":
                self.skipLiteral("true")
                return (yield (BOOLEAN, True))
            elif char is "f":
                self.skipLiteral("false")
                return (yield (BOOLEAN, False))
            elif char is "n":
                self.skipLiteral("null")
                return (yield (NULL, None))
            else:
                raise MedeaError("Unexpected character {}".format(char))

    def tokenizeArray(self):
        if self.nextChar() != "[":
            raise MedeaError("Array should begin with [")
        yield (OPEN,"[")
        while True:
            self.skipSpace()
            char = self.peekChar()
            if char is "]":
                self.nextChar()
                return (yield (CLOSE, "]"))
            else:
                yield from self.tokenizeValue()
                if self.peekChar() is ",":
                    self.nextChar()
                    continue

    def tokenizeObject(self):
        if self.nextChar() !="{":
            raise MedeaError("Objects begin {")
        else:
            yield (OPEN,"{")
        while True:
            self.skipSpace()
            peek = self.peekChar()
            if peek is "}":
                self.nextChar()
                return (yield (CLOSE,"}"))
            elif peek is "'" or peek is '"' :
                # BEGIN 'tokenizePair'
                yield from self.tokenizeKey()
                self.skipSpace()
                if self.nextChar() != ":":
                    raise MedeaError("Expecting : after key")
                self.skipSpace()
                yield from self.tokenizeValue()
                # END'tokenizePair'
            else:
                raise MedeaError("Keys begin \" or '")

            self.skipSpace()
            peek = self.peekChar()
            if peek is  "}":
                pass
            elif peek is ",":
                self.nextChar()
            else:
                raise MedeaError("Pairs precede , or }")

    def tokenizeString(self, token=STRING):
        delimiter = self.nextChar()
        if not(delimiter is "'" or delimiter is '"'):
            raise MedeaError("{} starts with ' or \"".format(token))
        accumulator = []
        peek = self.peekChar()
        while peek != delimiter:
            if peek is "\\": # backslash escaping means consume two chars
                accumulator.append(self.nextChar())
            accumulator.append(self.nextChar())
            peek = self.peekChar()
        self.nextChar() # drop delimiter
        string = "".join(accumulator)
        yield (token, string)

    def tokenizeKey(self):
        return self.tokenizeString(KEY)

    def tokenizeNumber(self):
        accumulator = []
        accumulator.append(self.nextChar())
        if accumulator[-1]is'-':
            accumulator.append(self.nextChar())
        if not(accumulator[-1].isdigit()):
            raise MedeaError("Numbers begin [0-9] after optional - sign")
        while True:
            peek = self.peekChar()
            if peek.isdigit() or peek in '.xeEb':
                accumulator.append(self.nextChar())
            else:
                if len(accumulator):
                    number = "".join(accumulator)
                    yield (NUMBER, number)
                    break
                else:
                    raise MedeaError("Invalid number")

    def skipSpace(self):  # TODO CH make consistent with skipLiteral - eliminate empty yield syntax
        while self.peekChar().isspace():
            self.nextChar()

    def skipLiteral(self, literal):
        for literalChar in literal:
            if self.nextChar() != literalChar:
                raise MedeaError("Expecting keyword {}" + literal)