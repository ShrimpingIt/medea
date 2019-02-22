from sys import platform
from medea import Tokenizer, defaultBufferSize
from medea.twitter import generateTweets, generateTimelineBytes
from examples.scripts import timeit

def run():
    
    if platform == "esp8266" or platform == "esp32":
        from medea.auth import wifiName, wifiPass
        from medea.wifi import connect
        assert wifiName is not None and wifiPass is not None, "Provide wifi credentials"
        connect(wifiName.decode('utf8'), wifiPass.decode('utf8'))

    buf = bytearray(defaultBufferSize)
    tokenizer = Tokenizer()
    timelineBytes = generateTimelineBytes("realDonaldTrump", buf=buf)
    
    try:
        for tweetId, tweetText in generateTweets(tokenizer, timelineBytes):
            print("{} : '{}'".format(tweetId, tweetText))
    finally:
        timelineBytes.close()

if __name__ == "__main__":
    timeit(run)
