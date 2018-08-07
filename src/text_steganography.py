from PIL import Image
from src.conversion_utils import ConversionUtils as cu
from src.auto_increment_int import AutoIncrementInt
from src.exceptions import CapacityException, NoMessageFoundException


class TextSteganography:
    """
    A class to hide and retrieve text messages in an image.
    The texts are converted to ASCII binaries (each character takes 7 bits) for capacity purposes.
    """

    _LENGTH_TAG = cu.str2bin("SIZE")
    _START_TAG = cu.str2bin("START")
    _LENGTH_BITS = 32
    # TODO remove this buggy delimiter and use tags
    _DELIMITER = "1010101010101010"

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
        self._check_capacity(message)
        new_image = Image.new(self.image.mode, self.image.size)
        new_pixels = new_image.load()
        binary_message = self._get_header_and_message_bin(message)
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
                    if binary_msg[-len(self._DELIMITER):] == self._DELIMITER:
                        return cu.bin2str(binary_msg[:-len(self._DELIMITER)])
        print("No message found !")
        return None

    def _check_capacity(self, message):
        """
        Makes sure that there is enough available bits in the image to store the given message.
        :param message: The message to store in the image.
        :exception CapacityException: if there is not enough capacity in the image to store the given message
        """
        height, width = self.image.size
        # TODO The last '1' should be later replaced by the number of LSB bits used per color chanel
        available_bits = height * width * 3 * 1
        # In ASCII, each character is encoded in 7 bits
        message_size = len(message) * 7
        headers_size = len(self._LENGTH_TAG) + self._LENGTH_BITS + len(self._START_TAG)
        content_size = message_size + headers_size
        if available_bits < content_size:
            raise CapacityException(content_size, available_bits)

    def _get_header_and_message_bin(self, message):
        """
        Generates the binary that must be stored in the image.
        This binary cntains the length ans start tags, the number of characters in the message encoded in 32 bits, and the message in binary
        :param message: the message to be converted to binary
        :return: the binary concatenation of the headers and the actual message
        """
        return self._LENGTH_TAG + cu.int2bin32(len(message)) + self._START_TAG + cu.str2bin(message)

    # TODO find a way to retrieve the indices from which the double for loop must start to skip the length tag
    # def _get_encoded_length(self):
    # x_index = floor(length_to_skip / y_size)
    # y_index = length_to_skip - y_size * x_index - 1

    def _check_length_tag(self):
        length_tag_binary = ""
        for x in range(self.image.size[0]):
            for y in range(self.image.size[1]):
                rgb_tuple = self.pixels[x, y]
                for channel in rgb_tuple:
                    length_tag_binary += cu.get_lsb(cu.int2bin(channel))
                    if len(length_tag_binary) == len(self._LENGTH_TAG):
                        if length_tag_binary != self._LENGTH_TAG:
                            raise NoMessageFoundException("The LENGTH tag was not found.")
