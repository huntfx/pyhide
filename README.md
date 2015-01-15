# ImageStore


Use this to store or read information within images. It will keep the format of whatever you put in, so even lists and dictionaries are compatible.

By default the image is saved to your My Documents folder, but a different location can be set. It can be uploaded anywhere and read from other computers as long as it stays as a PNG file.

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
Added in support to store files within the image. Obviously it's cheating if I was to store the actual data, so currently it's just various bits such as the version number and time created. Eventually it'll store the URL to an original image once I provide the option to use custom images.

v3 (in progress):
Ability to use custom images

<br>

<h4>Installation:</h4>
Copy all files (aside from the older versions folder) into 'C:/Users/(name)/Documents/maya/(mayaversion)/scripts'.
use 'from ImageStore import ImageStore' to import the module.

<br>

<h4>Usage:</h4>

    #import module
    from ImageStore import ImageStore

    #Store data
    ImageStore().write( infoToStore )
     - Return [location, (url if uploaded)]

    #Retrieve data
    ImageStore().read()
     - Return the stored data



<br>

<h4>Advanced:</h4>


    #Save to the D drive
    ImageStore( "D:/" ).write( infoToStore )

    #Save to the D drive and give a name
    ImageStore( "D:/My Information" ).write( infoToStore )

    #Upload image
    ImageStore().write( infoToStore, upload = True, open = True )
     - Upload is false by default, setting it to true will upload the image and return the URL.
     - Open is true by default, which will load the uploaded image in a browser.

    #Read uploaded image
    ImageStore( "http://imgur.com/image.png" ).read()

    #Change padding
    ImageStore().write( infoToStore, padding = 15 )
     - 10 by default, used to add extra height to the image so the data doesn't get truncated.
     - Ideally needs to be as low as possible, but will usually say "Incorrect padding" if it's too low and the image is read.
     - Make sure you try read each image after creating it, as it is sometimes a bit hit and miss.
     
<br>

<h4>Other:</h4>


    #Hide creation details
    ImageStore().write( infoToStore, disableInfo = True )
     - Will stop any information being printed from inside the file when it is read.
     - Currently includes version number, computer account name, and time created.


    #Output creation details
    ImageStore().read( output = True )
     - Print the creation details from the file if they exist
     - False by default


    #Change image imensions
    ImageStore().write( infoToStore, ratio = 0.5 )
     - Change ratio of width to height. It is 0.52 by default as that is close to 16:9 resolutions.
     - A value of 0.5 will attempt to give a square image.

<br>

<h4>Bugs:</h4>

Using backslashes in the filepath can convert the characters and change the path.

<br>

<h4>Compatibility:</h4>

v0.1 and v0.2 are not compatible due to being totally rewritten.

<br>

<h4>License:</h4>

You may use my code without permission as long as my name and website are left at the top of the file, although it'd be cool if you told me you were using it.
