from medea.util import visit
import medea.https as https
import medea.weather as weather

# TODO handle the way that nested httpByteGenerator within httpContentByteGenerator causes
# loss of a single byte, preventing Object from being parsed correctly. Where is the byte mismatch?
# How come it doesn't affect the Twitter implementation

def visitor(tok, val):
    print(tok, val)

def run():
    weatherUrl = weather.createCityUrl()
    visit(https.createContentByteGeneratorFactory(weatherUrl), visitor)

if __name__ == "__main__":
    run()