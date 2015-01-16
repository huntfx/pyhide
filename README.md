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
I've included 2 image files in the folder, "Hamlet.png" and "PiToOneMillion.png", so you can try out the code.

v2.2:
Added in support to store files within the image. It's like a different version of EXIF data I guess.

v3:
Rewrote the code again to give the ability to use custom images.
By default this initial image will be uploaded and URL stored in the file, so it can be read without any extra user input.

Custom images will take longer, as it'll decide the best and most efficient way to store the data.
It will cache a small amount of information about an image after the first run, which on a 1080p image for example, equates to 50 million less calculations, or 9 billion fewer list lookups, so makes things quite a bit faster.

The incorrect padding error should also be fully fixed now, and trying to store more data than an image can handle will revert to the basic method, but keep the same aspect ratio of the custom image.

<br>

<h4>Installation:</h4>
Copy all files (aside from the older versions folder) into 'C:/Users/(name)/Documents/maya/(mayaversion)/scripts'.
use 'from ImageStore import ImageStore' to import the module.

<h4>Config:</h4>

Load up ImageStore.py and you can change the default save location of files. Normally, the image gets saved to My Documents, and the cache file to the python folder.

<br>

<h4>Usage:</h4>

    #import module
    from ImageStore import ImageStore

    #Store data
    ImageStore().write( infoToStore )
     - Return [location, (url if uploaded)]

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
     
<br>

<h4>All Commands:</h4>


    class ImageStore( imageName ):
    
        imageName
         - the name to save the image as, which may include the location
            Default: "C:/Users/Name/Documents/ImageDataStore.png"
    
        def write( input, **kwargs ):
       
            input
             - any data to store in the image
    
            Kwargs:
    
                i/c/image/customImage
                 - String
                 - Path or URL to an image to store data in a copy.
                    Default: None
    
                uI/uploadOriginal/uploadCustomImage
                 - True/False
                 - Upload the original image to imgur and store URL in the file.
                 - Setting to false will require a path or URL for the original image to be provided each time the image is read.
                    Default: True
    
                u/upload/uploadImage
                 - True/False
                 - Upload the image to imgur after creation.
                    Default: False
               
                o/open/openImage
                 - True/False
                 - Open the image in a browser.
                    Default: True
    
                r/ratio/sizeRatio
                 - Float (0-1)
                 - Set the ratio of width to height.
                 - If a custom image is provided but is too small to store the data, the ratio will switch to that of the image.
                    Default: 0.52 (similar to 16:9 resolutions)
    
                d/disable/disableInformation
                 - True/False
                 - Disable output of extra information such as time created, username and version number.
                 - This information is still written to the image, but will not be shown if the outputInformation command is given.
                    Default: False
    
                INI/cache/writeINI/writeCache
                 - True/False
                 - Store some calculated information to a cache file, which can dramatically improve loading times.
                 - It runs on the hash of an image and takes up barely any space, so it's worthwile keeping activated.
                    Default: True
    
    
                #DEBUGGING
    
                debug/debugResult/debugOutput
                 - True/False
                 - Will set all stored information to white, and all other information to black.
                 - There is something wrong is everything is white.
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
                Return [Path to image, (image url if uploaded) ]
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
    
                o/output/outputInformation
                 - True/False
                 - Print stored information within the file if it exists. If disableInfo was set to True, nothing will be shown.
    
    
            If image was read:
                Return <stored data>
            If error in reading image:
                Return None

<br>

<h4>Known Issues:</h4>

Using backslashes in the filepath will convert the characters and change the path.
There may be a noticeable line if the input data is finished before the image ends. I tried to reduce this by adding random data but it's still far from perfect.
The cache may not stop a large custom image being uploaded each time. It works on a hash, which will be different from the original image if it's resized by imgur.

<br>

<h4>Compatibility:</h4>

No versions are compatible with each other due to full rewrites of the code.

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
