from medea import Tokenizer,createFileStreamGenerator
from examples.scripts import timeit

def run():
    tokenizer = Tokenizer(createFileStreamGenerator('examples/data/weathermap.json'))

    for tok, val in tokenizer.tokenizeValuesNamed("rain"):
        print(tok, val)

timeit(run)