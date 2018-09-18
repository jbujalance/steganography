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
    _HEADER_LENGTH = len(_LENGTH_TAG) + _LENGTH_BITS + len(_START_TAG)

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
        header_bit_list = self._get_header_bit_list()
        self._check_length_tag(header_bit_list)
        self._check_start_tag(header_bit_list)
        message_binary_length = self._get_encoded_binary_message_length(header_bit_list)
        return self._get_encoded_message(message_binary_length)

    def _check_capacity(self, message):
        """
        Makes sure that there is enough available bits in the image to store the given message.
        :param message: The message to store in the image.
        :exception CapacityException: if there is not enough capacity in the image to store the given message
        """
        height, width = self.image.size
        # TODO The last '1' should be later replaced by the number of LSB bits used per color chanel
        available_bits = height * width * 3 * 1
        # In ASCII, each character is encoded in 7 bits, and each link between characters take 1 bit
        message_size = len(message) * 7 + len(message) - 1
        content_size = message_size + self._HEADER_LENGTH
        if available_bits < content_size:
            raise CapacityException(content_size, available_bits)

    def _get_header_and_message_bin(self, message):
        """
        Generates the binary that must be stored in the image.
        This binary contains the length ans start tags, the number of binary characters in the message encoded in 32 bits, and the message in binary
        :param message: the message to be converted to binary
        :return: the binary concatenation of the headers and the actual message
        """
        binary_message = cu.str2bin(message)
        return self._LENGTH_TAG + cu.int2bin32(len(binary_message)) + self._START_TAG + binary_message

    def _check_length_tag(self, bit_list):
        """
        Checks if the LENGTH tag is encoded in the image.
        :param bit_list: the list of encoded bits
        :exception NoMessageFoundException: if the LENGTH tag is not present
        """
        sublist = bit_list[:len(self._LENGTH_TAG)]
        retrieved_tag = "".join(sublist)
        if retrieved_tag != self._LENGTH_TAG:
            raise NoMessageFoundException("The LENGTH tag was not found.")

    def _check_start_tag(self, bit_list):
        """
        Checks if the START tag is present in the encoded bits
        :param bit_list: the list of encoded bits
        :exception NoMessageFoundException: if the START tag is not present
        """
        sublist = bit_list[len(self._LENGTH_TAG) + self._LENGTH_BITS:len(self._LENGTH_TAG) + self._LENGTH_BITS + len(self._START_TAG)]
        retrieved_tag = "".join(sublist)
        if retrieved_tag != self._START_TAG:
            raise NoMessageFoundException("The START tag was not found.")

    def _get_encoded_binary_message_length(self, bit_list):
        """
        Gets the binary length of the encoded message.
        :param bit_list: the encoded bits
        :return: the number of binary characters that conform the encoded message
        """
        sublist = bit_list[len(self._LENGTH_TAG):len(self._LENGTH_TAG) + self._LENGTH_BITS]
        binary_length = "".join(sublist)
        return cu.bin2long(binary_length)

    def _get_encoded_message(self, message_length):
        """
        Retrieves the translated encoded message.
        :param message_length: the length of the binary representing the encoded message
        :return: human-readable encoded message
        """
        binary = "".join(self._get_message_bit_list(message_length))
        return cu.bin2str(binary)

    def _get_header_bit_list(self):
        """
        :return: The list of bits conforming the header of the message
        """
        header_list = list()
        for x in range(self.image.size[0]):
            for y in range(self.image.size[1]):
                rgb_tuple = self.pixels[x, y]
                for channel in rgb_tuple:
                    header_list.append(cu.get_lsb(cu.int2bin(channel)))
                    if len(header_list) == self._HEADER_LENGTH:
                        return header_list

    def _get_message_bit_list(self, message_length):
        """
        :param message_length: the length of the binary representing the encoded message
        :return: The list of bits conforming the encoded binary message
        """
        message_bits = list()
        # TODO we can do better: it is useless to iterate over the header to skip it.
        # Use some formula to get the initial x and y from which to start iterating in order to skip the header
        index = AutoIncrementInt(0)
        for x in range(self.image.size[0]):
            for y in range(self.image.size[1]):
                rgb_tuple = self.pixels[x, y]
                for channel in rgb_tuple:
                    if index.get_and_increment() >= self._HEADER_LENGTH:
                        message_bits.append(cu.get_lsb(cu.int2bin(channel)))
                    if len(message_bits) == message_length:
                        return message_bits
