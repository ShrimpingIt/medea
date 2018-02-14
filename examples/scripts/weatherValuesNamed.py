from medea import Tokenizer
from medea.file import createFileByteGeneratorFactory
from examples.scripts import timeit

def run():
    tokenizer = Tokenizer(createFileByteGeneratorFactory('examples/data/weathermap.json'))

    for tok, val in tokenizer.tokenizeValuesNamed("rain"):
        print(tok, val)

timeit(run)