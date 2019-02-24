from medea.file import tokenizeFile

for tok, val in tokenizeFile('examples/data/emptyObject.json'):
    print(tok, val)
