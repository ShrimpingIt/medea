from medea import Tokenizer
from medea.file import createFileByteGeneratorFactory
from medea.https import createHttpsContentByteGeneratorFactory
from medea.twitter import twitterHeaders, createTwitterTimelineUrl
from examples.scripts import timeit

def generateTweets():
    """ 
    testGenerator = createFileStreamGenerator('examples/data/trumpTweet.json')
    """

    twitterUrl = createTwitterTimelineUrl('realDonaldTrump', count=1)
    byteGeneratorFactory = createHttpsContentByteGeneratorFactory(twitterUrl, twitterHeaders)

    tokenizer = Tokenizer(byteGeneratorFactory)

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

    # yield forces the generator factories to be invoked, populating ids and texts
    # until stream empty, but actually generates ()
    yield from tokenizer.generateFromNamed(["id","text","user"], generatorFactory)

    # this is doing the real yielding of value pairs
    yield from zip(ids, texts)

def run():
    for id, text in generateTweets():
        print("{} : '{}'".format(id, text))

timeit(run)
