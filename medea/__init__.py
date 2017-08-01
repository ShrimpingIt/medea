from medea.agnostic import io

OPEN="open"
CLOSE="close"
KEY="key"
STRING="string"
NUMBER="number"
BOOLEAN="boolean"
NULL="null"

KEYCHARS = ('$','_')
QUOTECHARS = ("'", '"')

class MedeaError(AssertionError):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)

def dumpTokens(source):
    tokenizer = Tokenizer(source)
    tokenizer.dumpTokens()

def visit(source, callback):
    tokenizer = Tokenizer(source)
    for tokenPair in tokenizer.tokenize():
        callback(*tokenPair)

class Tokenizer():
    def __init__(self, source):
        self.source = source
        self.peeked = None
        self.read = -1
        sourceType = type(self.source)
        if type(self.source) is io.TextIOWrapper:
            def textFileGeneratorFactory(*a):
                while True:
                    yield self.source.read(1)
            self.generatorFactory = textFileGeneratorFactory
        else:
            raise MedeaError("No generatorFactory for {}".format(sourceType))

    def nextChar(self):
        self.read += 1
        if self.peeked is None:
            return next(self.generator)
        else:
            waspeeked = self.peeked
            self.peeked = None
            return waspeeked

    def peekChar(self):
        if self.peeked is None:
            self.peeked = self.nextChar()
            self.read -= 1
        return self.peeked

    def tokenize(self):
        self.generator = self.generatorFactory()
        yield from self.tokenizeValue()

    def dumpTokens(self):
        for token in self.tokenize():
            print(token)

    def tokenizeSpace(self):
        while self.peekChar().isspace():
            self.nextChar()
        yield from ()

    def tokenizeValue(self):
        yield from self.tokenizeSpace()
        char = self.peekChar()
        if char is not None:
            if char=="[":
                return (yield from self.tokenizeArray())
            elif char=="{":
                return (yield from self.tokenizeObject())
            elif char=='"' or char=="'":
                return (yield from self.tokenizeString())
            elif char.isdigit() or char=="-":
                return (yield from self.tokenizeNumber())
            elif char=="t":
                self.skipLiteral("true")
                return (yield (BOOLEAN, True))
            elif char=="f":
                self.skipLiteral("false")
                return (yield (BOOLEAN, False))
            elif char=="n":
                self.skipLiteral("null")
                return (yield (NULL, None))
            else:
                raise MedeaError("Unexpected character {}".format(char))

    def tokenizeArray(self):
        if self.nextChar() != "[":
            raise MedeaError("Array should begin with [")
        yield (OPEN,"[")
        while True:
            yield from self.tokenizeSpace()
            char = self.peekChar()
            if char == "]":
                self.nextChar()
                yield (CLOSE, "]")
                return
            else:
                yield from self.tokenizeValue()
                if self.peekChar() == ",":
                    self.nextChar()
                    continue

    def tokenizeObject(self):
        if self.nextChar() !="{":
            raise MedeaError("Objects begin {")
        else:
            yield (OPEN,"{")
        while True:
            yield from self.tokenizeSpace()
            peek = self.peekChar()
            if peek == "}":
                self.nextChar()
                yield (CLOSE,"}")
                return
            elif peek in QUOTECHARS:
                # BEGIN 'tokenizePair'
                yield from self.tokenizeKey()
                yield from self.tokenizeSpace()
                if self.nextChar() != ":":
                    raise MedeaError("Expecting : after key")
                yield from self.tokenizeSpace()
                yield from self.tokenizeValue()
                # END'tokenizePair'
            else:
                raise MedeaError("Keys begin \" or '")

            yield from self.tokenizeSpace()
            peek = self.peekChar()
            if peek == "}":
                pass
            elif peek == ",":
                self.nextChar()
            else:
                raise MedeaError("Pairs precede , or }")

    def tokenizeKey(self):
        return self.tokenizeString(KEY)

    def tokenizeString(self, token=STRING):
        delimiter = self.nextChar()
        if not delimiter in QUOTECHARS:
            raise MedeaError("{} starts with {}".format(token, QUOTECHARS))
        accumulator = []
        peek = self.peekChar()
        while peek != delimiter:
            if peek == "\\": # backslash escaping means consume two chars
                accumulator.append(self.nextChar())
            accumulator.append(self.nextChar())
            peek = self.peekChar()
        self.nextChar() # drop delimiter
        string = "".join(accumulator)
        yield (token, string)

    def tokenizeNumber(self):
        accumulator = []
        accumulator.append(self.nextChar())
        if accumulator[-1]=='-':
            accumulator.append(self.nextChar())
        if not(accumulator[-1].isdigit()):
            raise MedeaError("Numbers begin [0-9] after optional - sign")
        while True:
            peek = self.peekChar()
            if peek.isdigit() or peek in '.xeEb':
                accumulator.append(self.nextChar())
            else:
                if len(accumulator):
                    yield (NUMBER, "".join(accumulator))
                    break
                else:
                    raise MedeaError("Invalid number")

    def skipLiteral(self, literal):
        for literalChar in literal:
            if self.nextChar() != literalChar:
                raise MedeaError("Expecting keyword {}" + literal)