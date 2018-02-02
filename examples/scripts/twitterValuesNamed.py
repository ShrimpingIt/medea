from medea import Tokenizer,createFileStreamGenerator
from medea import createHttpsContentStreamGenerator, createTwitterTimelineUrl, processHttpHeaders
from medea.auth import bearerHeader
from examples.scripts import timeit

def generateTweets():
    streamGenerator = createFileStreamGenerator('examples/data/trumpTweet.json')

    """ # to use live twitter instead of cached file
    twitterUrl = createTwitterTimelineUrl('realDonaldTrump')
    streamGenerator = createHttpsContentStreamGenerator(twitterUrl, bearerHeader)
    """

    tokenizer = Tokenizer(streamGenerator)

    ids = []
    texts = []

    def generatorFactory(name):
        if name == "id":
            for tok, val in tokenizer.tokenizeValue():
                print("Found id {}".format(val))
                ids.append(val)
        elif name == "text":
            for tok, val in tokenizer.tokenizeValue():
                print("Found text {}".format(val))
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