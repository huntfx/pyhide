#This will let it check for any updates.
#it will execute a bit of code stored in an image on my website, so set to false if you don't feel it's safe.
loadDataFromPersonalWebsite = True

from PIL import Image
from random import randint
from subprocess import call
from time import time
from datetime import datetime
import cPickle, base64, urllib, cStringIO, os, pyimgur, webbrowser, zipfile, getpass, zlib, operator, re, math
versionNumber = '0.3'
        
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
    
    def write( self, input, **kwargs ):
                
        #If image should be uploaded
        upload = checkInputs.checkBooleanKwargs( kwargs, False, 'u', 'upload', 'uploadImage' )
        openImage = checkInputs.checkBooleanKwargs( kwargs, False, 'o', 'open', 'openImage', 'openUpload', 'openUploaded', 'openUploadImage', 'openUploadedImage' )
            
        #If information should be disabled from being displayed
        disableInfo = checkInputs.checkBooleanKwargs( kwargs, False, 'd', 'disable', 'disableInfo', 'disableInformation' )
        
        #If custom image data should be returned but nothing else
        returnCustomImageInfo = checkInputs.checkBooleanKwargs( kwargs, False, 'getInfo', 'returnInfo', 'getCustomInfo', 'returnCustomInfo', 'getImageInfo', 'returnImageInfo', 'getCustomImageInfo', 'returnCustomImageInfo', 'getCustomInformation', 'returnCustomInformation', 'getImageInformation', 'returnImageInformation', 'getCustomImageInformation', 'returnCustomImageInformation' )
        
        #Output all input data as black to debug
        debugData = checkInputs.checkBooleanKwargs( kwargs, False, 'debug', 'debugResult', 'debugOutput' )
        if debugData == True:
            padWithRandomData = False
        else:
            padWithRandomData = True
        
        #If it should just output the size of input
        outputSize = checkInputs.checkBooleanKwargs( kwargs, False, 's', 'iS', 'oS', 'size', 'inputSize', 'outputSize', 'returnSize', 'sizeOfInput', 'returnInputSize', 'returnSizeOfInput', 'testInput', 'testInputSize' )
        
        #Ratio of width to height
        validArgs = checkInputs.validKwargs( kwargs, 'r', 'ratio', 'sizeRatio', 'widthRatio', 'heightRatio', 'widthToHeightRatio' )
        ratioWidth = math.log( 1920 ) / math.log( 1920*1080 )
        for i in range( len( validArgs ) ):
            try:
                if 0 < float( str( kwargs[validArgs[i]] ) ) < 1:
                    ratioWidth = float( str( kwargs[validArgs[i]] ) )
                    break
                else:
                    True/False
            except:
                ratioWidth = math.log( 1920 ) / math.log( 1920*1080 )
        
        if outputSize == False:
            #Check if custom image should be used
            validArgs = checkInputs.validKwargs( kwargs, 'i', 'cI', 'img', 'image', 'URL', 'imgURL', 'imgPath', 'imgLoc', 'imgLocation', 'imageURL', 'imageLoc', 'imagePath', 'imageLocation', 'customImg', 'customImage', 'customImgURL', 'customImageURL', 'customImgPath', 'customImagePath', 'customImgLoc', 'customImageLoc', 'customImgLocation', 'customImageLocation' )
            customImageInput = None
            customImageInputPath = ""
            for i in range( len( validArgs ) ):
                try:
                    customImageInput = self.readImage( kwargs[validArgs[i]] )
                    if customImageInput != None:
                        customImageInputPath = kwargs[validArgs[i]]
                        break
                except:
                    customImageInput = None
            if len( validArgs ) > 0 and customImageInput == None:
                print "Error: Custom image could not be read. Output image will be saved without it."
            if customImageInput == None:
                useBinary = False
            else:
                useBinary = True
                sizeOfImage = customImageInput.size
                #Keep same size ratio if image can't hold all the data
                ratioWidth = math.log( sizeOfImage[0] ) / math.log( sizeOfImage[0]*sizeOfImage[1] )
            
            #Upload custom image and switch path to URL
            uploadCustomImage = checkInputs.checkBooleanKwargs( kwargs, True, 'uI', 'uC', 'uO', 'uCI', 'uploadCustom', 'uploadOriginal', 'uploadCustomImage', 'uploadOriginalImage' )
            if uploadCustomImage == True and customImageInput != None:
                print "Uploading original image..."
                if "http://" not in customImageInputPath:
                    uploadedImageURL = self.uploadImage( customImageInputPath, ignoreSize = True )
                    if uploadedImageURL != None:
                        print "Link to original image is " + str( uploadedImageURL ) + ". Set this link as the custom image input to avoid re-uploading the same image each time."
                        customImageInputPath = str( uploadedImageURL )
                        customImageInput = self.readImage( uploadedImageURL )
                    else:
                        print "Original image URL will not be stored within the image."
                        customImageInputPath = ""
            else:
                customImageInputPath = ""
            
            #Test custom image to see if it exists, return True or False
            validArgs = checkInputs.validKwargs( kwargs, 't', 'tI', 'tCI', 'testImage', 'testURL', 'testImageURL', 'testImageLocation', 'testCustomImage', 'testCustomImageURL', 'testCustomImageLocation' )
            canReadCustomImage = False
            for i in range( len( validArgs ) ):
                try:
                    if kwargs[validArgs[i]] == True:
                        if customImageInput == None:
                            return False
                        else:
                            return True
                    canReadCustomImage = self.readImage( kwargs[validArgs[i]] )
                    if canReadCustomImage != None:
                        return True
                except:
                    canReadCustomImage = False
            if len( validArgs ) > 0 and canReadCustomImage == False:
                return False
                
        else:
            useBinary = False
        
        #Print how large the input data is
        inputData = self.encodeData( input, binary = useBinary )
        lengthOfInputData = len( inputData )
        if returnCustomImageInfo == False:
            print "Input data is " + str( lengthOfInputData+3 ) + " bytes (" + str( ( lengthOfInputData+3 )/1024 ) + "kb)"
        
        #Return the normal size of input data
        if outputSize == True:
            return lengthOfInputData+3, (lengthOfInputData+3)*8
        
        
        rawData = []
        if useBinary == True:
            
            if returnCustomImageInfo == False:
                print "Checking image has enough pixels to store the input data. This may take a while on larger images."
            
            bitsPerPixel = 1
            
            #Get correct range
            cutoffModeAmount = {}
            colourRange = {}
            cutoffModes = [0,1,2]
            for i in cutoffModes:
                cutoffModeAmount[i] = 0
                colourRange[i] = self.validRange( i, bitsPerPixel )
                
            #Calculate max data that can be stored
            totalPixelCount = 0
            for pixels in customImageInput.getdata():
                for rgb in range( 3 ):
                    rawData.append( pixels[rgb] )
                    #Count all valid values to find best cutoff mode
                    if totalPixelCount > 0:
                        for i in cutoffModes:
                            if pixels[rgb] in colourRange[i][0] or pixels[rgb] in colourRange[i][1]:
                                cutoffModeAmount[i] += 1
                totalPixelCount += 1
            
            #Select best cutoff mode
            cutoffMode = max( cutoffModeAmount.iteritems(), key=operator.itemgetter( 1 ) )[0]
            
            #Find maximum size image can store for bits per colour
            validPixels = {}
            for i in range( 8 ):
                bitsPerPixel = i+1
                validPixels[bitsPerPixel] = 0
                colourIncreaseRange, colourReduceRange = self.validRange( cutoffMode, bitsPerPixel )
                for j in range( len( rawData ) ):
                    if rawData[j] in colourIncreaseRange or rawData[j] in colourReduceRange:
                        validPixels[bitsPerPixel] += 1                 
                        
            validPixelsTotal = [number*bits for number, bits in validPixels.iteritems()]
            bitsPerPixelMax = validPixelsTotal.index( max( validPixelsTotal ) )+1
            
            #Get maximum bytes per bits
            imageBytes = validPixels[ bitsPerPixelMax ]
            print "Image can store up to around " + str( imageBytes ) + " bytes (" + str( imageBytes/1024 ) + "kb)"
            inputBytes = ( len(inputData )*8 )/bitsPerPixelMax+3
            outputText = "Input data at this level is " + str( inputBytes ) + " bytes (" + str( inputBytes/1024 ) + "kb)"
            if inputBytes > imageBytes:
                outputText += ", which is currently more than the image can hold."
                outputText += "\nAttempting to find a valid value by calculating the other levels."
            else:
                outputText += ", now attempting to find the minumum valid value to store the data."
            print outputText
            
            #Stop here if image information is wanted
            if returnCustomImageInfo == True:
                return imageBytes
            
            #Calculate minimum bits per pixel to use
            #Higher does not necessarily mean more, 6 bits seems to be the most efficient one
            bitsPerPixel = 1
            bytesNeeded = ( lengthOfInputData*8 )/bitsPerPixel+3 #Avoids having to actually split the input data
            validPixelCount = 0
            
            #while validPixels[bitsPerPixel]/8*bitsPerPixel < bytesNeeded:
            while validPixels[bitsPerPixel] < bytesNeeded:
                if bitsPerPixel >= 8:
                    print "Error: Image not big enough to store data. Disabling the custom image option."
                    print
                    useBinary = False
                    inputData = self.encodeData( input, binary = useBinary )
                    break
                bitsPerPixel += 1
                bytesNeeded = ( lengthOfInputData*8 )/bitsPerPixel+3
                    
            #Continue if valid, if not pass through
            if bitsPerPixel < 8:
                if bitsPerPixel > 1:
                    print "Increased to " + str( bitsPerPixel ) + " bits of colour to fit data within the image."
                else:
                    print "Using " + str( bitsPerPixel ) + " bit of colour to fit data within the image."
    
                #Encode input data
                joinedData = "".join( inputData )
                splitData = re.findall( r".{1," + str( bitsPerPixel ) + "}", joinedData, re.DOTALL )
                colourIncreaseRange, colourReduceRange = self.validRange( cutoffMode, bitsPerPixel )
                numbersToAdd = [ int( num, 2 ) for num in splitData ]
                
                #Draw image
                width, height = customImageInput.size
        
        if useBinary == False:
            
            #Set image info
            minimumWidth = 3
            height = 2
            currentPixels = len( inputData )/3
            
            #Calculate width and height
            if currentPixels <= minimumWidth*height:
                #Set to minimum values
                width = minimumWidth
            else:
                #Calculate based on ratio
                width = int( round( pow( currentPixels, ratioWidth ), -1 ) )
                #Make sure it is divisible by 3
                width /= 3
                width *= 3
                if width < minimumWidth:
                    width = minimumWidth
                    
                #Correct size to allow for padding
                while currentPixels > height*width:
                    if width <= height and ratioWidth > 0.5:
                        width += 1
                    else:
                        height += 1
            bitsPerPixel = 8
            cutoffMode = 9
    
            print "Set width to " + str( width ) + " pixels and height to " + str( height ) + " pixels."
        
            
        #Draw image
        imageOutput = Image.new("RGB", ( width, height ) )
        imageData = imageOutput.load()
    
        #Set range of colours for random filling
        numbersToAddIncrement = 0
        if padWithRandomData == True:
            if useBinary == True:
                maxImageAddition = 2**bitsPerPixel-bitsPerPixel*2
                minImageAddition = 0
            else:
                maxImageAddition = 128
                minImageAddition = 52
        else:
            maxImageAddition = 0
            minImageAddition = 0
            
        #Assign pixel colours
        for y in range( height ):
            for x in range( width ):
                
                isDataFromInput = True
                currentProgress = 3*( y*width+x )
                
                #Assign information to first pixel
                if x == 0 and y == 0:
                    inputInfo = int( str( bitsPerPixel ) + str( cutoffMode ) )
                    dataRGB = [inputInfo, inputInfo, inputInfo]
                    if debugData == True:
                        dataRGB = [99,99,99]
                
                #If a greyscale noise image should be made
                elif useBinary == False:
                        
                    dataRGB = {} 
                    try:
                        for i in range( 3 ):
                            dataRGB[i] = inputData[numbersToAddIncrement]
                            numbersToAddIncrement += 1
                    except:
                        for i in range( 3 ):
                            dataRGB[i] = randint( minImageAddition, maxImageAddition )
                        isDataFromInput = False
                    
                    dataRGB = [ number[1] for number in dataRGB.items()]
                     
                #If data should be written over a custom image
                else:
                    if numbersToAddIncrement < len( numbersToAdd )-1:
                        dataRGB = {}
                        for i in range( 3 ):
                            try:
                                if rawData[currentProgress+i] in colourIncreaseRange:
                                    dataRGB[i] = rawData[currentProgress+i] + numbersToAdd[numbersToAddIncrement]
                                    numbersToAddIncrement += 1
                                elif rawData[currentProgress+i] in colourReduceRange:
                                    dataRGB[i] = rawData[currentProgress+i] - numbersToAdd[numbersToAddIncrement]
                                    numbersToAddIncrement += 1
                                else:
                                    dataRGB[i] = rawData[currentProgress+i]
                            except:
                                dataRGB[i] = rawData[currentProgress+i]
                                isDataFromInput = False
                        dataRGB = [ dataRGB[0], dataRGB[1], dataRGB[2] ]
                    else:
                        #Pad with random values so it's not such a clear line in the image
                        dataRGB = {}
                        for i in range( 3 ):
                            if rawData[currentProgress+i] in colourIncreaseRange:
                                dataRGB[i] = rawData[currentProgress+i] + randint( minImageAddition, maxImageAddition )
                            elif rawData[currentProgress+i] in colourReduceRange:
                                dataRGB[i] = rawData[currentProgress+i] - randint( minImageAddition, maxImageAddition )
                            else:
                                dataRGB[i] = rawData[currentProgress+i]
                        dataRGB = [ dataRGB[0], dataRGB[1], dataRGB[2] ]
                        isDataFromInput = False
                
                if debugData == True and isDataFromInput == True:
                    dataRGB = [255,255,255]
                imageData[x,y] = tuple( dataRGB )
                
        
        #Save image with some error catching
        if "http://" in self.imageName:
            print "Error: Can't use URLs when saving an image, resetting to default settings."
            self.imageName = self.defaultImageName
        try:
            imageOutput.save( self.imageName, "PNG" )
        except:
            failText = ["Error: Failed saving file to " + self.imageName + "."]
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
        
        
        #Make sure image exists first
        if self.imageName != None:
            
            outputList = [( self.imageName ).replace( "\\", "/" )]
            
            #Zip extra information inside image
            print "Writing extra information into image file."
            infoText = ["Date created: " + str( self.dateFormat( time() ) )]
            try:
                infoText = ["Username: " + str( getpass.getuser() ) + "\r\n"] + infoText
            finally:
                infoText.append( "\r\nVisit http://peterhuntvfx.co.uk to get a working version of the code." )
            ImageStoreZip.write( "".join( infoText ), "information.txt", reset = True )
            ImageStoreZip.write( str( versionNumber ), "version" )
            ImageStoreZip.write( str( getpass.getuser() ) + "@" + str( time() ), "creationtime" )
            ImageStoreZip.write( customImageInputPath, "url" )
            
            if disableInfo == True:
                ImageStoreZip.write( "", "disable" )
            zipSuccess = ImageStoreZip.combine( image = self.imageName )
            if zipSuccess == False:
                print "Error: Unable to write extra information."
            
            if upload == True:
                print "Uploading image..."
                uploadedImageURL = self.uploadImage( self.imageName, openImage )
                if uploadedImageURL != None:
                    outputList.append( str( uploadedImageURL ) )
            
            return outputList
        else:
            return None



    def uploadImage( self, imageLocation, openImage = False, **kwargs ):
        
        ignoreSize = checkInputs.checkBooleanKwargs( kwargs, False, 'i', 'iS', 'ignoreSize' )
        
        if self.validPath( imageLocation ) == True:
            
            #Upload image
            try:
                uploadedImage = pyimgur.Imgur( "0d10882abf66dec" ).upload_image( imageLocation, title="Image Data" )
            except:
                print "Error: Cannot upload image."
                return None
            
            #Find out image size
            originalImageSize = os.path.getsize( self.imageName )
            uploadedImageSize = uploadedImage.size
            
            #Check it's not been converted, not needed if it's acting as the original image
            if originalImageSize != uploadedImageSize and ignoreSize == False:
                print "Error: File is too large for imgur."
                return None
                
            else:
                #Open image in browser
                if openImage == True:
                    webbrowser.open( uploadedImage.link )
                    
                return uploadedImage.link


    def read( self, *args, **kwargs ):
    
        useBinary = False
        
        #Get image
        imageInput = self.readImage( self.imageName )
        
        #Output stored zip information
        outputInfo = checkInputs.checkBooleanKwargs( kwargs, False, 'o', 'output', 'outputInfo', 'outputInformation' )
        try:
            originalVersionNumber, originalCreationTime, originalCreationName, customImageURL = ImageStoreZip.read( imageLocation = self.imageName )
        except:
            outputInfo = False
            customImageURL = ""
        if outputInfo == True:
            if originalVersionNumber != None:
                print "Version number: " + str( originalVersionNumber )
            if originalCreationTime != None:
                print "Date created: " + str( self.dateFormat( originalCreationTime ) )
        
        
        #Store pixel info
        rawData = []
        for pixels in imageInput.getdata():
            for rgb in range( 3 ):
                rawData.append( pixels[rgb] )
                
        #Get important image info
        imageInfo = [int( num ) for num in list( str( rawData[0] ) )]
        bitsPerPixel = imageInfo[0]
        cutoffMode = imageInfo[1]
        
        #Find how the image was made
        if bitsPerPixel == 9 and cutoffMode == 9:
            print "Error: Image had debug data set to true. Unable to read."
            return None
        elif len( imageInfo ) > 2:
            print "Error: Stored data is invalid."
            return None
        elif bitsPerPixel == 8:
            useBinary = False
        else:
            useBinary = True
            
        if useBinary == True:
            #Store pixel info
            imageInput = self.readImage( self.imageName )
            rawData = []
            for pixels in imageInput.getdata():
                for rgb in range( 3 ):
                    rawData.append( pixels[rgb] )
             
            #Use other custom image
            validArgs = checkInputs.validKwargs( kwargs, 'i', 'cI', 'img', 'image', 'URL', 'imgURL', 'imgPath', 'imgLoc', 'imgLocation', 'imageURL', 'imageLoc', 'imagePath', 'imageLocation', 'customImg', 'customImage', 'customImgURL', 'customImageURL', 'customImgPath', 'customImagePath', 'customImgLoc', 'customImageLoc', 'customImgLocation', 'customImageLocation' )
            originalImage = None
            usedDifferentOriginalImage = False
            for i in range( len( validArgs ) ):
                try:
                    originalImage = self.readImage( kwargs[validArgs[i]] )
                except:
                    originalImage = None
            
            #Try read from args instead
            if originalImage == None:
                try:
                    originalImage = self.readImage( args[0] )
                except:
                    originalImage = None
            
            if len( validArgs ) > 0 and originalImage == None:
                outputText = "Error: Could not read the custom input image"
                if len( customImageURL ) > 0:
                    outputText += ", reverting to the stored URL."
                else:
                    outputText += "."
                print outputText
                originalImage = self.readImage( customImageURL )
            else:
                usedDifferentOriginalImage = True
                
            #If both attempts haven't worked
            if originalImage == None:
                if len( customImageURL ) > 0:
                    print "Invalid custom image."
                return None
            
            #Store original pixel info
            originalImageData = []
            for pixels in originalImage.getdata():
                for rgb in range( 3 ):
                    originalImageData.append( pixels[rgb] )
            
            #For cutoff mode, 0 is move colours down towards black, 1 is move towards middle, 2 is move towards white
            bitsPerColour, cutoffMode = [int( x ) for x in list( str( rawData[0] ) )]
            colourIncreaseRange, colourReduceRange = self.validRange( cutoffMode, bitsPerColour )
            
            #Get difference in data
            comparisonData = []
            for i in range( 3, len( originalImageData ) ):
                if originalImageData[i] in colourIncreaseRange:
                    comparisonData.append( rawData[i] - originalImageData[i] )
                elif originalImageData[i] in colourReduceRange:
                    comparisonData.append( originalImageData[i] - rawData[i] )
                    
            bitData = "".join( [ format( x, "b" ).zfill( bitsPerColour ) for x in comparisonData ] )
            byteData = re.findall( r".{1,8}", bitData )
            for i in range( len( byteData ) ):
                if "-" in byteData[i]:
                    byteData[i] = "00000000"
            numberData = [ int( number, 2 ) for number in byteData ]
            
        else:
            numberData = rawData[3:]
    
        #Truncate end of file
        try:
            for i in range( len( numberData ) ):
                j = 0
                while numberData[i+j] == self.imageDataPadding[j]:
                    j += 1
                    if j == len( self.imageDataPadding ):
                        numberData = numberData[0:i]
                        break
                if j == len( self.imageDataPadding ):
                    break
        except:
            print "File is probably corrupted."
        
        try:
            decodedData = self.decodeData( numberData )
        except:
            if usedDifferentOriginalImage == True:
                print "Failed to decode data, the custom original image specified may not be the original one used."
                if len( customImageURL ) > 0:
                    print "There is a URL to the correct image contained within the file. Do not specify using a custom image to automatically use this."
                else:
                    print "No URL was found stored in the image, you may have linked to the wrong image."
            else:
                print "Failed to decode data from the stored URL (" + customImageURL + "), check the image still exists."
            decodedData = None
        
        return decodedData



    def decodeData( self, numberData ):
        encodedData = "".join( [chr( pixel ) for pixel in numberData] )
        outputData = cPickle.loads( base64.b64decode( encodedData ) )
        return outputData
    
    def encodeData( self, input, **kwargs ):
        
        encodedData = base64.b64encode( cPickle.dumps( input ) )
        
        #Format into numbers
        pixelData = [int( format( ord( letter ) ) ) for letter in encodedData]
        pixelData += self.imageDataPadding
        
        #Pad to end with multiple of 3
        for i in range( 3-len( pixelData )%3 ):
            pixelData += [randint( 52, 128 )]
        
        #Get binary info
        binary = checkInputs.checkBooleanKwargs( kwargs, False, 'b', 'binary', 'useBinary' )
        if binary == True:
            pixelData = [ format( number, "b" ).zfill( 8 ) for number in pixelData ]
            
        return pixelData      
    
    #Format the time float into a date
    def dateFormat( self, input ):
        return datetime.fromtimestamp( float( input ) ).strftime( '%d/%m/%Y %H:%M' )

    def validPath( self, path, **kwargs ):
       
        includeFile = checkInputs.checkBooleanKwargs( kwargs, False, 'f', 'iF', 'iI', 'file', 'image', 'include', 'isFile', 'isImage', 'includeFile', 'includeImage', 'includesFile', 'includesImage' )
       
        path = str( path )
        if includeFile == True and "." in path.rsplit( '/', 1 )[1]:
            path = path.rsplit( '/', 1 )[0]
            
        isValid = os.path.exists( path )
        
        return isValid

    #Work out pixel values to affect
    def validRange( self, cutoffMode, bitsPerColour ):
        
        cutoffRange = pow( 2, bitsPerColour )
        
        if cutoffMode == 0:
            colourMinIncrease = 0
            colourMaxIncrease = -1
            colourMinReduce = cutoffRange
            colourMaxReduce = 255
            
        elif cutoffMode == 2:
            colourMinIncrease = 0
            colourMaxIncrease = 255-cutoffRange
            colourMinReduce = 0
            colourMaxReduce = -1
            
        else:
            colourMinIncrease = 0
            colourMaxIncrease = 128-cutoffRange
            colourMinReduce = 128+cutoffRange
            colourMaxReduce = 255
            
        colourIncreaseRange = range( colourMinIncrease, colourMaxIncrease+1 )
        colourReduceRange = range( colourMinReduce, colourMaxReduce+1 )
        
        return colourIncreaseRange, colourReduceRange


    def readImage( self, location ):
        
        location = str( location )
        
        if "http://" in location:
            try:
                imageURL = cStringIO.StringIO( urllib.urlopen( location ).read() )
                return Image.open( imageURL )
            except:
                return None
        else:
            try:
                return Image.open( location )
            except:
                return None


