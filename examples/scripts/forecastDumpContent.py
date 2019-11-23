import sys
import medea.https as https
import medea.weather as weather

def run():
    """Dump only the Content bytes from an OpenWeatherMap forecast HTTP Response"""
    weatherUrl = weather.createCityUrl()
    weatherBytes = https.generateContentBytes(weatherUrl)

    try:
        while True:
            sys.stdout.write(chr(next(weatherBytes)))
    except StopIteration:
        pass

if __name__ == "__main__":
    run()
