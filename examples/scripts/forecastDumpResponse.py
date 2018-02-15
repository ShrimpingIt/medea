import sys
from medea.util import visit
import medea.https as https
import medea.weather as weather

def visitor(tok, val):
    print(tok, val)

def run():
    weatherUrl = weather.createCityUrl()
    byteGeneratorFactory = https.createByteGeneratorFactory(weatherUrl)
    byteGenerator = byteGeneratorFactory()

    try:
        while True:
            sys.stdout.write(chr(next(byteGenerator)))
    except StopIteration:
        pass

if __name__ == "__main__":
    run()