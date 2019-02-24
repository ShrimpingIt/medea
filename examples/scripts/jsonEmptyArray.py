from medea.file import tokenizeFile

for tok, val in tokenizeFile('examples/data/emptyArray.json'):
    print(tok, val)