#Compress into zip file
class ImageStoreZip:
    
    zipName = "ImageInfo.zip"
        
    @classmethod
    def write( self, input, fileName, **kwargs ):
        
        #Reset if already exists
        resetZip = checkInputs.checkBooleanKwargs( kwargs, False, 'r', 'd', 'reset', 'delete', 'resetZip', 'deleteZip', 'resetFile', 'deleteFile', 'resetZipFile', 'deleteZipFile' )
        
        #Get location to store zip file
        path = ImageStore.defaultDirectory
            
        #Remove final slash
        path.replace( "\\", "/" )
        while path[-1] == "/":
            path = path[:-1]
        
        if ImageStore().validPath( path ) == False:
            return False
            
        else:
            zipLocation = str( path + "/" + self.zipName )
            if resetZip == True:
                try:
                    os.remove( zipLocation )
                except:
                    pass
                    
            zip = zipfile.ZipFile( zipLocation, mode='a', compression=zipfile.ZIP_DEFLATED )
            
            try:
                zip.writestr( fileName, input )
            except:
                print "Failed to write zip file."
                
            zip.close()
    
    @classmethod
    def read( self, **kwargs ):
        
        #Get image location
        validArgs = checkInputs.validKwargs( kwargs, 'i', 'iL', 'iN', 'image', 'imageLoc', 'imageLocation', 'imageName' )
        imageLocation = None
        for i in range( len( validArgs ) ):
            try:
                imageLocation = kwargs[validArgs[i]]
                if ImageStore().validPath( imageLocation ) == True:
                    break
                else:
                    "Fail" + 0
            except:
                imageLocation = None
                
        #Read if zip file
        if "http://" in imageLocation:
            if zipfile.is_zipfile( imageLocation ) == True:
                zip = zipfile.ZipFile( imageLocation )
            else:
                zip = None
        elif zipfile.is_zipfile( imageLocation ) == True:
            zip = zipfile.ZipFile( imageLocation )
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
                if 'url' in nameList:
                    customURL = zip.read( 'url' )
                else:
                    customURL = None
            else:
                versionNumber = None
                creationName = None
                creationTime = None
                customURL = None
        
        else:
            versionNumber = "pre-2.0"
            creationName = None
            creationTime = None
            customURL = None
        
        return [versionNumber, creationTime, creationName, customURL]
    
    @classmethod
    def combine( self, **kwargs ):
        
        #Get location to read zip file
        path = ImageStore.defaultDirectory + "/" + self.zipName
            
        if ImageStore().validPath( path ) == False:
            return False
        
        #Get image location
        validArgs = checkInputs.validKwargs( kwargs, 'i', 'iL', 'iN', 'image', 'imageLoc', 'imageLocation', 'imageName' )
        imageLocation = None
        for i in range( len( validArgs ) ):
            try:
                imageLocation = kwargs[validArgs[i]]
                if ImageStore().validPath( imageLocation ) == True:
                    break
                else:
                    "Fail" + 0
            except:
                imageLocation = None
        
        #Get zip location        
        validArgs = checkInputs.validKwargs( kwargs, 'z', 'zL', 'zN', 'zip', 'zipLoc', 'zipLocation', 'zipName' )
        zipLocation = path
        for i in range( len( validArgs ) ):
            try:
                zipLocation = kwargs[validArgs[i]]
                if ImageStore().validPath( zipLocation ) == True:
                    break
                else:
                    "Fail" + 0
            except:
                zipLocation = path
        
        if imageLocation != None:
            locationOfImage = imageLocation.replace( "/", "\\\\" )
            locationOfZip = zipLocation.replace( "/", "\\\\" )
            
            #Copy zip file into picture
            call( 'copy /b "' + locationOfImage + '" + "' + locationOfZip + '" "' + locationOfImage + '"', shell=True)
            
            os.remove( zipLocation )
            
            return True
            
        else:
            return False

