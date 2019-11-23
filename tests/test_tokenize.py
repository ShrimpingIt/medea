import pytest
from medea import Tokenizer
from medea import OPEN, CLOSE, ARR, OBJ, KEY, STR, NUM, NUL, BOOL
from tests.helpers import verifyGeneratedTokens
from itertools import chain

# TODO CH refactor tests and code for bytestrings being extracted as keys and strings

tokenizer = Tokenizer()

literalSequences = {
    "true": ((BOOL, True), ),
    "false":((BOOL, False), ),
    "null": ((NUL, None), ),
}

numberSequences = {
    "0":    ((NUM, 0), ),
    "1":    ((NUM, 1), ),
    "-1":   ((NUM, -1), ),
    "10":   ((NUM, 10), ),
    "10e1": ((NUM, 100.0), ),
}

stringSequences = {
    "'hello'":    ((STR, "hello"), ),
    "'world'":    ((STR, "world"), ),
}

arraySequences = {
    "[]": (
        (OPEN, ARR),
        (CLOSE, ARR)
    ),
    "[3,4,5]": (
        (OPEN, ARR),
        (NUM, 3),
        (NUM, 4),
        (NUM, 5),
        (CLOSE, ARR)
    ),
    "[3 ,4 ,5 ]": (
        (OPEN, ARR),
        (NUM, 3),
        (NUM, 4),
        (NUM, 5),
        (CLOSE, ARR)
    ),
    "[ 3 , 4 , 5 ]": (
        (OPEN, ARR),
        (NUM, 3),
        (NUM, 4),
        (NUM, 5),
        (CLOSE, ARR)
    ),
    "[null,true,false]": (
        (OPEN, ARR),
        (NUL, None),
        (BOOL, True),
        (BOOL, False),
        (CLOSE, ARR)
    ),
}

objectSequences = {
    "{}": (
        (OPEN, OBJ),
        (CLOSE, OBJ)
    ),
    "{'roses':'red','violets':'blue'}": (
        (OPEN, OBJ),
        (KEY, 'roses'),
        (STR, 'red'),
        (KEY, 'violets'),
        (STR, 'blue'),
        (CLOSE, OBJ)
    ),
    '{"entities":{"hashtags":[],"symbols":[]}}': (
        (OPEN, OBJ),
        (KEY, 'entities'),
        (OPEN, OBJ),
        (KEY, 'hashtags'),
        (OPEN, ARR),
        (CLOSE, ARR),
        (KEY, 'symbols'),
        (OPEN, ARR),
        (CLOSE, ARR),
        (CLOSE, OBJ),
        (CLOSE, OBJ)
    ),
    '{"indices":[0,23]}': (
        (OPEN, OBJ),
        (KEY, 'indices'),
        (OPEN, ARR),
        (NUM, 0),
        (NUM, 23),
        (CLOSE, ARR),
        (CLOSE, OBJ)
    )
}

@pytest.mark.parametrize("byteString, expectedSequence", numberSequences.items())
def testTokenizeNumber(byteString, expectedSequence):
    return verifyGeneratedTokens(tokenizer.tokenizeNumber, byteString, expectedSequence)


@pytest.mark.parametrize("byteString, expectedSequence", stringSequences.items())
def testTokenizeString(byteString, expectedSequence):
    return verifyGeneratedTokens(tokenizer.tokenizeString, byteString, expectedSequence)


@pytest.mark.parametrize("byteString, expectedSequence", arraySequences.items())
def testTokenizeArray(byteString, expectedSequence):
    return verifyGeneratedTokens(tokenizer.tokenizeArray, byteString, expectedSequence)


@pytest.mark.parametrize("byteString, expectedSequence", objectSequences.items())
def testTokenizeObject(byteString, expectedSequence):
    return verifyGeneratedTokens(tokenizer.tokenizeObject, byteString, expectedSequence)


@pytest.mark.parametrize("byteString, expectedSequence", chain(
        literalSequences.items(),
        numberSequences.items(),
        stringSequences.items(),
        objectSequences.items(),
        arraySequences.items(),
))
def testTokenizeValue(byteString, expectedSequence):
    return verifyGeneratedTokens(tokenizer.tokenizeValue, byteString, expectedSequence)
