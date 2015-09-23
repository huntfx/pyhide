from __future__ import division
try:
    from PIL import Image
except:
    raise ImportError( "Python Imaging Library module was not found" )
from collections import defaultdict
from math import log
import cStringIO
import urllib2
import zlib
import cPickle
import UsefulThings
import os
import random
reload(UsefulThings)

class ISGlobals(object):
    """Class for determining default values, where it
    will read any changes from a config file.
    """
    def __init__(self, save_all_config_values=False):
        
        #Build list of default values
        link_dict = {}
        link_dict['%USERDIR'] = os.path.expanduser( "~" ).replace( "\\", "/" )
        link_dict['%PYTHONDIR'] = os.getcwd().replace( "\\", "/" )
        link_dict['%APPDATA'] = os.getenv('APPDATA')
        required_globals = defaultdict(dict)
        required_globals['ImageStore']['!DirectoryLinks'] = '%PYTHONDIR, %USERDIR, %APPDATA'
        default_globals = defaultdict(dict)
        default_globals['ImageStore']['ShowAllValuesHereOnNextRun'] = False
        default_globals['ImageStore']['DefaultImageName'] = 'ImageDataStore.png'
        default_globals['ImageStore']['DefaultImageDirectory'] = '%USERDIR/ImageStore'
        default_globals['ImageStore']['DefaultCustomImage'] = 'http://'
        default_globals['ImageStore']['DefaultUpload'] = True
        default_globals['ImageStore']['DefaultVerify'] = True
        hidden_globals = defaultdict(dict)
        hidden_globals['ImageStore']['CacheName'] = 'ImageStore.cache'
        hidden_globals['ImageStore']['CacheDirectory'] = '%APPDATA/ImageStore'
        hidden_globals['ImageStore']['ForceUpload'] = False
        hidden_globals['ImageStore']['ForceOpenOnUpload'] = False
        hidden_globals['ImageStore']['ForceNoSave'] = False
        hidden_globals['ImageStore']['ForceVerify'] = False
        hidden_globals['ImageStore']['ForceCustomImage'] = False
        required_globals = dict(required_globals)
        default_globals = dict(default_globals)
        hidden_globals = dict(hidden_globals)
        
        #Update the config and get the values
        config_location = '%APPDATA/VFXConfig.ini'
        for k in link_dict:
            config_location = config_location.replace(k, link_dict[k])
            
        required_globals = UsefulThings.read_config(config_location, config_sections=required_globals, write_values=True, update_values=True)
        default_globals = UsefulThings.read_config(config_location, config_sections=default_globals, write_values=True, update_values=False)
        hidden_globals = UsefulThings.read_config(config_location, config_sections=hidden_globals, write_values=save_all_config_values, update_values=False)
        
        all_globals = dict(default_globals).copy()
        all_globals['ImageStore'].update(hidden_globals['ImageStore'])
        self.global_dict = UsefulThings.read_config(config_location, config_sections=all_globals, write_values=False, update_values=False)['ImageStore']
        
        self.global_dict = {k: v for k, v in self.global_dict.iteritems() if k[0] not in ('!', ';')}
        
        #Convert links to the correct format
        for i in link_dict:
            self.global_dict = {k: (v.replace(i, link_dict[i]) if isinstance(v, str) else v) for k, v in self.global_dict.iteritems()}
        
        if not save_all_config_values and self.global_dict['ShowAllValuesHereOnNextRun']:
            ISGlobals(True)
    
    def get(self, x):
        """Easy way of getting a certain value."""
        return self.global_dict[x]

class ImageStoreError(Exception):
    pass