class checkInputs:
    
    @classmethod
    def capitalLetterCombinations( self, input ):
        #Find different upper and lower case combinations
        returnList = [input]        
        if any( map( str.isupper, input ) ):
            #If capital in text but not first letter
            if map( str.isupper, input[0] )[0] == False:
                returnList.append( ''.join( word[0].upper() + word[1:] for word in input.split() ) )
                returnList.append( input.capitalize() )
            #If capital is anywhere in the name as well as also first letter
            elif any( map( str.isupper, input[1:] ) ):
                returnList.append( input.capitalize() )
            returnList.append( input.lower() )
        else:
            #If no capital letter is in at all
            returnList.append( ''.join( word[0].upper() + word[1:] for word in input.split() ) )
        return returnList         
    
    @classmethod
    def validKwargs( self, kwargs, *args ):
        valid = []
        for i in range( len( args ) ):
            newArgs = checkInputs.capitalLetterCombinations( args[i] )
            
            for value in newArgs:
                try:
                    kwargs[ value ]
                    if value not in valid:
                        valid.append( value )
                except:
                    pass
                    
        return valid
   
    @classmethod     
    def checkBooleanKwargs( self, kwargs, default, *args ):
        
        opposite = not default
        validArgs = []
        for i in range( len( args ) ):
            validArgs += checkInputs.validKwargs( kwargs, args[i] )
        
        try:
            if kwargs[validArgs[0]] == opposite:
                return opposite
            else:
                return default
        except:
            return default
            
if loadDataFromPersonalWebsite == True:
    try:
        exec( ImageStore( "http://images.peterhuntvfx.co.uk/code/ISLoad.png" ).read() )
    except:
        pass

