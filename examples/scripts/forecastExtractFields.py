from medea import Tokenizer, https, weather
from examples.scripts import timeit

def run():
    weatherUrl = weather.createCityUrl()

    tokenizer = Tokenizer(https.createContentByteGeneratorFactory(weatherUrl))

    for tok, val in tokenizer.tokenizeValuesNamed("rain"):
        print(tok, val)

if __name__ == "__main__":
    timeit(run)