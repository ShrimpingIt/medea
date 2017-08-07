from medea import Tokenizer
from examples.scripts import timeit

def run():
    source = open('examples/data/weathermap.json')
    tokenizer = Tokenizer(source)

    for tok, val in tokenizer.tokenizeValuesNamed("rain"):
        print(tok, val)

timeit(run)