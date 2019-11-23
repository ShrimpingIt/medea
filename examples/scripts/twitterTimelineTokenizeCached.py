from medea import Tokenizer
from medea.https import generateContentBytes
from medea.file import generateFileBytes
from medea.twitter import twitterHeaders, createTwitterTimelineUrl

filename = 'examples/data/trumpTweet.json'


def visitor(tok, val):
    print(tok, val)


def writefile(): # reference implementation to populate the sample file
    twitterUrl = createTwitterTimelineUrl('realDonaldTrump', count=1)
    generator = generateContentBytes(twitterUrl, twitterHeaders)
    with open(filename, "wb") as f:
        while True:
            f.write(bytearray([next(generator)]))


def readfile():
    tokenizer = Tokenizer()
    generator = generateFileBytes(filename)
    for tok, val in tokenizer.tokenizeValue(generator):
        print(tok, val)


if __name__ == "__main__":
    readfile()
