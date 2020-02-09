import math
import logging
import numpy as np
import pickle
import requests
import zlib
from io import BytesIO
from PIL import Image


logger = logging.getLogger('pyhide')
logging.basicConfig(level=logging.INFO)


def image_from_url(url):
    """Read a URL to get an Image object."""
    response = requests.get(url, stream=True)
    if response:
        return Image.open(BytesIO(response.content))
    raise RuntimeError('connection failed with status code {}'.format(response.status_code))


def image_from_path(path):
    """Read a path to get an Image object."""
    return Image.open(path)


class PyHide(object):
    """Encode data in other data with steganography."""

    ImageHeaderSize = 3

    def __init__(self, data):
        self.data = data

    @property
    def payload(self):
        """Data formatted as a binary array."""
        try:
            return self._payload
        except AttributeError:
            logger.info('Encoding data...')
            pickled = zlib.compress(pickle.dumps(self.data))
            binary = ''.join(bin(x)[2:].zfill(8) for x in pickled)
            self._payload = np.array(tuple(binary), dtype=int)
            logger.info('Encoded data is {} bytes.'.format(len(self._payload)))
        return self._payload

    def image_encode(self, channels='RGBA', base=None, ratio=1):
        """Encode data to an image.
        Supported modes are L, RGB and RGBA.
        """
        logger.info('Starting image encode...')
        channels = list(channels)

        # Convert any PIL object to array
        if isinstance(base, Image.Image):
            base = np.asarray(base, dtype=int)

        if isinstance(base, np.ndarray):
            # The format should be in (width, height, depth)
            # or (width, height) if depth is 1
            if len(base.shape) >= 2:
                height = base.shape[0]
                width = base.shape[1]
                try:
                    channels = [i for i in ('RGB', 'RGBA')[base.shape[2]>3] if i in channels]
                except IndexError:
                    channels = ['L']
                num_channels = len(channels)
                base = base.ravel()
            
            else:
                channels = [i for i in 'RGBA' if i in channels]
                if not channels:
                    channels = ['L']
                num_channels = len(channels)

                for bits in range(1, 8):
                    if self.payload.size <= (base.size * bits) - self.ImageHeaderSize:
                        break
                else:
                    raise ValueError('image not large enough to store data')

                cells = base.size + self.ImageHeaderSize

                # Convert width to be a factor of the total size
                width = int(round(pow(cells * ratio / num_channels, 0.5)))
                if base.size % width:
                    width_ratio = base.size / width
                    if width_ratio % 1 < 0.5:
                        multiplier = -1
                    else:
                        multiplier = 1
                    while base.size % width:
                        width += multiplier

                height = int(cells / width / num_channels)
                
        # Don't allow strings, file reading should be done before
        elif base is not None:
            raise TypeError('no support for base type "{}"'.format(type(base)))
        
        if base is None:
            bits = 8
            channels = [i for i in 'RGBA' if i in channels]
            if not channels:
                channels = ['L']
            num_channels = len(channels)

            cells = (self.payload.size + self.ImageHeaderSize) / bits
            width = int(round(pow(cells * ratio / num_channels, 0.5)))
            height = int(math.ceil(cells / width / num_channels))
            trimmed_base = np.zeros(width * height * num_channels, dtype=int)
        
        else:
            # Calculate how many bits per channel to use
            for bits in range(1, 8):
                if self.payload.size <= (base.size * bits) - self.ImageHeaderSize:
                    break
            else:
                raise ValueError('image not large enough to store data')
            
            # Remove the least significant bits from base
            logger.info('Removing least sigificant bits...')
            trimmed_base = base >> bits << bits
            trimmed_base[0:self.ImageHeaderSize] = base[0:self.ImageHeaderSize]

        logger.info('Using {} bit{} per channel on a {}x{} image.'.format(bits, 's'[:bits!=1], width, height))

        # Convert the payload to a binary array that matches base
        logger.info('Converting payload to match image...')
        padding = np.append(self.payload, [0] * (bits - self.payload.size % bits))
        split_payload = pow(2, np.arange(bits)[::-1]) * padding.reshape(padding.size // bits, bits)
        joined_payload = np.sum(split_payload, axis=1)

        # Add the payload to the base array
        logger.info('Merging payload into image...')
        padded_payload = np.zeros(trimmed_base.shape, dtype=int)
        padded_payload[self.ImageHeaderSize:joined_payload.shape[0] + self.ImageHeaderSize] = joined_payload
        final = trimmed_base + padded_payload

        # Set header
        logger.info('Creating image header...')
        if bits == 8:
            bits = 0  # 8 bits is too large to store, and 0 will never be used otherwise
        bits_binary = bin(bits)[2:].zfill(self.ImageHeaderSize)
        for i in range(self.ImageHeaderSize):
            final[i] = int(bin(final[i])[2:-1] + bits_binary[i], 2)

        # Create image
        logger.info('Generating image...')
        if num_channels == 1:
            shaped = final.reshape((height, width))
        else:
            shaped = final.reshape((height, width, num_channels))

        try:
            image = Image.fromarray(np.uint8(shaped))
            
         # Fallback to slow method if PIL somehow fails
        except TypeError:
            image = Image.new(''.join(channels), (width, height))
            pixel_data = image.load()
            for y in range(height):
                for x in range(width):
                    position = num_channels * (x + y * width)
                    pixel_data[x, y] = tuple(final[position:position + num_channels])

        logger.info('Completed image encode.')
        return image
    
    @classmethod
    def image_decode(cls, image):
        """Get data from a previously encoded image."""
        if isinstance(image, Image.Image):
            image = np.asarray(image, dtype=int)
        flattened = image.ravel()

        # Get the number of bits used
        logger.info('Reading image header...')
        bits = int(''.join(bin(i)[-1] for i in flattened[0:cls.ImageHeaderSize]), 2)
        if not bits:
            bits = 8

        # Grab the original data from the array
        logger.info('Decoding data...')
        shifted = flattened >> bits << bits
        raw_data = (flattened - shifted)[cls.ImageHeaderSize:]

        # Reconstruct the data
        logger.info('Reconstructing data...')
        binary_data = ''.join(bin(i)[2:].zfill(bits) for i in raw_data)
        encoded = ''.join(chr(int(binary_data[i:i + 8], 2)) for i in range(0, len(binary_data), 8))

        logger.info('Completed image decode.')
        return pickle.loads(zlib.decompress(encoded.encode('latin-1')))


if __name__ == '__main__':
    # Get random image from URL
    #wiki_random = 'http://commons.wikimedia.org/wiki/Special:Random/File'
    #image_url = str(requests.get(wiki_random).content).split('fullImageLink')[1].split('src="')[1].split('"')[0]
    #image = image_from_url(image_url)
    image = image_from_path(r"D:\Peter\Downloads\rku6ks73wlj01.jpg")
    
    # Generate data to save
    import random
    hide = PyHide([random.uniform(-100000000, 100000000) for i in range(200000)])

    # Test encode over base image
    encoded_image = hide.image_encode(channels='RGB', base=np.asarray(image).ravel(), ratio=16/9)
    encoded_image.save(r"D:\Peter\Downloads\test.png")
    assert PyHide.image_decode(encoded_image) == hide.data

    '''
    # Test encode with no base image
    encoded_image = hide.image_encode()
    assert PyHide.image_decode(encoded_image) == hide.data
    '''
