from medea.util import visit
from medea.https import createContentByteGeneratorFactory
from medea.twitter import twitterHeaders, createTwitterTimelineUrl


def visitor(*a):
    print(a)


def run():
    twitterUrl = createTwitterTimelineUrl('realDonaldTrump', count=1)
    byteGeneratorFactory = createContentByteGeneratorFactory(twitterUrl, twitterHeaders)
    visit(byteGeneratorFactory, visitor)


run()