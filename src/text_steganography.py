from PIL import Image
from conversion_utils import ConversionUtils as cu
from auto_increment_int import AutoIncrementInt


class TextSteganography:

    def __init__(self, input_filename):
        self.image = Image.open(input_filename).convert("RGB")
        self.pixels = self.image.load()
        self.__delimiter = "1010101010101010"

    def hide_message(self, message, output):
        new_image = Image.new(self.image.mode, self.image.size)
        new_pixels = new_image.load()
        binary_message = cu.str2bin(message) + self.__delimiter

        msg_index = AutoIncrementInt(0)
        for x in range(self.image.size[0]):
            for y in range(self.image.size[1]):
                red, green, blue = self.pixels[x, y]
                if msg_index.get() < len(binary_message):
                    red = cu.bin2int(cu.replace_lsb(cu.int2bin(red), binary_message[msg_index.get_and_increment()]))
                if msg_index.get() < len(binary_message):
                    green = cu.bin2int(cu.replace_lsb(cu.int2bin(green), binary_message[msg_index.get_and_increment()]))
                if msg_index.get() < len(binary_message):
                    blue = cu.bin2int(cu.replace_lsb(cu.int2bin(blue), binary_message[msg_index.get_and_increment()]))
                new_pixels[x, y] = (red, green, blue)

        new_image.save(output)

    def retrieve_message(self):
        binary_msg = ""
        for x in range(self.image.size[0]):
            for y in range(self.image.size[1]):
                rgb_tuple = self.pixels[x, y]
                for channel in rgb_tuple:
                    bit = cu.get_lsb(cu.int2bin(channel))
                    binary_msg += bit
                    if binary_msg[-16:] == self.__delimiter:
                        return cu.bin2str(binary_msg[:-16])

        print("No message found !")
        return None
