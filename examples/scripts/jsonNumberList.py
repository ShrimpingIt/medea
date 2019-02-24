from medea.file import tokenizeFile

for tok, val in tokenizeFile('examples/data/numberList.json'):
    print(tok, val)
