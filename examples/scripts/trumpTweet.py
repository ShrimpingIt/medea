from medea import visit

def visitor(tok, val):
    print(tok, val)

def run():
    visit(open('examples/data/trumpTweet.json'), visitor)

run()