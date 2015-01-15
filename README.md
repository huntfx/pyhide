# ImageStore

Use this to store or read information within images. It will keep the format of whatever you put in,
so even lists and dictionaries are compatible.

By default the image is saved to the Maya directory, but a different location can be set. It should
support being uploaded assuming the image is left untouched and not converted to a different format.

Currently the images are dull, so in the future I'll try add in a feature where you can use a custom
image, and it'll write the information over it.

<br>


<h4>Installation:</h4>
Copy the imageStore.py file and PIL folder into 'C:/Users/(name)/Documents/maya/(mayaversion)/scripts'

<br>

<h4>Usage:</h4>

    #import module
    from imageStore import ImageStore

    #store data
    ImageStore().write( infoToStore )

    #retrieve data
    ImageStore().read()


<br>

<h4>Advanced:</h4>

    #Save to the D drive
    ImageStore( "D:/" ).write( infoToStore )

    #Save to the D drive and give a name
    ImageStore( "D:/My Information" ).write( infoToStore )
