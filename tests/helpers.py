from medea.bytestring import generateStringBytes

def verifyGeneratedTokens(tokenizeMethod, byteString, expectedSequence):
    byteGenerator = generateStringBytes(byteString)
    generatedSequence = list(tokenizeMethod(byteGenerator))
    expectedSequence = list(expectedSequence)
    for generated, expected in zip(generatedSequence, expectedSequence):
        assert generated == expected
    assert len(generatedSequence) == len(expectedSequence)
