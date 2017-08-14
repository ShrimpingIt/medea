# Medea - Low-memory-overhead JSON tokenizer

[Medea](https://en.wikipedia.org/wiki/Medea) was the sorcerer wife of [Jason](https://en.wikipedia.org/wiki/Jason) who was famed for killing off her own children. It is a fitting name for a low-overhead JSON tokenizer for Micropython. In this implementation, no children survive at all. Only a series of [SAX-style](https://en.wikipedia.org/wiki/Simple_API_for_XML) notifications are made as the JSON family 'tree' is traversed.

## Purpose

If JSON is parsed in the conventional Micropython way ( see https://docs.micropython.org/en/latest/esp8266/library/ujson.html#ujson.loads ) then an in-memory structure is created in which an ancestor dict or list is the parent of contained child elements. In turn those children may be parents to further data structures. All these children accumulate in memory as the JSON is decoded. On an internet-of-things device like the ESP8266 (Cockle) this means complex online API structures such as the OpenWeatherMap API or Twitter are impossible to decode because the memory overhead is too high. For some services, even constructing a single string to pass into the ```json.loads()``` call would exceed the memory, before creating any children at all.

Medea was implemented for specifically this purpose. It can tokenize an arbitrary length of JSON with only a single byte of buffering. The biggest limitation Medea faces is recursion depth from nested items inside items. The ESP8266 cannot handle recursion beyond 19 stack levels, so very deep JSON data still cannot be handled without further optimising this library.

# Proof

Two sample JSON API results from Twitter and from OpenWeatherMap have been included in the repository and can be successfully processed into tokens by the library as demonstrated by, for example...

```
import examples.scripts.trumpTweet
```

...or...

```
import examples.scripts.weatherMap
```
