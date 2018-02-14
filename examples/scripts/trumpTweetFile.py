from medea import visit
from medea.https import createHttpsContentByteGeneratorFactory
from medea.file import createFileByteGeneratorFactory
from medea.twitter import twitterHeaders, createTwitterTimelineUrl

filename = "trump.content"

def visitor(tok, val):
    print(tok, val)

def writefile():
    twitterUrl = createTwitterTimelineUrl('realDonaldTrump', count=1)
    streamGenerator = createHttpsContentByteGeneratorFactory(twitterUrl, twitterHeaders)
    stream = streamGenerator()
    with open(filename, "wb") as f:
        try:
            while True:
                f.write(chr(next(stream)).encode('ascii'))
        except StopIteration:
            pass

def readfile():
    streamGenerator = createFileByteGeneratorFactory(filename)
    visit(streamGenerator, visitor)

if __name__ == "__main__":
    writefile()
    readfile()