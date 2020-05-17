from machine import freq
freq(160000000)
from utime import ticks_ms

def measure(size):
    numChars = 0
    numPairs = 0
    startMs = ticks_ms()
    with open("examples/data/weatherMap.json") as f:
        while True:
            result = f.read(size)
            if result:
                for char in result:
                    numChars += 1
                    if numChars % 100 == 0:
                        print("Chars", numChars)
                    if char == ":":
                        numPairs += 1
                        if numPairs % 100 == 0:
                            print("Pairs", numPairs)
            else:
                break
    stopMs = ticks_ms()
    return stopMs - startMs

blockSize = 1
for index in range(12):
    duration = measure(blockSize)
    print("{} bytes : {} ms".format(blockSize, duration))
    blockSize *= 2