from machine import freq
freq(160000000)
from medea import Tokenizer

source = open('examples/data/weathermap.json')
tokenizer = Tokenizer(source)

for tok, val in tokenizer.tokenizeValuesNamed("rain"):
    print(tok, val)