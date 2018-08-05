from text_steganography import TextSteganography

encoder = TextSteganography("../res/original.png")
encoder.hide_message("Hello world !", "../res/output.png")

decoder = TextSteganography("../res/output.png")
print(decoder.retrieve_message())
