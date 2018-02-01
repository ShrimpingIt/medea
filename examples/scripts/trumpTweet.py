from medea import visit, createFileStreamGenerator

def visitor(tok, val):
    print(tok, val)

def run():
    visit(createFileStreamGenerator('examples/data/trumpTweet.json'), visitor)

run()