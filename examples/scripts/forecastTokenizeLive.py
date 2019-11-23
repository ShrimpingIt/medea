from medea import Tokenizer
from medea.https import generateContentBytes
from medea.weather import createCityUrl


def run():
    tokenizer = Tokenizer()
    weatherUrl = createCityUrl()
    byteGenerator = generateContentBytes(weatherUrl)
    for tok, val in tokenizer.tokenizeValue(byteGenerator):
        print(tok, val)


if __name__ == "__main__":
    run()
