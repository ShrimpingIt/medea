from medea import Tokenizer,createFileFactory
from examples.scripts import timeit

def generateTweets():
    sourceFactory = createFileFactory('examples/data/trumpTweet.json')
    tokenizer = Tokenizer(sourceFactory)

    ids = []
    texts = []

    def generatorFactory(name):
        if name == "id":
            for tok, val in tokenizer.tokenizeValue():
                ids.append(val)
        elif name == "text":
            for tok, val in tokenizer.tokenizeValue():
                texts.append(val)
        elif name == "user":
            pass
        yield from ()

    # yield forces the generator factories to be invoked until stream empty, but actually generates ()
    yield from tokenizer.generateFromNamed(["id","text","user"], generatorFactory)

    # this is doing the real yielding
    yield from zip(ids, texts)

def run():
    for id, text in generateTweets():
        print("{} : '{}'".format(id, text))

timeit(run)