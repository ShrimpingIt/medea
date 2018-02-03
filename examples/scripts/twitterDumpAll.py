from medea.https import createHttpsByteGeneratorFactory, processHttpHeaders
from medea.twitter import twitterHeaders, createTwitterTimelineUrl
import sys

twitterUrl = createTwitterTimelineUrl('realDonaldTrump')
byteGeneratorFactory = createHttpsByteGeneratorFactory(twitterUrl, twitterHeaders)
byteGenerator = byteGeneratorFactory()
contentPos = 0
while True:
    sys.stdout.write(chr(next(byteGenerator)))
    print(contentPos)
    contentPos += 1
