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
        bit_list = self._get_bit_list()
        self._check_length_tag(bit_list)
        self._check_start_tag(bit_list)
        return self._get_encoded_message(bit_list)

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
        headers_size = len(self._LENGTH_TAG) + self._LENGTH_BITS + len(self._START_TAG)
        content_size = message_size + headers_size
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

    def _get_encoded_message(self, bit_list):
        """
        Retrieves the translated encoded message.
        :param bit_list:  the encoded bits
        :return: human-readable encoded message
        """
        header_length = len(self._LENGTH_TAG) + self._LENGTH_BITS + len(self._START_TAG)
        message_length = self._get_encoded_binary_message_length(bit_list)
        binary = "".join(bit_list[header_length:header_length + message_length])
        return cu.bin2str(binary)

    def _get_bit_list(self):
        """
        :return: all the LSB used for message encryption in the image
        """
        # TODO there is no need to loop over all the image's pixels. We just need the bits until the end of the message
        bit_list = list()
        for x in range(self.image.size[0]):
            for y in range(self.image.size[1]):
                rgb_tuple = self.pixels[x, y]
                for channel in rgb_tuple:
                    bit_list.append(cu.get_lsb(cu.int2bin(channel)))
        return bit_list
