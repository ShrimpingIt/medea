from medea.https import createContentByteGeneratorFactory, processHttpHeaders
from medea.twitter import twitterHeaders, createTwitterTimelineUrl
import sys

twitterUrl = createTwitterTimelineUrl('realDonaldTrump')
byteGeneratorFactory = createContentByteGeneratorFactory(twitterUrl, twitterHeaders)
byteGenerator = byteGeneratorFactory()

try:
    while True:
        sys.stdout.write(chr(next(byteGenerator)))
except StopIteration:
    pass