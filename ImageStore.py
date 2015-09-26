from __future__ import division
from collections import defaultdict
from math import log
import os
import random
import cPickle
import StringIO
import urllib2
import webbrowser
import zlib
import UsefulThings
reload(UsefulThings)

try:
    from PIL import Image
except ImportError:
    raise ImportError('python imaging library module was not found')
    
#Import internet bits, stop upload features if any don't exist
global override_upload
override_upload = False
try:
    import pyimgur
    import requests
except ImportError:
    output_text = ['Warning: Error importing pyimgur', 
                   ', disabling the upload features.']
    try:
        import requests
    except ImportError:
        output_text = output_text[0] + [' and requests'] + output_text[1]
    print ''.join(output_text)
    override_upload = True
#Disable requests from printing everything
try:
    requests
except NameError:
    pass
else:
    import logging
    logging.getLogger('requests').setLevel(logging.WARNING)


class ISGlobals(object):
    """Class for determining default values, where it will read any 
    changes from a config file.
    
    There are three different groups of variables:
        Required (shown but are reset if edited) - This would mainly be
            for things to show the user, such as comments. If any 
            variables are like this, there is no point adding them to 
            the config file.
            
        Default (shown and can be edited) - These are the core variables
            used in the code. Things the user would normally pass in 
            through the function, but it allows them to set the default 
            values without needing to pass them into the class each time.
            
        Hidden (not shown but can be edited) - These are the less 
            important variables, which aren't normally needed. Things 
            such as overrides should go here, which can be used if a 
            program uses this code and needs to force a few things to 
            happen.
    
    By default, the config file is stored in appdata, though this has
    only been tested on Windows.
    """
    
    #Build list of default values
    link_dict = {}
    link_dict['%USERDIR'] = os.path.expanduser( "~" ).replace( "\\", "/" )
    link_dict['%PYTHONDIR'] = os.getcwd().replace( "\\", "/" )
    link_dict['%APPDATA'] = os.getenv('APPDATA')
        
    location = '%APPDATA/VFXConfig.ini'
    
    for k in link_dict:
        location = location.replace(k, link_dict[k])
    
    def __init__(self, save_all_config_values=False):
        """Define the default values, then check them against the 
        values stored in the config.
        """
        
        reset_config = False
        
        
        required_globals = defaultdict(dict)
        default_globals = defaultdict(dict)
        hidden_globals = defaultdict(dict)
        rg = required_globals['ImageStore']
        dg = default_globals['ImageStore']
        hg = hidden_globals['ImageStore']
        
        rg['!UsableDirectoryLinks'] = ('%PYTHONDIR, %USERDIR, %APPDATA')
        dg['ShowAllValuesHereOnNextRun'] = False
        dg['DefaultImageName'] = 'ImageDataStore.png'
        dg['DefaultImageDirectory'] = '%USERDIR/ImageStore'
        dg['DefaultCustomImage'] = 'http://bit.ly/1G3u3cV'
        dg['UseDefaultCustomImageIfNone'] = False
        dg['DefaultShouldVerify'] = True
        dg['DefaultShouldSave'] = True
        dg['DefaultShouldUpload'] = False
        dg['DefaultShouldOpenOnUpload'] = False
        hg['ForceDefaultVerify'] = False
        hg['ForceNoSave'] = False
        hg['ForceNoUpload'] = False
        hg['ForceNoOpenOnUpload'] = False
        hg['ForceDefaultCustomImage'] = False
        
        #Not yet implemented:
        hg['CacheName'] = 'ImageStore.cache'
        hg['CacheDirectory'] = '%APPDATA/ImageStore'
        
        required_globals = dict(required_globals)
        default_globals = dict(default_globals)
        hidden_globals = dict(hidden_globals)
        
        required_globals = UsefulThings.read_config(self.location, 
                                config_sections=required_globals, 
                                write_values=True, 
                                update_values=True)
        default_globals = UsefulThings.read_config(self.location, 
                                config_sections=default_globals, 
                                write_values=True, 
                                update_values=reset_config)
        hidden_globals = UsefulThings.read_config(self.location, 
                                config_sections=hidden_globals, 
                                write_values=save_all_config_values, 
                                update_values=reset_config)
        
        all_globals = dict(default_globals).copy()
        all_globals['ImageStore'].update(hidden_globals['ImageStore'])
        self.global_dict = UsefulThings.read_config(self.location, 
                                    config_sections=all_globals, 
                                    write_values=False, 
                                    update_values=False)['ImageStore']
        
        self.global_dict = {k: v for k, v in self.global_dict.iteritems() 
                            if k[0] not in ('!', ';')}
        
        #Convert links to the correct format
        for i in self.link_dict:
            self.global_dict = {k: (v.replace(i, self.link_dict[i]) if 
                                    isinstance(v, str) else v) 
                                for k, v in self.global_dict.iteritems()}
        
        if not save_all_config_values and \
            self.global_dict['ShowAllValuesHereOnNextRun']:
            ISGlobals(True)
    
    def get(self, x):
        """Get one of the stored values.
        This should be used after assigning ISGlobals to a variable, 
        so that it doesn't rebuild the list each time a new variable is
        looked up.
        """
        return self.global_dict[x]

