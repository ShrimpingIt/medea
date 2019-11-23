# Summary

Tokenizer is a class with multiple tokenizeX() generator methods which yield token,value pairs which correspond with events in a JSON tree traversal. 

No JSON document structure is stored. A Tokenizer yields only transient events indicating the boundaries of Array or Object containers, the Keys of named values and the type+value of individual primitives, with these events being issued as the JSON is read byte by byte.

Subclasses of Tokenizer can override its generator methods with application-specific logic. Intercepting the different tokenizeX phases allows very memory-efficient extraction of data from a JSON file or stream, by tracking the Tokenizer's entry and exit from different tokenising phases.

See http://xmlsoft.org/interface.html or http://www.jamesh.id.au/articles/libxml-sax/libxml-sax.html for an introduction to SAX which adopts a similar strategy for XML parsing.

There are tokenizeXxx() generator methods for each of the JSON types (boolean, number and string primitives, Arrays and Objects). Combining these is a type-agnostic tokenizeValue() generator method which detects the type from the byte stream then yields from the appropriate type-specific tokenizeXxx() generator.

# Tokenizer method signatures

Each tokenizeXXX() generator method accepts a byteGenerator and a boolean repeat flag, and returns a generator for token, value pairs.

## ByteGenerators

To tokenize a JSON stream, the bytes have to be retrieved from an in-memory array, from a file, over HTTP or some other mechanism. Tokenizers are designed to consume bytes from generators which fulfil this contract:

* Calling next(gen) or gen.step(None) yields the next byte. This will move the cursor position to the next unread byte then return its value.
* Calling gen.step(True) yields a repeat of the previous byte. This will read the current byte and leave the cursor position unchanged.
    - Note: Asking for a repeat byte before the first byte has been read will raise an error.
* When the stream is exhausted, a call to next() or gen.step() will raise StopIteration

In general, they can be treated as ordinary generators, except for the Tokenizer-specific handling of the repeat-byte signal.

## The 'repeat' flag

A tokenizer often has to read one-byte its own JSON value to detect the ending of the value. For this reason, tokenizeX() methods are provided with a flag to indicate that they should begin from the last read cursor position. 

In general if they are starting a new stream, tokenizerX() methods can rely on getting the next unread byte and should be invoked without repeat=True. However if the tokenizer is picking up from a previous tokenizer, it may need to explicitly request a repeat byte which has already been read.

## Future

In a future implementation the byteGenerator contract could be improved by using gen.send() for a previous requester to signal the need to push a byte back into the stream for the next requester. This signal from the previous requester (who knows the byte is unconsumed) would ensure the stream would repeat the byte next time, rather than requiring the next requester to have this information passed to them. This promises substantially simplified tokenizer implementations.

Additionally a switch should be made to use bytestrings for efficiency throughout, and not to ascii decode them to python's own unicode strings.

To improve test coverage, cases should be created which exercise all the Exception cases. Currently only 97% of code lines have coverage in the test suite. Notably, there are failure handling routines which have only been tested interactively during debugging and don't have tests.