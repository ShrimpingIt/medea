from medea import Tokenizer
from medea.file import generateFileBytes
from medea.twitter import generateTweets
from examples.scripts import timeit


filename = 'examples/data/trumpTweet.json'

def run():
    
    tokenizer = Tokenizer()
    timelineBytes = generateFileBytes(filename)
    
    try:
        for tweetId, tweetText in generateTweets(tokenizer, timelineBytes):
            print("{} : '{}'".format(tweetId, tweetText))
    finally:
        timelineBytes.close()

if __name__ == "__main__":
    timeit(run)
