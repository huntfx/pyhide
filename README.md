# ImageStore


Use this to store or read information within images. It will keep the format of whatever you put in, so even lists and dictionaries are compatible.
It can be uploaded anywhere and read from other computers as long as it stays as a PNG file.

<br>

<h4>Updates:</h4>

v1:
Manually wrote all the parts aside from the image library. Amazingly slow with any large amounts of data.

v2:
Entirely rewrote to use built in functions for a lot of the conversion. Very lightweight and relatively fast.

v2.1
Added support for imgur, so you may set the code to upload the image, or read any image but putting the URL as the file path.

v2.2:
Added in support to store files within the image, in preperation for custom images. 

v3:
Rewrote the code again to give the ability to use custom images. 
By default this initial image will be uploaded and URL stored in the file, so it can be read without any extra user input.

Custom images will take longer, as it'll decide the best and most efficient way to store the data.
It will cache a small amount of information about an image after the first run, which on a 1080p image for example, equates to 50 million less calculations, or 9 billion fewer list lookups, so makes things quite a bit faster.
The incorrect padding error should also be fully fixed now, and trying to store more data than an image can handle will revert to the basic method, but keep the same aspect ratio of the custom image.

v3.1
Input data is now compressed, and progress is output every few seconds as calculations can take a while.
Added more cutoff modes, the option to use multiple cutoff modes, and another value that can be set to true to automatically use them all.
The cache is now fixed to store each cutoff mode separately, instead of just the first one.

v3.1.1
Wrote some code to track stats, and cleaned up a lot of the URL checking.
Added in debugging for reading images, it can display the first x decoded characters (any amount but 100 by default) and various other information about the image.
If pyimgur or requests are not found, instead of throwing an error, it will just disable the upload capabilities and continue as normal.

v3.1.2
Made it a lot easier to force default values, which could be useful in an application.
Putting a URL as the save path will attempt to use it as a custom image instead of throwing an error, and the cache function can return the hash of an image, to make it easier to locate in the cache.
Fixed various other bugs such as black and white images crashing the code.

<br>

<h4>Installation:</h4>
Copy ImageStore.py with the PIL, requests and pyimgur folders into your Python directory.<br>
Alternatively, you may add a new search path to any location through the following method, but it must be run each time Python is loaded.

	import sys
	sys.path.append( path to folder )
	
use `from ImageStore import ImageStore` to import the module.

<br>

<h4>Config:</h4>

Load up imageStore.py and you can change the default save location of files and a few other things. Normally, the image gets saved to My Documents, and the cache file to the python folder.

<br>

<h4>Usage:</h4>

    #import module
    from ImageStore import ImageStore

	#Store data
	ImageStore().write( infoToStore )
	 - Return [[location, (url if uploaded)]]

	#Store data in a custom image
	ImageStore().write( infoToStore, customImage = path/url )

	#Retrieve data
	ImageStore().read()
	 - Return the stored data

<br>

<h4>Advanced:</h4>

	#Save to the D drive
	ImageStore( "D:/" ).write( infoToStore )

	#Save to the D drive and call it "My Information.png" (the extension is optional)
	ImageStore( "D:/My Information" ).write( infoToStore )

	#Upload image
	ImageStore().write( infoToStore, upload = True, open = True )
	 - Upload is false by default, setting it to true will upload the image and return the URL.
	 - Open is true by default, which will load the uploaded image in a browser.

	#Read uploaded image
	ImageStore( "http://imgur.com/image.png" ).read()

	#Save the image using a different cutoff mode
	#The value can be given as an integer, list, tuple, or string, and supports multiple values
	ImageStore().write( infoToStore, cutoffMode = 4 )

	#Save 7 versions of the image with all the different cutoff modes (for use if the output image has some banding, another mode may fix it)
	ImageStore().write( infoToStore, allCutoffModes = True )
     
<br>

