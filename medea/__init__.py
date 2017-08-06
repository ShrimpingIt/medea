from medea.agnostic import io,native,viper

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
    for tok, val in tokenizer.tokenize():
        callback(tok, val)

class Tokenizer():
    def __init__(self, source):
        self.source = source
        """
        self.bufSize = 512
        self.buf = None
        """
        self.peeked = None
        self.charCount = -1

    def nextChar(self):
        self.charCount += 1
        if self.peeked is None:
            return self.source.read(1)
        else:
            waspeeked = self.peeked
            self.peeked = None
            return waspeeked

    def peekChar(self):
        if self.peeked is None:
            self.peeked = self.nextChar()
            self.charCount -= 1
        return self.peeked

    def tokenize(self):
        yield from self.tokenizeValue()

    def tokenizeValuesNamed(self, key):
        """Searches for the first item named 'key', tokenizes the
        value, then repeats the search from that point"""
        while True:
            delimiter = self.nextChar()
            if delimiter in QUOTECHARS:
                for char in key:
                    if self.nextChar() != char:
                        break
                else:
                    if self.nextChar() != delimiter:
                        continue
                    self.skipSpace()
                    if self.nextChar() != ":":
                        continue
                    self.skipSpace()
                    yield from self.tokenizeValue()
            elif delimiter is None:
                break

    def dumpTokens(self):
        for token in self.tokenize():
            print(token)

    def tokenizeValue(self):
        self.skipSpace()
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
            self.skipSpace()
            char = self.peekChar()
            if char == "]":
                self.nextChar()
                return (yield (CLOSE, "]"))
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
            self.skipSpace()
            peek = self.peekChar()
            if peek == "}":
                self.nextChar()
                return (yield (CLOSE,"}"))
            elif peek in QUOTECHARS:
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
            if peek == "}":
                pass
            elif peek == ",":
                self.nextChar()
            else:
                raise MedeaError("Pairs precede , or }")

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

    def tokenizeKey(self):
        return self.tokenizeString(KEY)

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