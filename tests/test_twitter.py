from medea import Tokenizer
from medea.file import generateFileBytes
from medea.twitter import generateTweets

timelinePath = './examples/data/trumpTweet.json'

def test_cached_twitter():
    tokenizer = Tokenizer()
    timelineBytes = generateFileBytes(timelinePath)

    try:
        for tweetId, tweetText in generateTweets(tokenizer, timelineBytes):
            assert (tweetId, tweetText) == (1099803719435239426, "....productive talks, I will be delaying the U.S. increase in tariffs now scheduled for March 1. Assuming both sides make additional progress, we will be planning a Summit for President Xi and myself, at Mar-a-Lago, to conclude an agreement. A very good weekend for U.S. &amp; China!")
    finally:
        timelineBytes.close()
