import gc
import sys
from time import sleep
from examples.scripts.twitterTimelineExtractFields import run
from medea.auth import wifiName, wifiPass

if sys.platform == "esp8266" or sys.platform == "esp32":
    from medea.wifi import connect
    assert wifiName is not None and wifiPass is not None, "Provide wifi credentials"
    connect(wifiName,wifiPass)

while True:
    run()
    gc.collect()
    sleep(120)
