import gc
import sys
from time import sleep
from examples.scripts.twitterTimelineExtractFields import run

def loop():
    if sys.platform == "esp8266" or sys.platform == "esp32":
        from medea.auth import wifiName, wifiPass
        from medea.wifi import connect
        assert wifiName is not None and wifiPass is not None, "Provide wifi credentials"
        connect(wifiName.decode('utf8'), wifiPass.decode('utf8'))

    while True:
        run()
        gc.collect()
        sleep(120)

if __name__ == "__main__":
    loop()