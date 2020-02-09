"""Use steganography to hide data in images."""

from __future__ import division

__all__ = ['PyHide', 'image_from_url', 'image_from_path']
__version__ = '1.0.0'

import logging
import math
import numpy as np
import pickle
import requests
import sys
import zlib
from functools import wraps
from io import BytesIO
try:
    from PIL import Image
except ImportError:
    Image = None
try:
    from PIL import UnidentifiedImageError
except ImportError:
    UnidentifiedImageError = IOError


logger = logging.getLogger('pyhide')
logging.basicConfig(level=logging.INFO)


def requires_image(func):
    """Check the image library exists, or raise a custom exception."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if Image is None:
            raise ImportError('pillow module required for image processing')
        return func(*args, **kwargs)
    return wrapper


@requires_image
def image_from_url(url):
    """Conveniance function to get an Image object from a URL."""

    logger.info('Reading image from "{}"...'.format(url))
    response = requests.get(url, stream=True)
    if response:
        try:
            return Image.open(BytesIO(response.content))
        except UnidentifiedImageError:
            raise UnidentifiedImageError("cannot identify image file '{}'".format(url))
    raise RuntimeError('connection failed with status code {}'.format(response.status_code))


@requires_image
def image_from_path(path):
    """Conveniance function to get an Image object from a path."""

    return Image.open(path)


@requires_image
def set_image_array_depth(image_array, depth):
    """Set the depth of an image array."""
    
    try:
        image_channels = image_array.shape[2]
    except IndexError:
        image_channels = 1

    # Delete channels from base if required
    if depth != image_channels:

        # Delete red and blue channels
        if depth == 1:
            logger.info('Converting base image to luminance...')
            image_array = np.delete(image_array, 0, axis=2)
            image_array = np.delete(image_array, slice(1, None), axis=2)
            image_array = image_array.reshape(image_array.shape[0], image_array.shape[1])
        
        # Create empty red and blue (and alpha) channels
        elif image_channels == 1:
            flat = image_array.ravel()
            insert_points_r = range(0, flat.size, 1)
            flat_r = np.insert(flat, insert_points_r, 255)
            insert_points_b = range(2, flat_r.size+2, 2)
            flat_b = np.insert(flat_r, insert_points_b, 255)
            if depth == 4:
                insert_points_a = range(3, flat_b.size+3, 3)
                flat_a = np.insert(flat_b, insert_points_a, 255)
            else:
                flat_a = flat_b
            image_array = flat_a.reshape(image_array.shape[0], image_array.shape[1], depth)

        # Delete alpha channel
        elif depth == 3:
            logger.info('Converting base image from RGBA to RGB...')
            image_array = np.delete(image_array, 3, axis=2)

        # Create alpha channel
        elif depth == 4:
            flat = image_array.ravel()
            insert_points = range(3, flat.size+3, 3)
            flat_a = np.insert(flat, insert_points, 255)
            image_array = flat_a.reshape(image_array.shape[0], image_array.shape[1], depth)
    return image_array


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
            if sys.version_info.major < 3:
                pickled = map(ord, pickled)
            binary = ''.join(bin(x)[2:].zfill(8) for x in pickled)
            self._payload = np.array(tuple(binary), dtype=int)
            logger.info('Encoded data is {} bytes.'.format(len(self._payload)))
        return self._payload

    @requires_image
    def image_encode(self, mode='RGBA', base=None, ratio=1):
        """Encode data to an image.
        Supported modes are L, RGB and RGBA.
        """

        logger.info('Starting image encode...')
        if mode not in ('L', 'RGB', 'RGBA'):
            raise TypeError('unsupported channel type "{}"'.format(mode))
        channels = len(mode)

        # Convert any PIL object to array
        if isinstance(base, Image.Image):
            base = np.asarray(base, dtype=int)

        # Prepare base image
        if isinstance(base, np.ndarray):
            flat = len(base.shape) < 2

            # Parse the channels input
            if not flat:
                base = set_image_array_depth(base, channels)

            # Calculate number of bits required
            for bits in range(1, 9):
                if self.payload.size <= (base.size * bits) - self.ImageHeaderSize:
                    break
            else:
                raise ValueError('image not large enough to store data (need {} byte{}, {} available)'.format(
                    int(self.payload.size / 8), 's'[:self.payload.size!=8], base.size
                ))

            # Calculate width and height of image
            if flat:
                cells = base.size + self.ImageHeaderSize

                # Ensure width is a factor of the total size
                width = int(round(pow(cells * ratio / channels, 0.5)))
                height = int(cells / width / channels)

                # Since we don't know the base channel count, adjust the array to allow it to reshape
                total_channels = width * height * channels
                if base.size < total_channels:
                    np.append(base, [0] * (base.size - total_channels))
                elif base.size > total_channels:
                    base = base[:total_channels]
                
            else:
                height = base.shape[0]
                width = base.shape[1]
                base = base.ravel()
            
            # Remove the least significant bits from base
            logger.info('Removing least sigificant bits...')
            trimmed_base = base >> bits << bits
            trimmed_base[0:self.ImageHeaderSize] = base[0:self.ImageHeaderSize]

        # Prepare having no base image
        elif base is None:
            bits = 8
            cells = (self.payload.size + self.ImageHeaderSize) / bits
            width = int(round(pow(cells * ratio / channels, 0.5)))
            height = int(math.ceil(cells / width / channels))
            trimmed_base = np.zeros(width * height * channels, dtype=int)
                
        # Don't allow strings, file reading should be done before
        elif base is not None:
            raise TypeError('no support for base type "{}"'.format(type(base)))
        
        logger.info('Using {} bit{} per channel on a {}x{} image.'.format(bits, 's'[:bits!=1], width, height))

        # Convert the payload to a binary array that matches base
        logger.info('Converting payload to match image...')
        if self.payload.size % bits:
            padding = np.append(self.payload, [0] * (bits - self.payload.size % bits))
        else:
            padding = self.payload
        split_payload = pow(2, np.arange(bits)[::-1]) * padding.reshape((padding.size // bits, bits))
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
        if channels == 1:
            shaped = final.reshape((height, width))
        else:
            shaped = final.reshape((height, width, channels))

        try:
            image = Image.fromarray(np.uint8(shaped))
            
         # Fallback to slow method if PIL somehow fails
        except TypeError:
            image = Image.new(mode, (width, height))
            pixel_data = image.load()
            for y in range(height):
                for x in range(width):
                    position = channels * (x + y * width)
                    pixel_data[x, y] = tuple(final[position:position + channels])

        logger.info('Completed image encode.')
        return image
    
    @classmethod
    @requires_image
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
        if sys.version_info.major > 2:
            encoded = encoded.encode('latin-1')
        return pickle.loads(zlib.decompress(encoded))


if __name__ == '__main__':
    # Get random image from URL
    while True:
        wiki_random = 'http://commons.wikimedia.org/wiki/Special:Random/File'
        image_url = str(requests.get(wiki_random).content).split('fullImageLink')[1].split('src="')[1].split('"')[0]
        try:
            image = image_from_url(image_url)
        except UnidentifiedImageError:
            continue
        break
    
    # Generate data to save
    import random
    hide = PyHide([random.uniform(-100000000, 100000000) for i in range(8000)])

    # Test encode over base image (RGB)
    encoded_image = hide.image_encode(mode='RGB', base=image, ratio=1)
    assert PyHide.image_decode(encoded_image) == hide.data

    # Test encode over base image (RGBA)
    encoded_image = hide.image_encode(mode='RGBA', base=image, ratio=1)
    assert PyHide.image_decode(encoded_image) == hide.data

    # Test encode over base image (L)
    encoded_image = hide.image_encode(mode='L', base=image, ratio=1)
    assert PyHide.image_decode(encoded_image) == hide.data

    # Test encode over flat base image
    encoded_image = hide.image_encode(base=np.asarray(image).ravel(), ratio=16/9)
    assert PyHide.image_decode(encoded_image) == hide.data

    # Test encode with no base image
    encoded_image = hide.image_encode()
    assert PyHide.image_decode(encoded_image) == hide.data