class ImageStoreError(Exception):
    pass

class ImageStore(object):
    """Class for writing and reading data in the actual pixels in an 
    image.
    
    Header Information:
        To mark the bits used and end of file, a header is stored at the 
        beginning of the image. 
        The first byte of the image (red value of the pixel), is used as
        an integer that stores two values. The last number determins how
        many bits are used per pixel, and the first two numbers 
        determine how many bytes are being used to store the number of 
        bytes of data being held in the image.
        
        The second part is what was just mentioned above, where the 
        number of bytes is converted to binary and joined, then split 
        into single bytes to allow it to be written to the image. To 
        avoid a noticeable line of pixels in the top corner, this is 
        encoded with the rest of the image. This means if the bits per 
        pixel value is below 8, the image must be decoded before this 
        information can be read.
        
        For example, if the number was 123, the image would be storing 3
        bits per colour, and the next 12 bytes would contain the length 
        of data. Once the image is read and original data pieced back 
        together, bytes at the index of [1:14] will store how many bytes 
        the data is. The data will then be found at [14:14+length].
        
        As to a practical example, if the number was 48, and the next 4 
        bytes were [39, 29, 177, 252], the number of bytes would be 
        656257532, and the data would be at image_data[6:656257538].
        
        The absolute maximum data size through using this method is 
        2.6*10^239 bytes, which is more than the number of atoms in the
        universe, so I think it's safe to say nobody will go above it.
    """
    max_data_len = int('1'*8*99, 2)
    
    def __init__(self, image_path=None, allow_print=True):
        """Format the image path ready to either read or write.
        
        Note that there are no checks on the directory or file, since 
        you do not need a writeable image for ImageStore.read(), and 
        the image/path doesn't need to exist for ImageStore.write().
        
        Parameters:
            image_path (str or None): Path to the image.
                There are basically three different options. If a full
                path is given, this will be used. If part of a path or
                just a filename is given, the default path will be used
                with the input added onto the end. If nothing is given,
                the default path and filename will be used.
            
            allow_print (bool): If printing the current progress of the
                code execution is allowed.
        """
        self.defaults = ISGlobals().get
        
        self.allow_print = allow_print
        
        #Get a valid image path based on the input
        self.image_path = image_path
        if image_path is None:
            self.image_path = '{}/{}'.format(
                                        self.defaults('DefaultImageDirectory'), 
                                        self.defaults('DefaultImageName')
                                      )
        else:
            if ':/' not in image_path:
                if image_path.startswith('/'):
                    image_path = image_path[1:]
                self.image_path = '{}/'.format(
                                        self.defaults('DefaultImageDirectory')
                                        ) + image_path
        
        #Format the extension
        self.image_original_extension = None
        ip = self.image_path
        ip_split = ip.split('/')
        if '.' in ip_split[-1]:
            self.image_original_extension = ip_split[-1].split('.')[-1]
            ip = (ip[::-1].split('.', 1)[1])[::-1]
        ip += '.png'
        self.path = ip
    
    def encode(self, data, b64=False):
        """Encode the image data from the raw input into something that
        can be converted into bytes.
        
        Parameters:
            data (any): Input to encode.
                Can be in any format, as long as it can be pickled.
        """
        data = zlib.compress(cPickle.dumps(data))
        if b64:
            data = base64.b64encode(data)
        return data
    
    def decode(self, data, b64=False):
        """Decode the image data.
        
        Parameters:
            data (str): Output from ImageStore.encode().
        """
        try:
            if b64:
                data = base64.b64decode(data)
            data = cPickle.loads(zlib.decompress(data))
            return data
        except (TypeError, cPickle.UnpicklingError, zlib.error):
            raise ImageStoreError('failed to decode image data')
    
    def _validate_client(self, client):
        """Validate the client manually since pyimgur only gives a
        generic 'Exception' if it is invalid.
        """
        if isinstance(client, pyimgur.Imgur):
            try:
                return all((client.client_secret is not None,
                            client.refresh_token is not None))
            except AttributeError:
                pass
        return False
        
    def _choose_client(self, imgur_auth):
        """Validate the input client or return the default one."""
        
        used_auth = 'None'
        if isinstance(imgur_auth, pyimgur.Imgur):
            
            try:
                #Decode client from input string
                client = self.decode(imgur_auth, b64=True)
                
                if not self._validate_client(client):
                    raise ImageStoreError()
                used_auth = 'Decoded input'
                            
            except (ImageStoreError, AttributeError):
                
                #Use raw input as client                        
                if self._validate_client(imgur_auth):
                
                    encoded_client = self.encode(imgur_auth, b64=True)
                    
                    self._print('Your encoded client string is as follows. '
                                'Use this for imgur_auth to bypass the login.')
                    self._print(encoded_client)
                    
                    #Write to config
                    config_write = defaultdict(dict)
                    config_write['ImageStore'] = {'LastImgurClient': 
                                                  encoded_client}
                    UsefulThings.read_config(ISGlobals.location, 
                                             config_write, 
                                             write_values=True, 
                                             update_values=True)
                    used_auth = 'Input'
                    
                else:
                    
                    #Move onto next part instead
                    imgur_auth = None
                                             
        if not isinstance(imgur_auth, pyimgur.Imgur):
            
            try:
                #Read config for last client
                encoded_client = UsefulThings.read_config(ISGlobals.location)
                encoded_client = encoded_client['ImageStore']['LastImgurClient']
                client = self.decode(''.join(encoded_client), b64=True)
                
                if not self._validate_client(client):
                    raise ImageStoreError()
                used_auth = 'Previously cached client'
                
                
            except (KeyError, ImageStoreError):
                
                #Use default client
                encoded_client = ['eJxtkEtPwzAQhO/+I+0JZf1YO0ckQIpUuL',
                                  'T0GvmxaS2aEMUpUv89diooIC6RNd9kRrPr',
                                  'OF5ifzhPrFm+I7B1GDnbriY70yn2cW7Pia',
                                  'bltWKjYC9pu4qptef5SMMcfbaFDCRrqopl',
                                  '9kFT7C5ZUVmBovxOmihRScIl6cb8Kea8rx',
                                  '79h17/7G0c4nDI3Czcek8ptfP7Gw1ZrNne',
                                  'E1i0VPNaO+ODANTKmBpk6IKiTiqP6I3SeW',
                                  'jF/un/2QGwlFxBG8tKKJepAlTGcOs6xEC+',
                                  'yILdjIn8tCwEmc0KpVaA2awrbSU3ngunlH',
                                  'GBG8EtOVVbAKuLX5WUh8en+9fNrt00z82u',
                                  'qMgauJ52oi5f7/i9FzTbIxqBXAXnuDAOrN',
                                  'R5MrigKutqcMgJbfCCZ7dhyd19ArUPmi4=']
                client = self.decode(''.join(encoded_client), b64=True)
                used_auth = 'Default client'
        
        self._print('Imgur authentication being used: {}'.format(used_auth))
        return client
                                                                
                                                                
    def _save_image(self, image_data):
        """Wrapper for saving the image.
        If the file path doesn't exist, it will be created, then the
        image is saved.
        """
        if UsefulThings.make_file_path(self.path):
            try:
                image_data.save(self.path, 'PNG')
            except IOError:
                raise IOError('unable to write image')
        else:
            raise IOError('unable to write image path')
    
    
    def _read_image(self, image_location, require_png=False): 
        """Wrapper for opening the image, supports opening from a URL as
        well as normal files.
        
        Parameters:
            image_location (str): Path to image.
            
            require_png (bool): If the image must be a PNG.
                If True and image isn't a PNG, it will throw an error.
        """
        #Load from URL
        if any(value in image_location for value in ('http://', 
                                                     'https://', 
                                                     'ftp://')):
            try:
                image_location = StringIO.StringIO(urllib2.urlopen(
                                                   image_location).read())
            except urllib2.URLError:
                raise urllib2.URLError('failed to load image from URL')
                
        #Open image
        try:
            return Image.open(image_location).convert('RGB')
        except IOError:
            if require_png:
                if self.image_original_extension is not None and \
                    'png' not in self.image_original_extension and \
                    'png' in image_location:
                    try:
                        Image.open(image_location.replace('png', 
                                                self.image_original_extension))
                        raise ImageStoreError('image format needs to be PNG')
                    except IOError:
                       pass
                raise IOError('no image file found')
            raise IOError('failed to open image file')
    
    def _print(self, item, indent=' '):
        """Print wrapper to allow disabling all messages."""
        if self.allow_print:
            print '{}{}'.format(indent, item)
    
    def _time(self, verb, TimeThisObject):
        """"Wrapper for formatting the time correctly.
        Allows the format to be easily edited without having to change
        each string.
        """
        self._print('{}: {}'.format(TimeThisObject.output(), verb), ' ')
    
    def write(self, input_data, custom_image=None, image_ratio=None, 
              verify=None, save_image=None, upload_image=None, 
              open_on_upload=None, imgur_title=None, imgur_description=None, 
              imgur_auth=None):
        """Write data to an image.
        
        If a custom image is used, bits per byte is calculated, which 
        determins how many bits are used to store data in each colour 
        value in the image. This can range from 1, which is virtually 
        invisible to the human eye, to 8, which would entirely erase the
        original image. 
        The input image is processed to remove the last few bits from
        each colour, and is padded back to 8 bits using the input data.
        
        Parameters:
            input_data (any): Data to be written to the image.
                May be in almost any format as it is pickled.
            
            custom_image (str or None, optional): Path or URL to an 
                image to write over. 
                Since the output has to be a PNG, a large custom image
                will result in a large file size, no matter what the
                input data is.
                Leave as None to write the smallest image possible, or
                use the default custom image depending on the config.
            
            image_ratio (str or None, optional): Set the width to height
                ratio if there is no custom image, in the format 'w:h'.
                If a custom image is given, but the data turns out too
                large to store in it, although it'll scrap the custom
                image and act like one wasn't provided, it will inherit
                the ratio from that image.
                Will default to a 16:9 resolution if left as None.
                
            verify (bool or None, optional): Read the image after 
                creation to make sure the read data matches the original
                input data.
                Will check the file and/or URL depending on where the
                image was saved.
                Disabling it will not have any adverse effects, since
                the code should catch most problems during writing.
                If None, it will use the default value provided in the 
                config.
            
            save_image (bool or None, optional): If the file should be 
                saved to disk.
                If None, it will use the default value provided in the 
                config.
            
            upload_image (bool or None, optional): If the file should be
                uploaded to imgur.
                If None, it will use the default value provided in the 
                config.
                
            open_on_upload (bool or None, optional): If the uploaded 
                link should be opened by the default web browser.
                If None, it will use the default value provided in the 
                config.
                
            imgur_title (str or None, optional): Title to give to the 
                Imgur upload.
                
            imgur_description (str or None, optional): Description to 
                give to the Imgur upload.
            
            imgur_auth (class, str or None, optional): Used to upload 
                images to the account of the authenticated user.
                Use imgur_log_in() to get the pyimgur instance for this, 
                and after code execution, a string will be provided to
                use here for the purpose of not having to authenticate 
                again.
        """
        #Get default values from config
        if verify is None or self.defaults('ForceDefaultVerify'):
            verify = self.defaults('DefaultShouldVerify')
        if self.defaults('ForceNoSave'):
            save_image = False
        elif save_image is None:
            save_image = self.defaults('DefaultShouldSave')
        if override_upload or self.defaults('ForceNoUpload'):
            upload_image = False
        else:
            if upload_image is None:
                upload_image = self.defaults('DefaultShouldUpload')
            if self.defaults('ForceNoOpenOnUpload'):
                open_on_upload = False
            elif open_on_upload is None:
                open_on_upload = self.defaults('DefaultShouldOpenOnUpload')
        
        bits_per_byte = 8
        
        self._print('Writing to image...', '')
        with UsefulThings.TimeThis(print_time=self.allow_print) as t:            
                        
            encoded_data = [ord(letter) for letter in self.encode(input_data)]
            self._time('Encoded data', t)
            
            #Build header info
            num_bytes = len(encoded_data)
            if num_bytes > self.max_data_len:
                message = 'well done for breaking the laws of physics'
                raise ImageStoreError(message)
            nb_binary = str(bin(num_bytes))[2:]
            nb_length = len(nb_binary)
            nb_integer_parts = nb_length // 8 + (1 if nb_length % 8 else 0)
            nb_total_length = nb_integer_parts * 8
            nb_new = [nb_binary.zfill(nb_total_length)[i:i+8] 
                      for i in range(0, nb_total_length, 8)]
            pixel_data = [int(i, 2) for i in nb_new] + encoded_data
            
            self._time('Calculated header', t)
            
            #Try read custom image from config if none has been given
            if (custom_image is None and \
                self.defaults('UseDefaultCustomImageIfNone')
                ) or self.defaults('ForceDefaultCustomImage'):
                
                try:
                    self._read_image(self.defaults('DefaultCustomImage'))
                    custom_image = self.defaults('DefaultCustomImage')
                except (IOError, urllib2.URLError):
                    pass
            
            if custom_image is not None:
                
                #Read and process custom image
                custom_image_input = self._read_image(custom_image)
                image_width, image_height = custom_image_input.size
                max_image_bytes = image_width * image_height
                
                self._time('Read custom image', t)
                
                #Calculate required bits per byte
                total_data_bytes = len(pixel_data) + 1
                
                self._print('Image resolution: {}x{} ({} pixels)'.format(
                               image_width, image_height, max_image_bytes))
                self._print('Input data: {} bytes'.format(total_data_bytes))
                bits_per_byte = 1
                self._print(('Checking the smallest possible '
                            'bits per byte to use...'))
                
                while bits_per_byte < 9:
                    storage_needed = total_data_bytes * (8 / (bits_per_byte))
                    self._print(" {}: Up to {} bytes".format(bits_per_byte, 
                                                    int(round(storage_needed))))
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
                    joined_binary_data = ''.join(str(bin(x))[2:].zfill(8) 
                                                 for x in pixel_data)
                    #Pad the end a little to stop an unusual error
                    joined_binary_data += '0' * bits_per_byte
                            
                    split_binary_data = UsefulThings.split_list(
                                                joined_binary_data, 
                                                bits_per_byte)
                            
                    num_pixels_needed = len(split_binary_data)
                    
                    split_image_data = UsefulThings.flatten_list(
                                                custom_image_input.getdata())
                    
                    self._time('Processed input data and image', t)
                    
                    reduced_image = [str(bin(i))[2:].zfill(8)[:-bits_per_byte] 
                                     for i in split_image_data]
                    self._time('Reduced bits of custom image', t)
                    
                    #Duplicate split_binary_data until it is long enough
                    #Faster overall compared to picking random values
                    extra_length_needed = (len(split_image_data) - 
                                           len(split_binary_data))
                                           
                    while len(split_binary_data) < extra_length_needed:
                        split_binary_data *= 2
                    
                    pixel_data = [int(reduced_image[i] + split_binary_data[i-1],
                                  2) for i in range(len(reduced_image))]
                    
                    self._time('Merged input data with custom image', t)
                
                else:
                    self._print('Data does not fit in image, '
                                'reverting to normal method...', '')
                
            if custom_image is None:
                
                #Convert input to numbers
                pixel_data = [0] + pixel_data
                input_bytes = len(pixel_data)
                pixel_data += [0] * (3 - input_bytes % 3) #Pad to multiple of 3
                total_bytes = len(pixel_data) // 3
                required_pixels = int(total_bytes * 8 / bits_per_byte)
                
                #Calculate width and height of image
                if ':' in str(image_ratio):
                    image_ratio_split = [max(1, float(i)) 
                                         for i in image_ratio.split(':')]
                    
                else:
                    image_ratio_split = [16, 9]
                    
                x = pow(required_pixels * image_ratio_split[0] * 
                        image_ratio_split[1], 0.5)
                
                #Don't let any dimensions go over the number of bytes
                image_width = max(1, min(required_pixels, 
                                         int(round(x/image_ratio_split[1]))))
                image_width //= 3
                image_width *= 3
                image_height = required_pixels / image_width
                
                #Round height up if left as a decimal
                if float(image_height) != float(int(image_height)):
                    image_height += 1
                image_height = int(image_height)
                image_dimensions = image_width * image_height
                
                self._time('Calculated image size', t)
                
                remaining_pixels = image_dimensions - required_pixels
                pixel_data += [random.choice(pixel_data) 
                               for i in range(3 * remaining_pixels)]
                self._time('Padded data', t)
            
            #Write first byte as header
            initial_header = int(str(nb_integer_parts) + str(bits_per_byte))
            pixel_data[0] = initial_header
            
            #Draw image
            image_output = Image.new('RGB', (image_width, image_height))
            image_data = image_output.load()
            
            #Assign pixels
            for y in range(image_height):
                for x in range(image_width):
                    cp = 3 * (x + y * image_width)
                    image_data[x, y] = tuple(pixel_data[cp:cp + 3])
            
            self._time('Created image', t)
                                        
                
            #Build StringIO file
            output_StringIO = StringIO.StringIO()
            image_output.save(output_StringIO, 'PNG')
            contents = output_StringIO.getvalue()
            output_StringIO.close()
                
            if upload_image:
                
                client = self._choose_client(imgur_auth)
                           
                #Renew the token
                if self._validate_client(client):
                    client.refresh_access_token()
                                
                                
                #Send upload request since pyimgur doesn't support StringIO
                image_upload = client._send_request(
                                            'https://api.imgur.com/3/image', 
                                            method='POST', 
                                            params={
                                           'image': contents.encode('base64'), 
                                           'title': imgur_title, 
                                           'description': imgur_description
                                            })
                uploaded_image_type = image_upload['type'].split('/')[1]
                uploaded_image_size = image_upload['size']
                uploaded_image_link = image_upload['link']
                uploaded_image_id = image_upload['id']
                uploaded_image_delete_link = image_upload['deletehash']
                
                self._time('Uploaded image', t)
                
                #Detect if image has uploaded correctly, delete if not
                if uploaded_image_type.lower() == 'png' and \
                    uploaded_image_size == len(contents):
                    
                    i_link = 'Link to image: {}'
                    i_delete = 'Link to delete image: {}/{}'
                    self._print(i_link.format(uploaded_image_link), '  ')
                    self._print(i_delete.format('http://imgur.com/delete',
                                              uploaded_image_delete_link), '  ')
                    
                    if open_on_upload:
                        webbrowser.open(uploaded_image_link)
                else:
                    output = 'Image failed to upload correctly - '
                    self._print('Image failed to upload correctly.')
                    if uploaded_image_type.lower() != 'png':
                        output += 'file was too large.'
                    else:
                        output += 'unknown reason'
                    upload_image = False
                    pyimgur.Image(image_upload, client).delete()
                
                
            #Save image
            if save_image:
                self._save_image(image_output)
                self._time('Saved file', t)
                self._print('Path to file: {}'.format(self.path), '  ')
                
                
            #Validate the image
            if save_image or upload_image:
                if verify:
                    read_save_image = input_data
                    read_upload_image = input_data
                    if save_image:
                        read_save_image = ImageStore(self.path, 
                                                     allow_print=False).read()
                    if upload_image:
                        read_upload_image = ImageStore(uploaded_image_link, 
                                                       allow_print=False).read()
                    
                    if read_save_image != read_upload_image or \
                        read_save_image != input_data:
                        raise ImageStoreError('image failed validation')
                    self._time('Verified file', t)
                
                output_path = {'size': len(contents)}
                
                if save_image:
                    output_path['path'] = self.path
                
                if upload_image:
                    output_path['url'] = '{}.{}'.format(uploaded_image_id, 
                                                        uploaded_image_type)
                    output_path['url_delete'] = uploaded_image_delete_link
                    
                return output_path
    
    def read(self):
        """Attempt to read the stored data from an image.
        
        To undo the write process, if a custom image is used, each 
        colour must be broken down into bits and the last few bits are 
        taken then pieced together. If these are split into groups of 8
        and converted back to characters, it results in the original 
        encoded string.
        """
        
        self._print('Reading image...', '')
        with UsefulThings.TimeThis(print_time=self.allow_print) as t:
            
            image_input = self._read_image(self.path, 
                                           require_png=True)
            
            self._time('Read image', t)
            
            #Get data and header
            image_data = UsefulThings.flatten_list(image_input.getdata())
            image_header = str(image_data[0])
            bytes_per_pixel = int(image_header[-1])
            nb_parts = int(image_header[:-1])
            image_data = image_data[1:]
            self._time('Processed image', t)
            
            #Get the required pixels as binary, piece together, and
            # convert back to int
            if bytes_per_pixel != 8:
                
                image_data_parts = [str(bin(i))[2:].zfill(8)[8-bytes_per_pixel:]
                                    for i in image_data]
                image_data_binary = ''.join(image_data_parts)
                image_data_split = UsefulThings.split_list(image_data_binary, 8)
                num_bytes = int(''.join(image_data_split[:nb_parts]), 2)
                truncated_data = [int(i, 2) for i in 
                    image_data_split[nb_parts:num_bytes + nb_parts]]
            
            else:
                #Does same as above, but avoids converting the entire 
                # data to binary to save time
                nb_raw = image_data[:nb_parts]
                nb_binary = ''.join(str(bin(i))[2:].zfill(8) 
                    for i in nb_raw)
                num_bytes = int(nb_binary, 2)
                truncated_data = image_data[nb_parts:num_bytes + nb_parts]
            
            self._time('Got required data', t)
            
            decoded_data = self.decode(''.join(chr(number) 
                                       for number in truncated_data))
            
            self._time('Decoded data', t)
            
            return decoded_data
            
def imgur_log_in():
    client = pyimgur.Imgur('0d10882abf66dec', 
                           '5647516abf707a428c23b558bd2832aeb59a11a7')
    auth_url = client.authorization_url('pin')
    webbrowser.open(auth_url)
    pin = raw_input('Please enter the pin number shown... ')
    print pin
    try:
        client.exchange_pin(pin)
    except requests.HTTPError:
        print 'Error: Invalid pin number'
        return None
    return client


log_in = True
if __name__ == '__main__':
    try:
        client.refresh_access_token()
    except (NameError, AttributeError):
        client = None
    if log_in:
        if not client:
            client = imgur_log_in()
