from medea.util import visit
from medea.https import createContentByteGeneratorFactory
from medea.twitter import twitterHeaders, createTwitterTimelineUrl


def visitor(tok, val):
    print(tok, val)


def run():
    twitterUrl = createTwitterTimelineUrl('realDonaldTrump', count=1)
    byteGeneratorFactory = createContentByteGeneratorFactory(twitterUrl, twitterHeaders)
    visit(byteGeneratorFactory, visitor)


run()