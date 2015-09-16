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

class ISGlobals(object):
    def __init__(self):
        
        #Build list of default values
        link_dict = {}
        link_dict['%USERDIR'] = os.path.expanduser( "~" ).replace( "\\", "/" )
        link_dict['%PYTHONDIR'] = os.getcwd().replace( "\\", "/" )
        required_globals = defaultdict(dict)
        required_globals['ImageStore']['!DirectoryLinks'] = '%PYTHONDIR, %USERDIR'
        default_globals = defaultdict(dict)
        default_globals['ImageStore']['DefaultImageName'] = 'ImageDataStore.png'
        default_globals['ImageStore']['DefaultImageDirectory'] = '%USERDIR/ImageStore'
        default_globals['ImageStore']['DefaultCustomImage'] = 'http://'
        default_globals['ImageStore']['DefaultUpload'] = True
        default_globals['ImageStore']['DefaultVerify'] = True
        hidden_globals = defaultdict(dict)
        hidden_globals['ImageStore']['ForceUpload'] = False
        hidden_globals['ImageStore']['ForceOpenOnUpload'] = False
        hidden_globals['ImageStore']['ForceNoSave'] = False
        hidden_globals['ImageStore']['ForceVerify'] = False
        hidden_globals['ImageStore']['ForceCustomImage'] = False
        required_globals = dict(required_globals)
        default_globals = dict(default_globals)
        hidden_globals = dict(hidden_globals)
        
        #Update the config and get the values
        required_globals = UsefulThings.read_config('c:/test.ini', config_sections=required_globals, write_values=True, update_values=True)
        default_globals = UsefulThings.read_config('c:/test.ini', config_sections=default_globals, write_values=True, update_values=False)
        hidden_globals = UsefulThings.read_config('c:/test.ini', config_sections=hidden_globals, write_values=False, update_values=False)
        
        all_globals = dict(default_globals).copy()
        all_globals['ImageStore'].update(hidden_globals['ImageStore'])
        self.global_dict = UsefulThings.read_config('c:/test.ini', config_sections=all_globals, write_values=False, update_values=False)['ImageStore']
        
        self.global_dict = {k: v for k, v in self.global_dict.iteritems() if k[0] not in ('!', ';')}
        
        #Convert links to the correct format
        for i in link_dict:
            self.global_dict = {k: (v.replace(i, link_dict[i]) if isinstance(v, str) else v) for k, v in self.global_dict.iteritems()}
    
    def get(self, x):
        return self.global_dict[x]

class SuccessfulTruncate(Exception):
    pass
class ImageStoreError(Exception):
    pass

class ImageStore(object):
    end_of_data = [255, 0]
    
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
    
    def encode(self, data):
        return zlib.compress(cPickle.dumps(data))
    
    def decode(self, data):
        return cPickle.loads(zlib.decompress(data))
    
    def _save(self, image_data):
        if not os.path.exists(self.image_save_path):
            os.makedirs('/'.join(self.image_save_path.split('/')[:-1]))
        image_data.save(self.image_save_path, 'PNG')
    
    def write(self, input_data, image_ratio=None, verify=None):
        
        if verify is None:
            verify = self.defaults.get('DefaultVerify')
        
        #Convert input to numbers
        encoded_data = self.encode(input_data)
        pixel_data = [ord(letter) for letter in encoded_data] + self.end_of_data
        input_bytes = len(pixel_data)
        pixel_data += [0] * (3 - input_bytes % 3) #Pad to multiple of 3
        required_pixels = len(pixel_data) // 3
        
        #Calculate width and height of image
        if image_ratio is None or not 0 < image_ratio < 1:
            image_ratio = log(1920) / log(1920 * 1080)
        image_width = int(round(pow(required_pixels, image_ratio)))
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
        return 'Saved file: {}'.format(self.image_save_path)
    
    def read(self):
        
        try:
            image_input = Image.open(self.image_save_path)
        except IOError:
            return 'No image file found.'
        
        image_data = UsefulThings.flatten_list(image_input.getdata())
        
        #Truncate end of file
        counter = 0
        end_of_data_len = len(self.end_of_data)
        try:
            for i in range(len(image_data)):
                if image_data[i] == self.end_of_data[counter]:
                    counter += 1
                else:
                    counter = 0
                if counter == end_of_data_len-1:
                    raise SuccessfulTruncate()
        except SuccessfulTruncate:
            image_data = image_data[:2 + i - end_of_data_len]
        else:
            return "Image doesn't contain valid data."
        
        image_data = ''.join(chr(number) for number in image_data)
        
        return self.decode(image_data)
