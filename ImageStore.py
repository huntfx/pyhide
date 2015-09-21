from __future__ import division
try:
    from PIL import Image
except:
    raise ImportError( "Python Imaging Library module was not found" )
from collections import defaultdict
from math import log
import zlib
import cPickle
import UsefulThings
import os
import random
reload(UsefulThings)

class ISGlobals(object):
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
        return self.global_dict[x]

class ImageStoreError(Exception):
    pass

class ImageStore(object):
    max_data_len = int('11111111'*255, 2)
    end_of_data = [92,67,104,132,98]
    
    def __init__(self, image_path=None):
        self.defaults = ISGlobals().global_dict
        
        self.image_path = image_path
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
    
    def _metadata_encode(self, input_data):
        """Add a header to the input data.
        
        The first byte determins how many bytes are being used to store
        the amount of data, which can then be used to get the relevant
        part from a longer stream of data.
        The maximum possible bytes to keep through this method is 2040 
        1's in binary, which relates to exactly (2^2040)-1 bytes, or
        approximately 1.26*10^616. Higher than the number of atoms in
        the universe anyway, so it's not really a problem.        
        """
    
        num_bytes = len(input_data)
        if num_bytes > self.max_data_len:
            raise ImageStoreError('you either broke the laws of physics or edited my code')
        num_bytes_binary = str(bin(num_bytes))[2:]
        num_bytes_binary_length = len(num_bytes_binary)
        num_bytes_integer_parts = num_bytes_binary_length // 8 + (1 if num_bytes_binary_length % 8 else 0)
        num_bytes_binary_padded = num_bytes_integer_parts * 8
        num_bytes_new = [num_bytes_binary.zfill(num_bytes_binary_padded)[i:i+8] for i in range(0, num_bytes_binary_padded, 8)]
        marker_length = str(bin(num_bytes_integer_parts))[2:].zfill(8)
        return [int(i, 2) for i in [marker_length] + num_bytes_new] + input_data
    
    def _metadata_decode(self, input_data):
        """Use the header to retrieve the original input data.
        Reverses the process used in _metadata_encode to get the
        original segment of data.
        """
        marker_length = input_data[0]
        offset = marker_length + 1
        data_length = int(''.join(str(bin(i))[2:].zfill(8) for i in input_data[1:offset]), 2)
        return input_data[offset:data_length + offset]
    
    def encode(self, data):
        return zlib.compress(cPickle.dumps(data))
    
    def decode(self, data):
        return cPickle.loads(zlib.decompress(data))
    
    def _save(self, image_data):
        if UsefulThings.make_file_path(self.image_save_path):
            image_data.save(self.image_save_path, 'PNG')
        else:
            raise IOError('unable to write image')
    
    def write(self, input_data, image_ratio=None, verify=None):
        
        if verify is None:
            verify = self.defaults.get('DefaultVerify')
        
        #Convert input to numbers
        encoded_data = [ord(letter) for letter in self.encode(input_data)]
        pixel_data = self._metadata_encode(encoded_data)
        input_bytes = len(pixel_data)
        pixel_data += [0] * (3 - input_bytes % 3) #Pad to multiple of 3
        required_pixels = len(pixel_data) // 3
        
        #Calculate width and height of image
        if image_ratio is None or not 0 < image_ratio < 1:
            image_ratio = log(1920) / log(1920 * 1080)
        image_width = max(3, int(round(pow(required_pixels, image_ratio))))
        image_width //= 3
        image_width *= 3
        image_height = required_pixels / image_width
        if float(image_height) != float(int(image_height)):
            image_height += 1
        image_height = int(image_height)
        pixel_data += [random.choice(pixel_data) for i in range(3 * (image_height * image_width - required_pixels))]
        
        #Draw image
        image_output = Image.new('RGB', (image_width, image_height))
        image_data = image_output.load()
        
        #Assign pixels
        for y in range(image_height):
            for x in range(image_width):
                current_progress = 3 * (x + y * image_width)
                image_data[x, y] = tuple(pixel_data[current_progress:current_progress + 3])
        
        self._save(image_output)
        if verify:
            if input_data != self.read():
                raise ImageStoreError('image failed validation')
        print 'Saved file: {}'.format(self.image_save_path)
        return {'path': self.image_save_path}
    
    def read(self):
        
        try:
            image_input = Image.open(self.image_save_path)
        except IOError:
            raise IOError('no image file found.')
        
        image_data = UsefulThings.flatten_list(image_input.getdata())
        
        truncated_data = self._metadata_decode(image_data)
        decoded_data = self.decode(''.join(chr(number) for number in truncated_data))
        
        return decoded_data
