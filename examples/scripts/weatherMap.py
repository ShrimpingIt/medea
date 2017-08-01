from medea import visit

def visitor(tok, val):
    print(tok, val)

def run():
    visit(open('examples/data/weathermap.json'), visitor)

run()