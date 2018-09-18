import binascii


class ConversionUtils:

    @staticmethod
    def int2bin(integer):
        return '{0:08b}'.format(integer)

    @staticmethod
    def int2bin32(integer):
        """
        Converts an integer into a 32 bit binary
        :param integer: integer to convert
        :return: the 32-bit binary corresponding to the given integer
        """
        return format(integer, '032b')

    @staticmethod
    def bin2long(binary):
        return long(binary, 2)

    @staticmethod
    def str2bin(string):
        binary = bin(int(binascii.hexlify(string), 16))
        return binary[2:]

    @staticmethod
    def bin2str(binary):
        return binascii.unhexlify('%x' % (int('0b' + binary, 2)))

    @staticmethod
    def bin2int(binary_string):
        return int(binary_string, 2)

    @staticmethod
    def replace_lsb(binary, bit):
        binary = binary[:-1] + bit
        return binary

    @staticmethod
    def get_lsb(binary):
        return binary[len(binary) - 1]
