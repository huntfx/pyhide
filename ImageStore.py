from __future__ import division
from PIL import Image
import numpy as np
import time
import cPickle
import base64
import zlib


def trim_bytes(numpy_array, num_bytes):
    """Quick way of removing the smallest n bits from an array of bytes."""
    return numpy_array >> num_bytes

def get_image_data(path):
    """Get 1D pixel data from an image quickly using numpy."""
    im = Image.open(path).convert('RGB')
    return np.asarray(im).ravel()

def split_input(value, n):
    return [value[i:i + n] for i in range(0, len(value), n)]

def encode_input(value):
    return zlib.compress(cPickle.dumps(value))

def decode_input(value):
    return cPickle.loads(zlib.decompress(value))

print split_input('11100110111', 8)

class Steganography(object):

    MAX_LEN = 256 ** 256 - 1
    DEBUG = True
    _MARKER = '01100110111' #Must be 11 bytes
    
    def __init__(self, input_data, original_data):
        
        self.i = encode_input(input_data)
        self.o = np.asarray(original_data)

        #Detect whether the input should be compressed
        self.enc = True
        if isinstance(input_data, str):
            if len(self.i) > len(input_data):
                self.i = input_data
                self.enc = False
        
        self.i_ord = [ord(i) for i in self.i]
        self.i_len = len(self.i_ord)
        self.o_len = len(self.o)

        #Basic error checking
        if self.i_len > self.MAX_LEN:
            raise OverflowError('input data is too large')
        if not self.i_len:
            raise ValueError('input data is empty')
        if not self.o_len:
            raise ValueError('original data is empty')

    @classmethod
    def _print(self, message, value=None, indent=0):
        if self.DEBUG:
            if value is None:
                print '{}{}'.format(' '*indent, message)
            else:
                print '{}{}: {}'.format(' '*indent, message, value)
    
    def generate_header(self):

        #Find how much space it is to store the length of data
        input_len_binary = '{0:b}'.format(self.i_len)
        input_len_padding = len(input_len_binary) // 8
        input_len_binary = input_len_binary.zfill(8 * (input_len_padding + 1))

        marker = split_input(self._MARKER, 8)
        if len(marker[0]) != 8 or len(marker[1]) != 3:
            raise ValueError('incorrect marker size')
        header = [int(marker[0], 2), None, input_len_padding]
        header += [int(i, 2) for i in split_input(input_len_binary, 8)]

        #Find how many bytes per colour are needed
        bytes_available = self.o_len - len(header)

        if bytes_available < self.i_len:
            raise ValueError('not enough space to encode data')
        
        for i in range(8):
            if self.i_len * (8 - i) < bytes_available:
                break
            
        bytes_per_colour = i + 1
        
        #header[0] = int('{0:04b}'.format(i + 1) + str(int(self.enc)) + '000', 2)
        header[1] = int(marker[1] + str(int(self.enc)) + '{0:04b}'.format(i + 1), 2)
        
        self._print('Bytes per colour', bytes_per_colour, indent=1)
        self._print('Input length', self.i_len, indent=1)
        self._print('Compressed', bool(self.enc), indent=1)
        self._print('Total bytes available', self.o_len, indent=1)
        self._print('Header bytes', len(header), indent=1)
        self._print('Remaining bytes', bytes_available, indent=1)
      

        return header, bytes_per_colour
        
    def encode(self):

        #Generate header
        self._print('Generating header...')
        data, bytes_per_colour = self.generate_header()

        #Convert data
        self._print('Converting input data to binary...')
        trimmed_original = trim_bytes(self.o, bytes_per_colour)
        format_binary = '{0:0' + '{}'.format(8 - bytes_per_colour) + 'b}'
        original_bytes = [format_binary.format(i) for i in trimmed_original]

        new_bytes = split_input(''.join('{0:08b}'.format(i) for i in self.i_ord), bytes_per_colour)
        new_bytes[-1] += '0' * (bytes_per_colour - len(new_bytes[-1]))
        
        #Increase length until both inputs match
        self._print('Matching length...')
        if bytes_per_colour == 8:
            required_length = len(data)
        else:
            required_length = len(original_bytes) - len(data)
            
        while True:
            new_byte_len = len(new_bytes)
            if new_byte_len >= required_length:
                break
            extra_length = min(new_byte_len, required_length - new_byte_len)
            new_bytes += new_bytes[:extra_length]
            self._print('Increased length from {} to {}'.format(new_byte_len, new_byte_len + extra_length), indent=1)

        self._print('Completed encoding')
        if bytes_per_colour == 8:
            return data + [int(i, 2) for i in new_bytes]
        else:
            return data + [int(a + b, 2) for a, b in zip(original_bytes[len(data):], new_bytes)]


    @classmethod
    def read_header(self, data):

        initial_data = '{0:08b}'.format(data[1])
        marker = '{0:08b}'.format(data[0]) + initial_data[0:3]
        if marker != self._MARKER:
            raise ValueError('incorrect marker')
        bytes_per_colour = int(initial_data[4:8], 2)
        encoded = int(initial_data[3], 2)

        num_bytes = int(''.join('{0:08b}'.format(i) for i in data[3:data[2] + 4]), 2)
        
        self._print('Bytes per colour', bytes_per_colour, indent=1)
        self._print('Input length', num_bytes, indent=1)
        self._print('Compressed', bool(encoded), indent=1)
        
        return data[data[2] + 4:], bytes_per_colour, data[2], num_bytes, encoded

        
    @classmethod 
    def decode(self, data):

        self._print('Reading header...')
        data, bytes_per_colour, data_len, num_bytes, encoded = self.read_header(data)
        
        self._print('Decoding data...')
        encoded_data = split_input(
                ''.join('{0:08b}'.format(i)[8 - bytes_per_colour:] for i in data), 8
        )[:num_bytes]
        decoded_data = ''.join(chr(int(i, 2)) for i in encoded_data)
        
        self._print('Completed decoding')
        if encoded:
            return decode_input(decoded_data)
        else:
            return decoded_data


orig = get_image_data("ImageStore/1.png")
data = 'Whats up doc. Just a test!!'

enc = Steganography(data, orig).encode()
print Steganography.decode(enc)


