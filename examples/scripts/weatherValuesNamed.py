from medea import Tokenizer,createFileFactory
from examples.scripts import timeit

def run():
    sourceFactory = createFileFactory('examples/data/weathermap.json')
    tokenizer = Tokenizer(sourceFactory)

    for tok, val in tokenizer.tokenizeValuesNamed("rain"):
        print(tok, val)

timeit(run)