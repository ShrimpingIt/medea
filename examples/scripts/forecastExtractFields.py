from medea import Tokenizer, https, weather
from examples.scripts import timeit

def run():
    """Tokenizes object values named 'wind' from an OpenWeatherMap forecast API response"""
    weatherUrl = weather.createCityUrl()

    tokenizer = Tokenizer()
    weatherBytes = https.generateContentBytes(weatherUrl)

    def tokenizeDescendants(name, gen):
        yield from tokenizer.tokenizeValue(gen, True)

    for tok, val in tokenizer.tokenizeValuesNamed("wind", tokenizeDescendants, weatherBytes):
        print(tok, val)

if __name__ == "__main__":
    timeit(run)
