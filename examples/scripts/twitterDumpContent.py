from medea.https import createHttpsByteGeneratorFactory, processHttpHeaders
from medea.twitter import twitterHeaders, createTwitterTimelineUrl
import sys

twitterUrl = createTwitterTimelineUrl('realDonaldTrump')
byteGeneratorFactory = createHttpsByteGeneratorFactory(twitterUrl, twitterHeaders)
byteGenerator = byteGeneratorFactory()

# process header bytes
contentLength = processHttpHeaders(byteGenerator)

# process content bytes
for contentPos in range(contentLength):
    sys.stdout.write(chr(next(byteGenerator)))

# reached end of known bytes, force stream to end, triggering socket close
byteGenerator.throw(StopIteration)