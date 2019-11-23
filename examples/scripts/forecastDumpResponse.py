import sys
import medea.https as https
import medea.weather as weather

def run():
    """Dump all the bytes from an OpenWeatherMap forecast HTTP Response"""
    weatherUrl = weather.createCityUrl()
    byteGenerator = https.generateResponseBytes(weatherUrl)

    try:
        while True:
            sys.stdout.write(chr(next(byteGenerator)))
    except StopIteration:
        pass

if __name__ == "__main__":
    run()
