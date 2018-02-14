# The code below runs successfully on ESP32, but causes ESP8266 
# to reset. I am using the same machine and (historically reliable) USB cable 
# in a USB3.0 slot in both cases. The put.sh shell script can upload the
# correct sources for testing

import sys
import gc
from medea.https import createHttpsByteGeneratorFactory
gc.collect()
if sys.implementation.name=="micropython":
    from medea.wifi import connect
    connect('SkyHome', 'c3fnh0ile')

#factory = createHttpsByteGeneratorFactory('https://www.google.com')
#factory = createHttpsByteGeneratorFactory('https://https://httpbin.org/ip')
factory = createHttpsByteGeneratorFactory('https://api.twitter.com/1.1/')
generator=factory()
byte = next(generator)
