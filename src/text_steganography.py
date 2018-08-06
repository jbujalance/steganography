from PIL import Image
from conversion_utils import ConversionUtils as cu
from auto_increment_int import AutoIncrementInt


class TextSteganography:
    """
    A class to hide and retrieve text messages in an image.
    The texts are converted to ASCII binaries (each character takes 7 bits) for capacity purposes.
    """

    __LENGTH_TAG = cu.str2bin("SIZE")
    __START_TAG = cu.str2bin("START")
    __LENGTH_BITS = 32
    # TODO remove this buggy delimiter and use tags
    __DELIMITER = "1010101010101010"

    def __init__(self, input_filename):
        self.image = Image.open(input_filename).convert("RGB")
        self.pixels = self.image.load()

    def hide_message(self, message, output):
        """
        Hides a message in the class image.
        The message must contain only ASCII characters.
        :param message: the message to hide in the class image.
        :param output: the directory where the coded image is stored.
        """
        new_image = Image.new(self.image.mode, self.image.size)
        new_pixels = new_image.load()
        binary_message = cu.str2bin(message) + self.__DELIMITER
        msg_index = AutoIncrementInt(0)
        for x in range(self.image.size[0]):
            for y in range(self.image.size[1]):
                rgb_list = list(self.pixels[x, y])
                for i in range(len(rgb_list)):
                    if msg_index.get() < len(binary_message):
                        rgb_list[i] = cu.bin2int(cu.replace_lsb(cu.int2bin(rgb_list[i]), binary_message[msg_index.get_and_increment()]))
                new_pixels[x, y] = tuple(rgb_list)
        new_image.save(output)

    def retrieve_message(self):
        """
        Retrieves a hidden message from the class image if there is any
        :return: The hidden message or None if not messages found
        """
        binary_msg = ""
        for x in range(self.image.size[0]):
            for y in range(self.image.size[1]):
                rgb_tuple = self.pixels[x, y]
                for channel in rgb_tuple:
                    binary_msg += cu.get_lsb(cu.int2bin(channel))
                    if binary_msg[-len(self.__DELIMITER):] == self.__DELIMITER:
                        return cu.bin2str(binary_msg[:-len(self.__DELIMITER)])
        print("No message found !")
        return None

    def __ensure_capacity(self, message):
        """
        Makes sure that there is enough available bits in the image to store the given message.
        :param message: The message to store in the image.
        :return: True if there is enough capacity, False otherwise
        """
        height, width = self.image.size
        # TODO The last '1' should be later replaced by the number of LSB bits used per color chanel
        available_bits = height * width * 3 * 1
        # In ASCII, each character is encoded in 7 bits
        message_size = len(message) * 7
        boilerplate_size = len(self.__LENGTH_TAG) + self.__LENGTH_BITS + len(self.__START_TAG)
        return available_bits >= message_size + boilerplate_size