<h4>All Commands:</h4>

    class ImageStore( imageName, **kwargs ):
    
    	imageName 
    	 - String
    	 - the name to save the image as, which may or may not include the location
    		Default: "C:/Users/Name/Documents/ImageDataStore.png"
    
    	Kwargs:
    		p/print/printProgress
    		 - True/False
    		 - Set to false to disable all messages being printed
    			Default: True
    
    
    	def write( input, **kwargs ):
    	
    		input
    		 - any data to store in the image
    
    		Kwargs:
    
    			i/c/image/customImage
    			 - String
    			 - Path or URL to an image to store data in a copy.
    				Default: None
    
    			u/upload/uploadImage
    			 - True/False 
    			 - Upload the image to imgur after creation.
    				Default: False
    			
    			o/open/openImage
    			 - True/False 
    			 - Open the image in a browser.
    				Default: True
    
    			uI/uploadOriginal/uploadCustomImage
    			 - True/False 
    			 - Upload the original image to imgur and store URL in the file.
    			 - Setting to false will require a path or URL for the original image to be provided each time the image is read.
    				Default: True
    
    			cM/mode/cutoffMode
    			 - Integer/String/Tuple
    			 - Choose a custom cutoff mode to use, supports multiple ones to be input.
    			 - Input may be an integer '4', tuple '(2,4,5)', or string "2,4,5"
    				Default: None
    
    			a/aCM/allCutoffModes
    			 - True/False
    			 - Automatically save the image under all the cutoff modes, the same as writing 0-7 for the above command.
    				Default: False
    
    			r/ratio/sizeRatio
    			 - Float (0-1)
    			 - Set the ratio of width to height.
    			 - If a custom image is provided but is too small to store the data, the ratio will switch to that of the image.
    				Default: 0.52 (similar to 16:9 resolutions)
    
    			revert/revertToDefault
    			 - True/False
    			 - When using a custom image, if it's too small, the code will revert to the default style and disable custom images.
    			 - You can use this to disable this option and return None if the image won't fit in the custom image.
    				Default: True
    
    			d/disable/disableInformation
    			 - True/False 
    			 - Disable output of extra information such as time created, URL and username.
    				Default: False
    
    			cache/writeCache
    			 - True/False
    			 - Store some calculated information to a cache file, which can dramatically improve loading times.
    			 - It runs on the hash of an image and takes up barely any space, so it's worthwile keeping activated.
    				Default: True
    
    			uploadURLsToImgur
    			 - True/False
    			 - Used when uploading custom images is enabled
    			 - By default the code will check if the custom image is a link, and this adds a bit extra to check it's from Imgur.
    			 - If set to True and the image is from elsewhere, it will reupload the image.
    			 - You may want to disable this if you are using an image on your own website, otherwise it's best to keep it enabled to avoid 404 errors.
    				Default: True
    
    			vO/validateOutput
    			 - True/False
    			 - Will read the output image to make sure the data exactly matches the input.
    			 - May slow down execution time if enabled.
    				Default: False
    
    
    			#DEBUGGING
    
    			debug/debugResult/debugOutput
    			 - True/False 
    			 - Will set all stored information to blackand all other information to white
    			 - There should always be mostly white and some black, unless you are storing a very small amount of information.
    				Default: False
    
    			cH/cutoffHelp/cutoffModeHelp
    			 - True/False
    			 - Output all cutoff modes and what they do
    				Default: False
    
    			s/size/returnSize
    			 - True/False 
    			 - Return the input size.
    				Default: False
    
    			returnInfo/getImageInfo
    			 - True/False 
    			 - Return maximum number of bytes the image can hold.
    				Default: False
    
    			t/test/testImage
    			 - String
    			 - Return True/False depending on if custom image can be read from the path/URL.
    				Default: None
    
    
    
    		If image was saved:
    			Return [[Path to image, (image url if uploaded) ], (same if multiple images were created)]
    		If error in saving image:
    			Return None
    
    
    
    	def read( *args, **kwargs ):
    
    		Args:
    			
    			(Path to custom image)
    			 - String
    			 - Use this path instead of stored URL for custom image. Won't work if it's not the exact same as the original image used to store data.
    			 - If the original image was uploaded and imgur resized/resampled it, only the URL will work, unless you saved the image again.
    				Default: None
    		
    		Kwargs:
    		
    			i/image/imagePath/customImage
    			 - String
    			 - Same as the path to custom image in args, this one will be given priority if set.
    				Default: None
    
    			o/output/outputInformation
    			 - True/False
    			 - Print stored information within the file if it exists. If disableInfo was set to True, nothing will be shown.
    				Default: False
    
    
    			#DEBUGGING
    
    			debug/debugResult/debugOutput
    			 - True/False/Integer
    			 - Print various information useful in testing if the correct information is stored.
    			 - By default it will output the stored files, length of data, type of data, and the first 100 characters (set to a number to modify the amount).
    			 - Note that it will still return the stored information, the only difference is it will print more information.
    				Default: False
    
    
    
    		If image was read:
    			Return <stored data>
    		If error in reading image:
    			Return None
    
    
    
    	def cache( **kwargs ):
    
    		Kwargs:
    	
    			c/clean/cleanCache
    			 - True/False
    			 - Delete the cache file.
    				Default: False
    
    			k/key/value
    			 - String (hash of image)
    			 - Return information related to the cached image as a list.
    				Default: None
    
    			delKey/deleteKey
    			 - String (hash of image)
    			 - Attempt to remove information on an individual cached image.
    				Default: None
    			
    			p/path/cachePath
    			 - String
    			 - Return the location where the cache is stored.
    			 - It will still return the location even if no cache file exists.
    				Default: False
    				
    			h/hash/imageHash
    			 - True/None/String
    			 - Return the hash of the image.
    			 - If True is given instead of a location, the image location passed to the main class will be used.
    			 	Default: None
    
    
    		If cache exists:
    			Return <cache dictionary>
    		If error somewhere:
    			Return None

