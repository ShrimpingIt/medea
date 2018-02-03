from medea.https import createHttpsByteGeneratorFactory, processHttpHeaders
from medea.twitter import twitterHeaders, createTwitterTimelineUrl
import sys

twitterUrl = createTwitterTimelineUrl('realDonaldTrump')
streamGenerator = createHttpsByteGeneratorFactory(twitterUrl, twitterHeaders)
stream = streamGenerator()

# process header bytes
contentLength = processHttpHeaders(stream)

# process content bytes
content = bytearray()
for contentPos in range(contentLength):
    sys.stdout.write(chr(next(stream)))

# reached end of known bytes, force stream to end, triggering socket close
stream.throw(StopIteration)