import gc
import sys
from time import sleep
from examples.scripts.forecastExtractFields import run


def loop():
    """
    Attempts to connect to local wifi (if running on ESP8266/ESP32 Micropython platform)
    requests an OpenWeatherMap forecast API response every two minutes and 
    tokenizes object values named 'wind' within the forecast JSON 
    """
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
