from medea import visit
from medea.file import createFileByteGeneratorFactory


def visitor(tok, val):
    print(tok, val)

def run():
    visit(createFileByteGeneratorFactory('examples/data/weathermap.json'), visitor)

run()