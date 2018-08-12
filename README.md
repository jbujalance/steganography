# Python Steganography
A simple library that performs text steganography over images.
The algorithm uses the LSB (Least Significant Bit) of every color channel (RGB)
of each pixel of the image to encode the message.

## Encoding
In order to hide a message in an image, follow the following snippet:
```python
from src.text_steganography import TextSteganography

encoder = TextSteganography("../res/original.png")
encoder.hide_message("Hello World !", "../res/output.png")
```
This will use the `original.png` image file to hide the message `Hello World!` in it
and output the result to the file `output.png`.

In case that the image is too small for the given message, a `CapacityException`
will be thrown by the `hide_mesage` method.

## Decoding
In order to retrieve an encoded message from an image, use the following snippet:ç
```python
from src.text_steganography import TextSteganography

decoder = TextSteganography("../res/image_with_message.png")
decoded_message = decoder.retrieve_message()
```
This will retrieve the hidden message from the file `image_with_message.png`.
In case there are not any encoded messages in the given image, a `NoMessageFoundException`
will be thrown by the method `retrieve_message`.
