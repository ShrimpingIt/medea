from medea import dumpTokens
from medea.file import createFileByteGeneratorFactory

dumpTokens(createFileByteGeneratorFactory('examples/data/numberList.json'))