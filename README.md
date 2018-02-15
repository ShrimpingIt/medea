# Medea - Low-memory-overhead JSON tokenizer

Medea is a Micropython and CPython-compatible library which can tokenize an arbitrary length of JSON with only a single byte of buffering, generating ([SAX-style](https://en.wikipedia.org/wiki/Simple_API_for_XML)) events to notify each structural element and its containing data. 

Medea can also negotiate HTTPS connections to some example JSON api providers, such as Twitter and OpenWeatherMap, in order to retrieve and process fields from live JSON data.

## Motivation

If JSON is parsed in the conventional Micropython way ( see [ujson.loads()](https://docs.micropython.org/en/latest/esp8266/library/ujson.html#ujson.loads) ) then an in-memory structure is created. A root ancestor dict or list is the parent of contained child elements. Those children can then be parents of further data structures. All these descendants accumulate in memory as the JSON is decoded.

On a limited-memory internet-of-things device like the ESP8266 this means complex online API structures such as the OpenWeatherMap API or Twitter are impossible to decode because the descendants cannot be stored in memory. For some verbose JSON services, even constructing a single string to pass into the ```json.loads()``` call would exceed the memory, before creating any children at all.

By contrast Medea processes the JSON source as a stream, throwing away all bytes and keeping just enough information to be able to detect and notify each complete 'token' found in the stream.  It can consume data from file, HTTPS, HTTP or socket streams using a buffer which can be as small as a single byte!

## Tokenizing

Bytes are traversed for JSON symbols, triggering \<JSON VALUE EVENTS>; pairs composed of (token, value) as follows.
  * (OPEN, OBJ)            : a new object, to be followed by a sequence of zero or more pairs like (KEY, keybytes) \<JSON VALUE EVENTS>
  * (CLOSE, OBJ)           : finishes the key/value pairs of the last-opened object
  * (OPEN, ARR)            : a new array, to be followed by a sequence of zero or more \<JSON VALUE EVENTS>
  * (CLOSE, ARR)           : finishes the last array which was opened
  * (KEY, keyBytes)        : the next value which follows is a value embedded in an object with the given KEY
  * (NUM, numberBytes)     : a whole or floating point number
  * (BOOL, booleanBytes)   : a `true` or `false` value
  * (STR, stringBytes)     : a text value
  * (NUL, nullBytes)       : corresponding with JSON `null` value

## Examples

Two sample JSON API results from Twitter and from OpenWeatherMap have been included in the repository and can be successfully processed into tokens by the library even on an ESP8266 as demonstrated by, for example...

```
import examples.scripts.twitterTimelineTokenizeCached
```

...or...

```
import examples.scripts.forecastTokenizeCached
```

The examples which process live Twitter or OpenWeatherMap JSON documents from their API servers over HTTPS need a Wifi connection. Getting a [Twitter developer account](https://apps.twitter.com/) allows you to apply for a [bearer token](https://www.npmjs.com/package/get-twitter-bearer-token) for your device to use. For forecasts you can apply for an [OpenWeatherMap app id](https://openweathermap.org/appid). 

Note: On ESP8266 a special build with Frozen Modules an increased size TLS buffer is needed (see pre-built image available below). 

Most example scripts assume you have configured an internet connection before running them. However, twitterTimelinePollFields.py and forecastPollFields.py show how to negotiate wifi before accessing an online JSON resource. 

## ESP32 Upload

See put.sh for a Linux (and probably Mac)-compatible console script which uploads all the scripts and data to an ESP32 using Adafruit's ampy tool.


## ESP8266 Pre-configured Image

A pre-configured image (based on version [5d0d12c9](https://github.com/ShrimpingIt/medea/tree/5d0d12c9e25965c26c06c7a3d223ab4aa80f05a0)) which works around the ESP8266 limitations noted below is available at http://shrimping.it/project/medea/ . It is based on the latest github at the time of writing with the `medea` library and examples onboard as frozen modules and a 8192byte TLS buffer to allow larger HTTPS payloads (e.g. at least 10 tweets from a Twitter timeline, at least a day's worth of 3-hourly OpenWeatherMap forecasts).

Use the standard `esptool` [instructions](https://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/intro.html) to upload the image.

Remember to add your own authentication values. After installing the special firmware, you can run test cases interactively as follows (note credentials are bytestrings, prefixed with b, and the values below will not work, they have to be YOUR credentials). 

```python
import medea.auth
medea.auth.wifiName=b"MyNetwork"
medea.auth.wifiPass=b"MyPassword"
medea.auth.twitterBearerId=b"abfed676767762762"
from examples.scripts.twitterTimelinePollFields import loop
loop()
```

...or for OpenWeatherMap...

```python
import medea.auth
medea.auth.wifiName=b"MyNetwork"
medea.auth.wifiPass=b"MyPassword"
medea.auth.weatherAppId=b"cebed89626876436487"
from examples.scripts.forecastPollFields import loop
loop()
```


## ESP8266 Limitations

Although Medea runs on CPython and ESP32 as regular python modules loaded from the filesystem, HTTPS JSON processing on ESP8266 requires that medea is installed as [frozen modules](http://docs.micropython.org/en/v1.9.3/unix/reference/constrained.html). Otherwise there is [not enough memory for the SSL socket handshake to complete](https://forum.micropython.org/viewtopic.php?f=2&t=4356#p25465). 

By default the standard ESP8266 TLS buffer is only large enough to handle a Twitter timeline API call requesting a single Tweet (count=1). However, the buffer can be increased [like this](https://github.com/micropython/micropython/commit/a47b8711316a4901bc81e1c46ce50de00207c47f) to build a special ESP8266 image that can handle larger payloads. Increasing the TLS record buffer to 8192 bytes enabled the handling of at least 10 tweets in testing.

See above for instructions to get hold of a pre-configured ESP8266 image which includes these fixes built-in to the firmware.

Note: The ESP8266 interpreter cannot handle recursion beyond 19 stack levels, so very deeply nested JSON data still cannot be handled without further optimising this library.


## Why the name?

[Medea](https://en.wikipedia.org/wiki/Medea) was the sorcerer wife of [Jason](https://en.wikipedia.org/wiki/Jason) who was famed for killing off her own children. It is a fitting name for a low-overhead JSON tokenizer for Micropython. In this implementation, no children survive at all. Only a series of SAX-style notifications are made as the JSON family 'tree' is traversed.
