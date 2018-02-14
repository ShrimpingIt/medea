from medea import Tokenizer


def dumpTokens(byteGeneratorFactory):
    tokenizer = Tokenizer(byteGeneratorFactory)
    tokenizer.dumpTokens()


def visit(byteGeneratorFactory, callback):
    tokenizer = Tokenizer(byteGeneratorFactory)
    for tok, val in tokenizer.tokenize():
        callback(tok, val)