from medea.file import tokenizeFile

for tok, val in tokenizeFile('examples/data/objectMap.json'):
    print(tok, val)
