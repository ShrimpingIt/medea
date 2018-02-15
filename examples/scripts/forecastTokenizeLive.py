from medea.util import visit
import medea.https as https
import medea.weather as weather

def visitor(tok, val):
    print(tok, val)

def run():
    weatherUrl = weather.createCityUrl()
    visit(https.createContentByteGeneratorFactory(weatherUrl), visitor)

if __name__ == "__main__":
    run()