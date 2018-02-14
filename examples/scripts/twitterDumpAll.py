from medea.https import createHttpsByteGeneratorFactory
from medea.twitter import twitterHeaders, createTwitterTimelineUrl
import sys

twitterUrl = createTwitterTimelineUrl('realDonaldTrump', tweet_mode="extended")
byteGeneratorFactory = createHttpsByteGeneratorFactory(twitterUrl, twitterHeaders)
byteGenerator = byteGeneratorFactory()
contentPos = 0
while True:
    sys.stdout.write(chr(next(byteGenerator)))
    contentPos += 1
