from medea import Tokenizer, https, weather
from examples.scripts import timeit

def run():
    weatherUrl = weather.createCityUrl()

    tokenizer = Tokenizer()
    weatherBytes = https.generateContentBytes(weatherUrl)
    weatherBytes.send(None)

    for tok, val in tokenizer.tokenizeValuesNamed("rain", weatherBytes):
        print(tok, val)

if __name__ == "__main__":
    timeit(run)
