from medea import Tokenizer
from medea.twitter import generateTimelineBytes

def run():
    tokenizer = Tokenizer()
    byteGenerator = generateTimelineBytes('realDonaldTrump')
    tokenGenerator = tokenizer.tokenizeValue(byteGenerator)
    for tok, val in tokenGenerator:
        print(tok, val)

run()
