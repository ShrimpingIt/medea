import sys
from medea.util import visit
from medea.https import createContentByteGeneratorFactory
from medea.file import createFileByteGeneratorFactory
from medea.twitter import twitterHeaders, createTwitterTimelineUrl

filename = 'examples/data/trumpTweet.json'

def visitor(tok, val):
    print(tok, val)

def writefile(): # reference implementation to populate the sample file
    twitterUrl = createTwitterTimelineUrl('realDonaldTrump', count=1)
    generatorFactory = createContentByteGeneratorFactory(twitterUrl, twitterHeaders)
    generator = generatorFactory()
    with open(filename, "wb") as f:
        while True:
            f.write(bytearray([next(generator)]))

def readfile():
    generatorFactory = createFileByteGeneratorFactory(filename)
    visit(generatorFactory, visitor)


if __name__ == "__main__":
    readfile()