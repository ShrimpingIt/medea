from medea import dumpTokens, visit

def visitor(tok, val):
    print(tok, val)

def run():
    visit(open('examples/data/trumpTweet.json', 'rb'), visitor)

run()