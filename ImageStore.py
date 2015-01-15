'''
Author: Peter Hunt
Website: peterhuntvfx.co.uk
Version: 0.2
'''
from PIL import Image
from random import randint
import cPickle, base64
import urllib, cStringIO, os, pyimgur, webbrowser
versionNumber = 0.2

#This will let me say when there's updates.
#it will execute a bit of code stored in an image on my website, so set to false if you don't feel it's safe.
loadDataFromPersonalWebsite = True

class ImageStore:

    defaultImageName = "ImageDataStore"
    homeDirectory = os.getcwd()

    def __init__( self, imageName=defaultImageName ):
    
        self.imageDataPadding = [116, 64, 84, 123, 93, 73, 106]
        self.imageName = str( imageName ).replace( "\\", "/" ).rsplit( '.', 1 )[0]
        if self.imageName[-1:] == ":":
            self.imageName += "/"
        if self.imageName[-1:] == "/":
            self.imageName += self.defaultImageName

    def __repr__( self ):
        return "Use this to store or read data from an image.\nUsage:\n - ImageStore().write(input), ImageStore().read()\nYou can also define the name and location of the image.\n - ImageStore( 'C:\Filename' )"
    
    def write( self, input, ratioWidth=0.52, **kwargs ):
        
        try:
            heightPadding = int( kwargs['padding'] )
        except:
            heightPadding = 10
            
        #Get upload info
        try:
            if kwargs['upload'] == True:
                upload = True
            else:
                upload = False
        except:
            upload = False
        try:
            if kwargs['open'] == False:
                openImage = False
            else:
                openImage = True
        except:
            openImage = True
        
        encodedData = base64.b64encode( cPickle.dumps( input ) )
        pixelData = [int( format( ord( letter ) ) ) for letter in encodedData]
        pixelData += self.imageDataPadding
        #Pad to end with multiple of 3
        for i in range( 3-len( pixelData ) ):
            rawData += [255]
        
        #Set image info
        minimumWidth = 16
        minimumHeight = 8
        currentPixels = len( pixelData )/3
        
        #Calculate width and height
        if currentPixels <= minimumWidth*minimumHeight:
            #Set to minimum values
            width = minimumWidth
            height = minimumHeight
        else:
            #Calculate based on ratio
            width = int( round( pow( currentPixels, ratioWidth ), -1 ) )
            #Make sure it is divisible by 3
            width /= 3
            width *= 3
            if width < minimumWidth:
                width = minimumWidth
            height = int( round( pow( width, 1/( 1/( 1-ratioWidth )-1 ) ), 0 ) )+heightPadding
                
        #Draw image
        imageOutput = Image.new("RGB", ( width, height ) )
        imageData = imageOutput.load()
            
        #Assign pixel colours
        for y in range( height ):
            for x in range( width ):
                currentProgress = 3*( y*width+x )
                try:
                    dataR = pixelData[currentProgress+0]
                    dataG = pixelData[currentProgress+1]
                    dataB = pixelData[currentProgress+2]
                except:
                    dataR = randint( 52, 128 )
                    dataG = randint( 52, 128 )
                    dataB = randint( 52, 128 )
                imageData[x,y] = ( dataR, dataG, dataB )
        
        #Save image with some error catching
        if "http://" in self.imageName:
            print "Can't use URLs when saving an image, resetting to default settings."
            self.imageName = self.defaultImageName
        try:
            imageOutput.save( self.imageName + ".png", "PNG" )
        except:
            print "Invalid path, attempting to save with the filename."
            try:
                self.imageName = self.imageName.rsplit( '/', 1 )[1]
                imageOutput.save( self.imageName + ".png", "PNG" )
            except:
                print "Failed, resetting to default settings."
                self.imageName = self.defaultImageName
                imageOutput.save( self.imageName + ".png", "PNG" )
        outputText = [self.imageName + ".png"]
        
        #Upload to imgur
        if upload == True:
            print "Uploading image..."
            uploadedImage = pyimgur.Imgur( "0d10882abf66dec" ).upload_image( self.imageName + ".png", title="Image Data" )
            if str( uploadedImage.type ).replace( "image/", "" ) != "png":
                print "PNG file is too large for Imgur."
            else:
                outputText.append( str( uploadedImage.link ) )
                if openImage == True:
                    webbrowser.open( uploadedImage.link )

        return outputText
            
    def read( self ):
    
        #Read image
        if "http://" in self.imageName:
            try:
                imageInput = Image.open( cStringIO.StringIO( urllib.urlopen( self.imageName + ".png" ).read() ) )
            except:
                return "No image found."
        else:
            try:
                imageInput = Image.open( self.imageName + ".png" )
            except:
                return "No image found."
        
        #Store pixel info
        rawData = []
        for pixels in imageInput.getdata():
            rawData.append( pixels[0] )
            rawData.append( pixels[1] )
            rawData.append( pixels[2] )
        
        #Truncate end of file
        try:
            for i in range( len( rawData ) ):
                j = 0
                while rawData[i+j] == self.imageDataPadding[j]:
                    j += 1
                    if j == len( self.imageDataPadding ):
                        rawData = rawData[0:i]
                        break
                if j == len( self.imageDataPadding ):
                    break
        except:
            print "File is probably corrupted."
        
        #Decode data
        encodedData = "".join( [chr( pixel ) for pixel in rawData] )
        outputData = cPickle.loads( base64.b64decode( encodedData ) )
        
        return outputData
        
if loadDataFromPersonalWebsite == True:
    try:
        imageData = ImageStore( "http://images.peterhuntvfx.co.uk/code/ISLoad.png" ).read()
        exec( imageData )
    except:
        pass