class ImageStore(object):
    """Class for writing and reading data in the actual pixels
    in an image.
    
    Header Information:
        To mark the bits used and end of file, a header is stored
        at the beginning of the image. 
        The first byte of the image (red value of the pixel), 
        is used as an integer that stores two values. The 
        last number determins how many bits are used per pixel, 
        and the first two numbers determine how many bytes are 
        used to store how many bytes are in the image.
        
        The second part is storing how many bytes are in the 
        image, though this is encoded with the rest of the image. 
        If the bits per pixel value is below 8, the image must be 
        pieced back together before this information can be
        retrieved.
        
        For example, if the number was 123, the image would be
        storing 3 bits per colour, and the next 12 bytes would
        contain the length of data. Once the image is combined,
        piece together the binary data from bytes [1:13] and convert
        to an integer to get the length of data. The data will be
        stored at [14:14+length of data].
        
        As to a practical example, if the number was 48, and the 
        next 4 bytes were [39, 29, 177, 252], the number of bytes 
        would be 656257532, and the data would be at 
        image_data[6:656257538].
        
        The absolute maximum data size through using this method
        is 2.6*10^239 bytes, which is more than the number of atoms
        in the universe, so I think it's safe to say nobody will 
        go above it.
    """
    max_data_len = int('1'*8*99, 2)
    
    def __init__(self, image_path=None, print_time=True):
        self.defaults = ISGlobals().global_dict
        
        self.print_time = print_time
        
        #Get a valid image path
        self.image_path = image_path
        self.image_path_original = image_path
        if image_path is None:
            self.image_path = '{}/{}'.format(self.defaults.get('DefaultImageDirectory'), self.defaults.get('DefaultImageName'))
        else:
            if ':/' not in image_path:
                if image_path.startswith('/'):
                    image_path = image_path[1:]
                self.image_path = '{}/'.format(self.defaults.get('DefaultImageDirectory')) + image_path
                
        self.image_save_path = self.image_path
        if '.' in self.image_save_path.split('/')[-1]:
            self.image_save_path = self.image_save_path[::-1].split('.', 1)[1][::-1]
        self.image_save_path += '.png'
    
    def encode(self, data):
        """Encode the image data, this may be edited as long
        as ImageStore.decode can reverse it.
        This is where you would add encryption.
        """
        return zlib.compress(cPickle.dumps(data))
    
    def decode(self, data):
        """Decode the image data."""
        try:
            return cPickle.loads(zlib.decompress(data))
        except (cPickle.UnpicklingError, zlib.error):
            raise ImageStoreError('failed to decode image data')
    
    def _save_image(self, image_data):
        """Wrapper for saving the image, will attempt to build the 
        file path if it doesn't exist, and will save the image.
        """
        if UsefulThings.make_file_path(self.image_save_path):
            image_data.save(self.image_save_path, 'PNG')
        else:
            raise IOError('unable to write image')
    
    
    def _read_image(self, image_location): 
        """Wrapper for opening the image, supports opening from a
        URL or just the computer.
        """
        #Load from URL
        if any(value in image_location for value in ('http://', 'https://', 'ftp://')):
            try:
                location = cStringIO.StringIO(urllib2.urlopen(image_location).read())
            except urllib2.URLError:
                raise urllib2.URLError('failed to load image from URL')
                
        #Open image
        try:
            return Image.open(image_location).convert('RGB')
        except IOError:
            IOError('failed to open image file')
    
    def _print(self, item, indent=' '):
        """Print wrapper to allow disabling all messages."""
        if self.print_time:
            print '{}{}'.format(indent, item)
    
    def _time(self, verb, TimeThisObject):
        self._print('{}: {}'.format(TimeThisObject.output(), verb), '')
    
    def write(self, input_data, custom_image=None, image_ratio=None, verify=None):
        """Write data to an image.
        
        If a custom image is used, bits per byte is calculated.
        This determins how many bits are used to store data in
        each colour value in the image. This ranges from 1, which
        is virtually invisible to the human eye, to 8, which
        would erase the original image. 
        The input image is processed to remove the final few bits,
        and is padded back to 8 bits using the data to store. The
        final padding is just a duplicate of the data, so it's not
        obvious where the data first finished.
        
        Parameters:
            input_data (any): Data to be written to the image.
                May be in any format as it is serialised and
                compressed, this also can be a file.
            
            custom_image (str or None): Path or URL to an image
                to write on top of. If left as None, the smallest
                possible image will be written but will look
                like random noise.
            
            image_ratio (str or None): If the custom image is,
                not provided, we have no idea of the image dimensions. 
                This determins the ratio of with to height.
                When giving a value, make sure a colon is
                separating two numbers for it to work.
                If None, will default to a 16:9 resolution.
                
            
            verify (bool or None): If the code should read the 
                image after writing to make sure the data is 
                intact. This can add a few seconds of processing 
                so you may disable it.
                If left as None, it will use the default value 
                provided in the config.
        """
        with UsefulThings.TimeThis(print_time=False) as t:
            
            self._print('Writing to image...', '')
            
            if verify is None:
                verify = self.defaults.get('DefaultVerify')
            bits_per_byte = 8
                        
            encoded_data = [ord(letter) for letter in self.encode(input_data)]
            self._time('Encoded data', t)
            
            #Build header info
            num_bytes = len(encoded_data)
            if num_bytes > self.max_data_len:
                raise ImageStoreError('congrats for breaking the laws of physics (you have more input bytes than atoms in universe)')
            num_bytes_binary = str(bin(num_bytes))[2:]
            num_bytes_length = len(num_bytes_binary)
            num_bytes_integer_parts = num_bytes_length // 8 + (1 if num_bytes_length % 8 else 0)
            num_bytes_total_length = num_bytes_integer_parts * 8
            num_bytes_new = [num_bytes_binary.zfill(num_bytes_total_length)[i:i+8] for i in range(0, num_bytes_total_length, 8)]
            pixel_data = [int(i, 2) for i in num_bytes_new] + encoded_data
            
            self._time('Calculated header', t)
            
            if custom_image is not None:
                
                #Read and process custom image
                custom_image_input = self._read_image(custom_image)
                image_width, image_height = custom_image_input.size
                max_image_bytes = image_width * image_height
                
                self._time('Read custom image', t)
                
                #Calculate required bits per byte
                total_data_bytes = len(pixel_data) + 1
                
                self._print("Image resolution: {}x{} ({} pixels)".format(image_width, image_height, max_image_bytes))
                self._print("Input data: {} bytes".format(total_data_bytes))
                bits_per_byte = 1
                self._print("Checking the smallest possible bits per byte to use...")
                
                while bits_per_byte < 9:
                    storage_needed = total_data_bytes * (8 / (bits_per_byte))
                    self._print(" {}: Up to {} bytes".format(bits_per_byte, int(round(storage_needed))))
                    if storage_needed < max_image_bytes:
                        break
                    bits_per_byte += 1
                    
                    #Data won't fit in image, revert to normal method
                    if bits_per_byte == 8:
                        custom_image = None
                        image_ratio = '{}:{}'.format(image_width, image_height)
                        break
                
                self._time('Calculated bits to use', t)
                
                if custom_image is not None:
                    
                    #Process both parts of data
                    # joined_binary_data needs to have an extra part added on the end to stop
                    # a strange error where it occasionally writes the incorrect final bits
                    joined_binary_data = ''.join(str(bin(x))[2:].zfill(8) for x in pixel_data) + '0' * bits_per_byte
                    split_binary_data = UsefulThings.split_list(joined_binary_data, bits_per_byte)
                    num_pixels_needed = len(split_binary_data)
                    split_image_data = UsefulThings.flatten_list(custom_image_input.getdata())
                    
                    self._time('Processed input data and image', t)
                    
                    reduced_image = [str(bin(i))[2:].zfill(8)[:-bits_per_byte] for i in split_image_data]
                    self._time('Reduced bits of custom image', t)
                    
                    #Copy the split_binary_data until it is of the required length
                    extra_length_needed = len(split_image_data) - len(split_binary_data)
                    while len(split_binary_data) < extra_length_needed:
                        split_binary_data *= 2
                    
                    pixel_data = [int(reduced_image[i] + split_binary_data[i-1], 2) for i in range(len(reduced_image))]
                    
                    self._time('Merged input data with custom image', t)
                
                else:
                    self._print('Data does not fit in image, reverting to normal storage...', '')
                
            if custom_image is None:
                
                #Convert input to numbers
                pixel_data = [0] + pixel_data
                input_bytes = len(pixel_data)
                pixel_data += [0] * (3 - input_bytes % 3) #Pad to multiple of 3
                total_bytes = len(pixel_data) // 3
                required_pixels = int(total_bytes * 8 / bits_per_byte)
                
                #Calculate width and height of image
                if ':' in str(image_ratio):
                    image_ratio_split = [max(1, float(i)) for i in image_ratio.split(':')]
                    
                else:
                    image_ratio_split = [16, 9]
                    
                x = pow(required_pixels * image_ratio_split[0] * image_ratio_split[1], 0.5)
                
                image_width = max(3, min(required_pixels, int(round(x/image_ratio_split[1]))))
                image_width //= 3
                image_width *= 3
                image_height = required_pixels / image_width
                if float(image_height) != float(int(image_height)):
                    image_height += 1
                image_height = int(image_height)

                self._time('Calculated image size', t)
                
                pixel_data += [random.choice(pixel_data) for i in range(3 * (image_height * image_width - required_pixels))]
                self._time('Padded data', t)
            
            
            initial_header = int(str(num_bytes_integer_parts) + str(bits_per_byte))
            pixel_data[0] = initial_header
            
            #Draw image
            image_output = Image.new('RGB', (image_width, image_height))
            image_data = image_output.load()
            
            #Assign pixels
            for y in range(image_height):
                for x in range(image_width):
                    current_progress = 3 * (x + y * image_width)
                    image_data[x, y] = tuple(pixel_data[current_progress:current_progress + 3])
            
            self._time('Created image', t)
                
            self._save_image(image_output)
            
            self._time('Saved file', t)
            if verify:
                if input_data != ImageStore(self.image_save_path, print_time=False).read():
                    raise ImageStoreError('image failed validation')
                self._time('Verified file', t)
            print 'Saved file at {}'.format(self.image_save_path)
            return {'path': self.image_save_path}
    
    def read(self):
        """Attempt to read the stored data from an image.
        
        To undo the write process, if a custom image is used,
        each colour must be broken down into bits and the last
        few bits are taken then pieced together. If these are
        split into groups of 8 and converted back to characters,
        it results in the original encoded string.
        """
        with UsefulThings.TimeThis(print_time=False) as t:
            
            self._print('Reading image...', '')
        
            try:
                image_input = Image.open(self.image_save_path)
            except IOError:
                #The image link will have been edited if not PNG, check the original link
                _image_name = self.image_path_original.split('/')[-1]
                if '.' in _image_name and 'png' not in _image_name:
                    raise ImageStoreError('image format needs to be PNG')
                raise IOError('no image file found')
            self._time('Read image', t)
            
            #Get data and header
            image_data = UsefulThings.flatten_list(image_input.getdata())
            image_header = str(image_data[0])
            bytes_per_pixel = int(image_header[-1])
            num_bytes_parts = int(image_header[:-1])
            image_data = image_data[1:]
            self._time('Processed image', t)
            
            #Get the required pixels as binary, piece together, and convert back to int
            if bytes_per_pixel != 8:
                
                image_data_parts = [str(bin(i))[2:].zfill(8)[8-bytes_per_pixel:] for i in image_data]
                image_data_binary = ''.join(image_data_parts)
                image_data_split = UsefulThings.split_list(image_data_binary, 8)
                num_bytes = int(''.join(image_data_split[:num_bytes_parts]), 2)
                truncated_data = [int(i, 2) for i in image_data_split[num_bytes_parts:num_bytes+num_bytes_parts]]
            
            else:
                #Does same as above, but avoids converting the entire data to binary since there is no extra data
                num_bytes_raw = image_data[:num_bytes_parts]
                num_bytes_binary = ''.join(str(bin(i))[2:].zfill(8) for i in num_bytes_raw)
                num_bytes = int(num_bytes_binary, 2)
                truncated_data = image_data[num_bytes_parts:num_bytes + num_bytes_parts]
            
            self._time('Got required data', t)
            
            decoded_data = self.decode(''.join(chr(number) for number in truncated_data))
            
            self._time('Decoded data', t)
            
            return decoded_data
