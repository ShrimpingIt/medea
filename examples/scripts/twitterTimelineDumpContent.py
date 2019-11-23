import sys
from medea.twitter import generateTimelineBytes

byteGenerator = generateTimelineBytes('realDonaldTrump')

try:
    while True:
        sys.stdout.write(chr(next(byteGenerator)))
except StopIteration:
    pass