<br>

<h4>Known Issues:</h4>

Using backslashes in the filepath will convert the characters and change the path.
There may be a noticeable line if the input data is finished before the image ends. I tried to reduce this by adding random data but it's still far from perfect.

<br>

<h4>Compatibility:</h4>

No versions before 3.1 are compatible with each other.

<br>

<h4>How It Works:</h4>


The basic idea is to convert the input data into numbers, then use those numbers as colour values for the pixels. A certain combination of numbers is appended to mark the end of the data.

However, with the introduction of custom images, it got a bit more complicated:

  An extra pixel at the start is now dedicated to storting two important pieces of information: bits per colour and the cutoff mode.

  The cutoff mode is how the image stores the data, and is automatically selected based on what has the potential to store most data. For example, a white image will need every pixel being darkened, yet a black image will need every pixel brightened. Alternatively, an image could work better with both.

  Bits per colour is how many bits are dedicated to storing the data. Each colour has 8 bits in total, and each increase doubles the affect on the image. 1 bit per colour only changes 1/255 values, yet 6 bits is 63/255 values, so ideally you want this as low as possible.

  Finding these values is a very resource heavy calculation. By performing 3 calculations on each pixel, it can find the best cutoff mode to use, then a further 8 calculations are done to find the maximum data it can store for 1-8 bits per pixel.
  The results from this can be stored in the cache for faster subsequent runs.

  The input data is then converted into binary, joined together, and split into parts as large as the bits per pixel.
  These values can then be converted back into numbers, to be added or subtracted from the existing pixels, based on the cutoff mode.

Reading the image simply reverses the process, but it requires every pixel to be exactly the same or it won't be able to decode the data.

<br>

<h4>License:</h4>

You may use my code without permission as long as my name and website are left at the top of the file, although it'd be cool if you told me you were using it.
