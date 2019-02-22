from sys import platform
from medea.twitter import generateTweets, createTimelineTokenizer
from examples.scripts import timeit

def run():
    
    if platform == "esp8266" or platform == "esp32":
        from medea.auth import wifiName, wifiPass
        from medea.wifi import connect
        assert wifiName is not None and wifiPass is not None, "Provide wifi credentials"
        connect(wifiName.decode('utf8'), wifiPass.decode('utf8'))
    
    for tweetId, tweetText in generateTweets(createTimelineTokenizer("realDonaldTrump")):
        print("{} : '{}'".format(tweetId, tweetText))

if __name__ == "__main__":
    timeit(run)
