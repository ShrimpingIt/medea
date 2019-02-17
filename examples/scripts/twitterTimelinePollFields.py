import gc
import sys
from time import sleep
from examples.scripts.twitterTimelineExtractFields import generateTweets

def loop(account=None):
    if sys.platform == "esp8266" or sys.platform == "esp32":
        from medea.auth import wifiName, wifiPass
        from medea.wifi import connect
        assert wifiName is not None and wifiPass is not None, "Provide wifi credentials"
        connect(wifiName.decode('utf8'), wifiPass.decode('utf8'))

    currentTweetId = None
    while True:
        gc.collect()
        try:
            for tweetId, tweetText in generateTweets(account):
                if tweetId != currentTweetId:
                    currentTweetId = tweetId
                    print("{} : '{}'".format(tweetId, tweetText))
        except OSError: # typically a network disconnection
            pass
        sleep(120)

if __name__ == "__main__":
    loop()
