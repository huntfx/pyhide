'''
Author: Peter Hunt
Website: peterhuntvfx.co.uk
Version: 0.2
'''
from PIL import Image
from random import randint
from subprocess import call
from time import time
from datetime import datetime
import cPickle, base64, urllib, cStringIO, os, pyimgur, webbrowser, zipfile, getpass, zlib
versionNumber = '0.2.1'

#This will let it check for any updates.
#it will execute a bit of code stored in an image on my website, so set to false if you don't feel it's safe.
loadDataFromPersonalWebsite = True

class ImageStore:

    defaultImageName = "ImageDataStore.png"
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
    #It'll write the original imagine to the file, and the difference between the two will contain the data
    #Writing the image will be optional, but if disabled you will need to provide the original image separately
    #If anyone has a better suggestion I'd be happy to hear it
    def writeZip( self, disableInfo = False ):
    
        #Define the text
        infoText = ["Date created: " + str( self.outputTime( time() ) )]
        try:
            infoText = ["Username: " + str( getpass.getuser() ) + "\r\n"] + infoText
        finally:
            infoText.append( "\r\nVisit http://peterhuntvfx.co.uk to get a working version of the code." )
        
        #Compress into zip file
        zipName = "ImageInfo.zip"
        zipLocation = str( self.imageName.rsplit( '/', 1 )[0] + "/" + zipName )
        zip = zipfile.ZipFile( zipLocation, mode='w', compression=zipfile.ZIP_DEFLATED )
        
        #Write zip file
        try:
            zip.writestr( 'infomation.txt', "".join( infoText ) )
            zip.writestr( 'version', str( versionNumber ) )
            zip.writestr( 'creationtime', str( getpass.getuser() ) + "@" + str( time() ) )
            if disableInfo == True:
                zip.writestr( 'disable', "" )
        finally:
            zip.close()
        
        locationOfImage = self.imageName.replace( "/", "\\\\" )
        locationOfZip = zipLocation.replace( "/", "\\\\" )
        
        #Copy zip file into picture
        call( 'copy /b "' + locationOfImage + '" + "' + locationOfZip + '" "' + locationOfImage + '"', shell=True)
        
        os.remove( zipLocation )
    
    def readZip( self ):
        
        #Read if zip file
        if "http://" in self.imageName:
            if zipfile.is_zipfile( self.imageURL ) == True:
                zip = zipfile.ZipFile( self.imageURL )
        elif zipfile.is_zipfile( self.imageName ) == True:
            zip = zipfile.ZipFile( self.imageName )
        else:
            zip = None
        
        #Read zip data
        if zip != None:
            nameList = zip.namelist()
            if 'disable' not in nameList:
                if 'version' in nameList:
                    versionNumber = zip.read( 'version' )
                else:
                    versionNumber = "pre-2.0"
                if 'creationtime' in nameList:
                    creation = zip.read( 'creationtime' )
                else:
                    creation = None
                if creation != None:
                    creationName = creation.split( "@" )[0]
                    creationTime = creation.split( "@" )[1]
            else:
                versionNumber = None
                creationName = None
                creationTime = None
        
        else:
            versionNumber = "pre-2.0"
            creationName = None
            creationTime = None
        
        return [versionNumber, creationTime, creationName]
                
    def outputTime( self, timeInt ):
        return datetime.fromtimestamp( float( timeInt ) ).strftime( '%d/%m/%Y %H:%M' )
        
    def write( self, input, **kwargs ):
        
        #Get height padding info
        try:
            heightPadding = int( kwargs['padding'] )
        except:
            heightPadding = 12
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
        #Get disable info
        try:
            if kwargs['disableInfo'] == True:
                disableInfo = True
            else:
                disableInfo = False
        except:
            disableInfo = False     
        
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
            failText = ["Failed saving file to " + self.imageName + "."]
            failText.append( "You may have incorrect permissions or the file may be in use." )
            failText.append( "\nAttempting to save in new location..." )
            print " ".join( failText )
            savingFailed = "\nFailed to save file."
            
            #If already in default directory
            if self.imageName.rsplit( '/', 1 )[0] == self.defaultDirectory:
                if self.imageName.rsplit( '/', 1 )[1] == self.defaultImageName:
                    self.imageName = None
                    failText = savingFailed
                else:
                    try:
                        self.imageName = self.defaultDirectory + "/" + self.defaultImageName
                        imageOutput.save( self.imageName, "PNG" )
                        failText = None
                    except:
                        self.imageName = None
                        failText = savingFailed
            #If not in default directory
            else:
                try:
                    self.imageName = self.defaultDirectory + "/" + self.imageName.rsplit( '/', 1 )[1]
                    imageOutput.save( self.imageName, "PNG" )
                    failText = None
                except:
                    try:
                        self.imageName = self.defaultDirectory + "/" + self.defaultImageName
                        imageOutput.save( self.imageName, "PNG" )
                        failText = None
                    except:
                        failText = savingFailed
                        self.imageName = None
        
        outputText = [self.imageName.replace( "\\", "/" )]
        
        #Make sure image exists first
        if self.imageName != None:
        
            self.writeZip( disableInfo )
            
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
        else:
            print failText
            
        return outputText
            
    def read( self, **kwargs ):
    
        #Get output version info
        try:
            if kwargs['output'] == True:
                outputVersion = True
            else:
                outputVersion = False
        except:
            outputVersion = False
    
        #Read image
        if "http://" in self.imageName:
            try:
                self.imageURL = cStringIO.StringIO( urllib.urlopen( self.imageName ).read() )
                imageInput = Image.open( self.imageURL )
            except:
                return "No image found."
        else:
            try:
                imageInput = Image.open( self.imageName )
            except:
                return "No image found."
     
        #Get some custom data
        if outputVersion == True:
            originalVersionNumber, originalCreationTime, originalCreationName = self.readZip()
            if originalVersionNumber != None:
                print "Version number: " + str( originalVersionNumber )
            if originalCreationTime != None:
                print "Date created: " + str( self.outputTime( originalCreationTime ) )
        
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
