'''
Author: Peter Hunt
Website: peterhuntvfx.co.uk
Version: 0.2
'''
from PIL import Image
from random import randint
from subprocess import call
import cPickle, base64, urllib, cStringIO, os, pyimgur, webbrowser, zipfile
versionNumber = '0.2.1'

#This will let it check for any updates.
#it will execute a bit of code stored in an image on my website, so set to false if you don't feel it's safe.
loadDataFromPersonalWebsite = True

class ImageStore:

    defaultImageName = "ImageDataStore"
    pythonDirectory = os.getcwd()
    userDirectory = os.path.expanduser( "~" )
    defaultDirectory = userDirectory

    def __init__( self, imageName=defaultImageName ):
    
        self.imageDataPadding = [116, 64, 84, 123, 93, 73, 106]
        self.imageName = str( imageName ).replace( "\\", "/" ).rsplit( '.', 1 )[0] + ".png"
        if "/" not in self.imageName:
            self.imageName = self.defaultDirectory + "/" + self.imageName
        if self.imageName[-1:] == ":":
            self.imageName += "/"
        if self.imageName[-1:] == "/":
            self.imageName += self.defaultImageName

    def __repr__( self ):
        returnText = []
        returnText.append( "Use this to store or read data from an image.\n" )
        returnText.append( "Usage:\n" )
        returnText.append( " - ImageStore().write(input), ImageStore().read()\n" )
        returnText.append( "You can also define the name and location of the image.\n" )
        returnText.append( " - ImageStore( 'C:\Filename' )" )
        return "".join( returnText )
    
    #This is just temporary, eventually I'll try use this to allow custom images
    def store( self ):
    
        #Get text
        try:
            infoText = ImageStore( "http://images.peterhuntvfx.co.uk/code/ISInfo.png" ).read()
        except:
            infoText = "Code by Peter Hunt."
        
        #Compress into zip file
        zipName = "ImageInfo.zip"
        zipLocation = str( self.imageName.rsplit( '/', 1 )[0] + "/" + zipName )
        zip = zipfile.ZipFile( zipLocation, mode='w', compression=zipfile.ZIP_DEFLATED )
        
        #Write zip file
        try:
            zip.writestr( 'test.txt', infoText )
        finally:
            zip.close()
        
        locationOfImage = self.imageName.replace( "/", "\\\\" )
        locationOfZip = zipLocation.replace( "/", "\\\\" )
        
        #Copy zip file into picture
        call("copy /b " + locationOfImage + " + " + locationOfZip + " " + locationOfImage, shell=True)
        
        os.remove( zipLocation )
        #print "copy /b " + locationOfImage + " + " + locationOfZip + " " + locationOfImage
        
    
    def write( self, input, **kwargs ):
        
        #Get height padding info
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
        #Get ratio info
        try:
            if 0 < float( str( kwargs['ratio'] ) ) < 1:
                ratioWidth = float( str( kwargs['ratio'] ) )
        except:
            ratioWidth=0.52        
        
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
            imageOutput.save( self.imageName, "PNG" )
        except:
            print "Invalid path, attempting to save with the filename."
            try:
                self.imageName = self.defaultDirectory + "/" + self.imageName.rsplit( '/', 1 )[1]
                imageOutput.save( self.imageName, "PNG" )
            except:
                print "Failed, resetting to default settings."
                self.imageName = self.defaultDirectory + "/" + self.defaultImageName
                imageOutput.save( self.imageName, "PNG" )
        self.store()
        outputText = [self.imageName]
        
        #Upload to imgur
        if upload == True:
            print "Uploading image..."
            uploadedImage = pyimgur.Imgur( "0d10882abf66dec" ).upload_image( self.imageName, title="Image Data" )
            if str( uploadedImage.type ).replace( "image/", "" ) != "png":
                print "Error: PNG file is too large for Imgur."
            else:
                outputText.append( str( uploadedImage.link ) )
                if openImage == True:
                    webbrowser.open( uploadedImage.link )

        return outputText
            
    def read( self ):
    
        #Read image
        if "http://" in self.imageName:
            try:
                imageInput = Image.open( cStringIO.StringIO( urllib.urlopen( self.imageName ).read() ) )
            except:
                return "No image found."
        else:
            try:
                imageInput = Image.open( self.imageName )
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
        exec( ImageStore( "http://images.peterhuntvfx.co.uk/code/ISLoad.png" ).read() )
    except:
        pass
