from medea import visit, createTwitterTimelineUrl, createHttpsContentStreamGenerator
from medea.auth import bearerHeader


def visitor(tok, val):
    print(tok, val)


def run():
    twitterUrl = createTwitterTimelineUrl('realDonaldTrump', count=1)
    streamGenerator = createHttpsContentStreamGenerator(twitterUrl, bearerHeader)

    visit(streamGenerator, visitor)


run()