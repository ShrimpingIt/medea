from medea import visit
from medea.https import createHttpsContentByteGeneratorFactory
from medea.twitter import twitterHeaders, createTwitterTimelineUrl


def visitor(tok, val):
    print(tok, val)


def run():
    twitterUrl = createTwitterTimelineUrl('realDonaldTrump', count=1)
    byteGeneratorFactory = createHttpsContentByteGeneratorFactory(twitterUrl, twitterHeaders)
    visit(byteGeneratorFactory, visitor)


run()