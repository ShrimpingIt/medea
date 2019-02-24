from medea import Tokenizer
from medea.file import generateFileBytes


def run():
    tokenizer = Tokenizer()
    byteGenerator = generateFileBytes('examples/data/weathermap.json')
    for tok, val in tokenizer.tokenizeValue(byteGenerator):
        print(tok, val)


if __name__ == "__main__":
    run()
