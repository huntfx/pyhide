'''
Author: Peter Hunt
Website: peterhuntvfx.co.uk
Version: 3.2
'''
#You can edit these values, but they lack error checking so be careful
def defaults():

    #These values will override any given to the script, set any 'force' value to True to use the corresponding settings below
    forceCustomFilename = False
    forceCustomImages = False
    forceUpload = False
    forceOpenImageOnUpload = False
    forceDisableSaving = False
    forceCacheWrite = False
    forceVerify = False
    
    customFilename = "ImageStore.png" #May include a path
    customImage = None #Set to None to disable, or give a path
    shouldUpload = True
    shouldOpenImageOnUpload = False
    shouldDisableSaving = False
    shouldWriteCache = True
        
    #Saving the image
    defaultImageName = "ImageDataStore.png"
    defaultImageDirectory = GlobalValues.userDirectory
    
    #Saving the cache
    defaultCacheName = "ImageStore.cache"
    defaultCacheDirectory = GlobalValues.pythonDirectory
    
    #Displaying a percentage of completion on long calculations
    outputProgressIterations = 2**12 #Check time after this many calculations
    outputProgressTime = 0.25 #Output progress after this many seconds
    
    output = [[defaultImageName, defaultImageDirectory]]
    output.append( [defaultCacheName, defaultCacheDirectory] )
    output.append( [outputProgressTime, outputProgressIterations] )
    disableList = [[forceCustomFilename, customFilename]]
    disableList.append( [forceCustomImages, customImage] )
    disableList.append( [forceUpload, shouldUpload] )
    disableList.append( [forceOpenImageOnUpload, shouldOpenImageOnUpload] )
    disableList.append( [forceDisableSaving, shouldDisableSaving] )
    disableList.append( [forceCacheWrite, shouldWriteCache] )
    output.append( disableList )
    return output 
    
try:
    from PIL import Image
except:
    raise ImportError( "Python Imaging Library module was not found" )
from random import randint
from subprocess import call
from time import time, sleep
from datetime import datetime
import cPickle, base64, urllib2, cStringIO, os, webbrowser, zipfile, getpass, zlib, operator, re, math, md5, itertools, inspect

#Disable upload features if requests and pyimgur are not found
printImportError = True #Set this to false if you want to disable the warning if pyimgur or requests are not found
global overrideUpload
try:
    import pyimgur, requests
    overrideUpload = False
except:
    outputText = "Warning: Error importing pyimgur{0}, disabling the upload features."
    try:
        import requests
        outputText = outputText.format( "" )
    except:
        outputText = outputText.format( " and requests" )
    if printImportError == True:
        print outputText
    overrideUpload = True

#Check if running from Maya
global mayaEnvironment
mayaEnvironment = False
try:
    import pymel.core as py
    import maya.utils as utils
    mayaEnvironment = True
except:
    pass

#Other fixed global values
class GlobalValues:
    newLine = os.linesep
    pythonDirectory = os.getcwd().replace( "\\", "/" )
    userDirectory = os.path.expanduser( "~" ).replace( "\\", "/" )

class ImageStore:
    
    startTime = time()
    defaultValues = defaults()
    defaultImageName = defaultValues[0][0]
    defaultImageDirectory = defaultValues[0][1]
    defaultCacheName = defaultValues[1][0]
    defaultCacheDirectory = defaultValues[1][1]
    outputProgressTime = defaultValues[2][0]
    outputProgressIterations = defaultValues[2][1]
    forceCustomFilenames = defaultValues[3][0][0]
    useThisCustomFilename = defaultValues[3][0][1]
    forceCustomImages = defaultValues[3][1][0]
    useThisCustomImage = defaultValues[3][1][1]
    forceUpload = defaultValues[3][2][0]
    shouldUpload = defaultValues[3][2][1]
    forceOpenOnUpload = defaultValues[3][3][0]
    shouldOpenOnUpload = defaultValues[3][3][1]
    forceDeleteFile = defaultValues[3][4][0]
    shouldDeleteFile = defaultValues[3][4][1]
    forceCacheWrite = defaultValues[3][5][0]
    shouldWriteCache = defaultValues[3][5][1]
                
    imageDataPadding = [116, 64, 84, 123, 93, 73, 106]
    firstPixelPadding = [92, 101]
    versionNumber = "3.2"
    maxCutoffModes = 7
    website = "http://peterhuntvfx.co.uk"
    protocols = ["http://", "https://"]
    debugging = False
    validateWrite = False
    
    #Maya
    renderViewSaveLocation = "{0}/RenderViewTemp".format( defaultCacheDirectory )
    renderViewCaption = "Image Store Output"
    
    #Percent completed
    writeProgress = {}
    writeProgress["CalculatingInputSize"] = 0
    writeProgress["InputSizeIs"] = 2
    writeProgress["CheckingImage"] = 2
    writeProgress["CalculatingCutoffMode"] = 63
    writeProgress["UsingCutoffMode"] = writeProgress["CalculatingCutoffMode"]
    writeProgress["CalculatingMaxImageData"] = 83
    writeProgress["ImageCanStore"] = writeProgress["CalculatingMaxImageData"]
    writeProgress["InputAtMax"] = 84
    writeProgress["MinimumBitsPerPixel"] = 85
    writeProgress["ChooseBitsPerPixel"] = 86
    writeProgress["SetDimensions"] = 88
    writeProgress["CalculatingImage"] = 95
    writeProgress["SavingImage"] = 97
    writeProgress["WritingExtraInformation"] = 98
    writeProgress["Validate"] = 100
    readProgress = {}
    readProgress["ReadingImage"] = 0
    readProgress["ReadingFiles"] = 6
    readProgress["FilesStored"] = 8
    readProgress["StoringPixels"] = 20
    readProgress["FirstPixel"] = 21
    readProgress["StoringCustomPixelInfo"] = 40
    readProgress["ReadingData"] = 75
    readProgress["TruncatingEnd"] = 90
    readProgress["Decoding"] = 100
        
    def __init__( self, *args, **kwargs ):
    
        if len( args ) == 0:
            imageName = self.defaultImageName
        elif args[0]:
            imageName = args[0]
        else:
            imageName = self.defaultImageName
        
        if self.forceCustomFilenames == True:
            imageName = self.useThisCustomFilename
        self.imageName = imageName
        
        #Extra check to be safe, shouldn't be needed though
        if not self.imageName:
            self.imageName = self.defaultImageName
        
        self.renderViewCheck = checkInputs.capitalLetterCombinations( "Render View" )
        
        self.originalFormat = None
        if "." in self.imageName:
            self.originalFormat = self.imageName.split( "." )[-1]
        
        if ".".join( self.imageName.split( "." )[:-1] ) not in self.renderViewCheck or mayaEnvironment == False:
    
            self.imageName = "{0}.png".format( str( imageName ).replace( "\\", "/" ).rsplit( '.', 1 )[0] )
            
            if "/" not in self.imageName:
                self.imageName = "{0}/{1}".format( self.defaultImageDirectory, self.imageName )
                
            if self.imageName[-1:] == ":":
                self.imageName += "/"
                
            if self.imageName[-1:] == "/":
                self.imageName += self.defaultImageName
        
        self.kwargs = kwargs
        self.printProgress = checkInputs.checkBooleanKwargs( kwargs, True, 'p', 'print', 'printProgress', 'printOutput', 'o', 'output', 'outputProgress' )
        self.cleanTemporaryFiles = checkInputs.checkBooleanKwargs( kwargs, True, 'c', 'cleanFiles', 'tempFiles', 'cleanTempFiles', 'temporaryFiles', 'cleanTemporaryFiles' )
        
        #For updating progress
        if mayaEnvironment == True:
            validArgs = checkInputs.validKwargs( kwargs, 'scrollField', 'scrollFieldToUpdate' )
            self.scrollFieldToUpdate = None
            for i in range( len( validArgs ) ):
                try:
                    py.scrollField( kwargs[validArgs[i]], query = True, text = True )
                    self.scrollFieldToUpdate = kwargs[validArgs[i]]
                    break
                except:
                    pass
                    
            validArgs = checkInputs.validKwargs( kwargs, 'progressBar', 'progressBarName' )
            self.progressBar = None
            for i in range( len( validArgs ) ):
                try:
                    py.progressBar( kwargs[validArgs[i]], query = True, progress = True )
                    self.progressBar = kwargs[validArgs[i]]
                    break
                except:
                    pass
                    
            validArgs = checkInputs.validKwargs( kwargs, 'progressBarText' )
            self.progressBarText = None
            for i in range( len( validArgs ) ):
                try:
                    py.text( kwargs[validArgs[i]], query = True, label = True )
                    self.progressBarText = kwargs[validArgs[i]]
                    break
                except:
                    pass
                    
            validArgs = checkInputs.validKwargs( kwargs, 'callbackWrite', 'callbackWriteCommand', 'deferredWrite', 'deferredWriteCommand' )
            self.callbackWrite = None
            for i in range( len( validArgs ) ):
                try:
                    if inspect.ismethod( kwargs[validArgs[i]] ):
                        self.callbackWrite = kwargs[validArgs[i]]
                        break
                except:
                    pass
                
        
        
        
    def getImageLocation( self, input ):
        
        if mayaEnvironment == True and input in self.renderViewCheck:
            self.renderView( True )
            imageLocation = self.renderViewSaveLocation
            self.originalFormat = self.imageFormats()[0][py.getAttr( "defaultRenderGlobals.imageFormat" )][0]
            
        else:
            imageLocation = input
        
        if self.readImage( imageLocation ):
            return imageLocation
        else:
            return None
    
    def updateMayaUI( self, text, display, percentComplete ):
    
        if self.progressBar:
            if not percentComplete:
                percentComplete = py.progressBar( self.progressBar, query = True, progress = True )
            py.progressBar( self.progressBar, edit = True, progress = percentComplete )
            
        if display:
        
            if self.progressBarText:
                py.text( self.progressBarText, edit = True, label = text )
                
            if self.scrollFieldToUpdate:
                currentText = py.scrollField( self.scrollFieldToUpdate, query = True, text = True )
                currentText = "{0}{1}{2}".format( text, GlobalValues.newLine, currentText )
                py.scrollField( self.scrollFieldToUpdate, edit = True, text = currentText )
    
    def printCurrentProgress( self, text, display = True, percentComplete = None ):
    
        if not self.validateWrite:
            if mayaEnvironment == True:
                
                #utils.executeDeferred( self.updateMayaUI, text, display, percentComplete )
                self.updateMayaUI( text, display, percentComplete )
                
            if self.printProgress == True:
                print text
                    
    
    def cleanTempFiles( self ):
        if self.cleanTemporaryFiles == True:
            self.renderView( False )

    def write( self, *args, **kwargs ):
        
        if mayaEnvironment == True:
            if self.progressBarText:
                py.text( self.progressBarText, edit = True, label = "Setting up variables..." )
            if self.progressBar:
                py.progressBar( self.progressBar, edit = True, progress = 0 )
        results = self.actualWrite( *args, **kwargs )
        self.cleanTempFiles()
        
        return results

    def read( self, *args, **kwargs ):
        
        if mayaEnvironment == True:
            try:
                if not self.validateWrite:
                    py.progressBar( self.progressBar, edit = True, progress = 0 )
            except:
                pass
        results = self.actualRead( *args, **kwargs )
        self.cleanTempFiles()
        
        return results
        
    def actualWrite( self, *args, **kwargs ):
    
        #self.printCurrentProgress( "Setting up variables...", True, 0 )
    
        input = None
        if len( args ) > 0:
            input = args[0]
        else:
            validArgs = checkInputs.validKwargs( kwargs, 'input', 'inputData' )
            for i in range( len( validArgs ) ):
                try:
                    input = kwargs[validArgs[i]]
                    if len( input ) > 0:
                        break
                except:
                    pass
                    
        #If image should be uploaded
        upload = checkInputs.checkBooleanKwargs( kwargs, False, 'u', 'upload', 'uploadImage' )
        if overrideUpload == True:
            upload = False
        elif self.forceUpload == True:
            upload = self.shouldUpload
        
        openImage = checkInputs.checkBooleanKwargs( kwargs, True, 'o', 'open', 'openImage', 'openUpload', 'openUploaded', 'openUploadImage', 'openUploadedImage' )
        if self.forceOpenOnUpload == True:
            openImage = self.shouldOpenOnUpload
        
        #If information should be disabled from being displayed
        disableInfo = checkInputs.checkBooleanKwargs( kwargs, False, 'd', 'disable', 'disableInfo', 'disableInformation' )
        
        #If custom image data should be returned but nothing else
        returnCustomImageInfoPrefix = ["get", "return", "calculate", "test"]
        returnCustomImageInfoMiddle = ["", "Custom" ]
        returnCustomImageInfoMiddle2 = ["", "Image"]
        returnCustomImageInfoSuffix = ["Info", "Information", "Size"]
        returnCustomImageInfoJoined = checkInputs.joinList( returnCustomImageInfoPrefix, returnCustomImageInfoMiddle, returnCustomImageInfoMiddle2, returnCustomImageInfoSuffix )
        returnCustomImageInfo = checkInputs.checkBooleanKwargs( kwargs, False, *returnCustomImageInfoJoined )
        
        #Final validation to read image that has just been created
        validateOutput = checkInputs.checkBooleanKwargs( kwargs, False, 'v', 'cO', 'vO', 'validate', 'verify', 'verifyOutput', 'checkOutput', 'validateOutput', 'checkImage', 'validateImage', 'verifyImage' )
        
        #Delete file after creation
        deleteImage = checkInputs.checkBooleanKwargs( kwargs, False, 'dI', 'deleteImage', 'removeImage', 'disableSaving', 'noSave', 'noSaving', 'uploadOnly' )
        if self.forceDeleteFile == True:
            deleteImage = self.shouldDeleteFile
        
        #Output all input data as black to debug
        debugData = checkInputs.checkBooleanKwargs( kwargs, False, 'debug', 'debugData', 'debugResult', 'debugOutput' )
        if debugData == True:
            padWithRandomData = False
        else:
            padWithRandomData = True
        
        #If a link to the custom image should be returned
        returnCustomImageURL = checkInputs.checkBooleanKwargs( kwargs, False, 'returnURL', 'returnCustomURL', 'returnCustomImageURL' )
        
        #If it should just output the size of input
        outputSizePrefix = ["return", "test", "get", "calculate"]
        outputSizeMiddle = ["Output", "Input"]
        outputSizeSuffix = ["Size"]
        outputSizeJoined = checkInputs.joinList( outputSizePrefix+[""], outputSizeMiddle+[""], outputSizeSuffix )
        outputSizeJoined += checkInputs.joinList( outputSizePrefix, outputSizeMiddle, outputSizeSuffix+[""] )
        outputSizeJoined += checkInputs.joinList( outputSizePrefix, outputSizeSuffix, ["OfInput"] )
        outputSizeJoined = tuple( set( [self.lowercase( word ) for word in outputSizeJoined + ( "s", "iS", "oS" ) if len( word ) > 0] ) )
        outputSize = checkInputs.checkBooleanKwargs( kwargs, False, *outputSizeJoined )
        
        #Write image information to cache, can speed up code execution by a lot
        writeToINI = checkInputs.checkBooleanKwargs( kwargs, True, 'DB', 'INI', 'cache', 'writeDB', 'writeINI', 'writeCache', 'writeToDB', 'writeDatabase', 'writeToCache', 'writeToINI', 'writeToDatabase' )
        if self.forceCacheWrite == True:
            writeToINI = self.shouldWriteCache
        
        #If the custom image option should be dynamically disabled or the code stopped
        revertToDefault = checkInputs.checkBooleanKwargs( kwargs, True, 'revert', 'revertToBasic', 'revertToDefault', 'revertToDefaultImage', 'revertToDefaultStyle' )
        
        #If all URLs should be reuploaded to Imgur
        uploadURLsToImgur = checkInputs.checkBooleanKwargs( kwargs, True, 'uploadURLToImgur', 'uploadURLSToImgur', 'uploadCustomURLToImgur', 'uploadCustomURLsToImgur' )
        
        #[Maya only - not working correctly] Write image to render view, but loses data when it's written so don't use it
        writeToRenderView = checkInputs.checkBooleanKwargs( kwargs, False, 'rV', 'renderView', 'writeRV', 'writeRenderView', 'writeToRV', 'writeToRenderView' )
        
        #Cutoff mode help
        cutoffModeHelp = checkInputs.checkBooleanKwargs( kwargs, False, 'cH', 'cMH', 'cHelp', 'cMHelp', 'cutoffHelp', 'cutoffModeHelp' )
        if cutoffModeHelp == True:
            print "Cutoff modes:"
            print "These define if the values should be added or subtracted based on the value of the pixel."
            print "0: Move towards 0"
            print "1: Move towards 64"
            print "2: Move towards 128"
            print "3: Move towards 192"
            print "4: Move towards 255"
            print "5: Move away from 64"
            print "6: Move away from 128"
            print "7: Move away from 192"
            return None
        
        #Ratio of width to height
        validArgs = checkInputs.validKwargs( kwargs, 'r', 'ratio', 'sizeRatio', 'widthRatio', 'heightRatio', 'widthToHeightRatio' )
        ratioWidth = math.log( 1920 ) / math.log( 1920*1080 )
        
        for i in range( len( validArgs ) ):
        
            try:
                if 0 < float( str( kwargs[validArgs[i]] ) ) < 1:
                    ratioWidth = float( str( kwargs[validArgs[i]] ) )
                    break
                    
                else:
                    raise RangeError( "number not in range" )
                    
            except:
                ratioWidth = math.log( 1920 ) / math.log( 1920*1080 )
        
        allOutputs = []
        usedRenderViewImage = False
        usedRenderView = False
        customImageInputPath = ""
        if outputSize == False:
        
            #Check if custom image should be used
            validArgs = checkInputs.validKwargs( kwargs, 'i', 'cI', 'img', 'image', 'URL', 'imgURL', 'imgPath', 'imgLoc', 'imgLocation', 'imageURL', 'imageLoc', 'imagePath', 'imageLocation', 'customImg', 'customURL', 'customImage', 'customImgURL', 'customImageURL', 'customImgPath', 'customImagePath', 'customImgLoc', 'customImageLoc', 'customImgLocation', 'customImageLocation' )
            customImageInput = None
            
            #Force certain custom image
            if self.forceCustomImages == True:
                validArgs = ["forceCustomImages"]
                kwargs["forceCustomImages"] = self.useThisCustomImage
            
            for i in range( len( validArgs ) ):
            
                try:
                    if kwargs[validArgs[i]] == None:
                        validArgs = []
                        break
                    customImageInput = self.readImage( kwargs[validArgs[i]] )
                    if customImageInput != None:
                        customImageInputPath = kwargs[validArgs[i]]
                        break
                    
                    #Read from the Maya Render View window
                    elif mayaEnvironment == True:
                    
                        #Check all combinations of text for render view
                        if kwargs[validArgs[i]] in self.renderViewCheck:
      
                            #Save file
                            self.renderView( True )
                            
                            #Get image details
                            customImageInputPath = self.renderViewSaveLocation
                            customImageInput = self.readImage( self.renderViewSaveLocation )
                            
                            usedRenderView = True
                            if customImageInput != None:
                                usedRenderViewImage = True
                                #returnCustomImageURL = True
                                break
                            else:
                                self.renderView( False )
                        
                except:
                    customImageInput = None
                    
            #Check image file path isn't URL, and set to custom image if it is
            usedFilenameAsCustom = False
            if any( value in self.imageName for value in self.protocols ):
            
                outputText = "Error: Can't use URLs when saving an image."
                
                if customImageInput == None and self.forceCustomImages == False:
                    outputText = outputText.replace( ".", ", using URL as a custom image." )
                    customImageInput = self.readImage( self.imageName )
                
                self.printCurrentProgress( outputText )
                    
                self.imageName = self.defaultImageName
                usedFilenameAsCustom = True
                
            
            if ( len( validArgs ) > 0 or usedFilenameAsCustom == True ) and customImageInput == None:
                self.printCurrentProgress( "Error: Custom image could not be read. Output image will be saved without it." )
            
            if customImageInput == None:
                useCustomImageMethod = False
            else:
                useCustomImageMethod = True
                
                sizeOfImage = customImageInput.size
                #Keep same size ratio if image can't hold all the data
                ratioWidth = math.log( sizeOfImage[0] ) / math.log( sizeOfImage[0]*sizeOfImage[1] )
                
                #Cutoff mode prefix
                validArgs = checkInputs.validKwargs( kwargs, 'cMP', 'cutoffModePrefix', 'cutoffModeName' )
                cutoffModePrefix = "m"
                for i in range( len( validArgs ) ):
                    try:
                        cutoffModePrefix = str( kwargs[validArgs[i]] )
                        break
                    except:
                        pass
            
                #Custom cutoff mode
                validArgs = checkInputs.validKwargs( kwargs, 'cM', 'mode', 'cutoff', 'cutoffMode', 'cutoffModes' )
                customCutoffMode = None
                validCustomCutoffModes = []
                for i in range( len( validArgs ) ):
                    try:
                        if "," in str( kwargs[validArgs[i]] ) or type( kwargs[validArgs[i]] ) == tuple:
                        
                            #If provided as tuple
                            if type( kwargs[validArgs[i]] ) == tuple:
                                customModeList = kwargs[validArgs[i]]
                                        
                            #If provided as string
                            else:
                                customModeList = kwargs[validArgs[i]].replace( "(", "" ).replace( ")", "" ).split( "," )
                                       
                            #Build list of all values
                            for j in range( len( customModeList ) ):
                                try:
                                    customCutoffMode = int( customModeList[j] )
                                    if 0 < customCutoffMode < self.maxCutoffModes+1:
                                        validCustomCutoffModes.append( customCutoffMode )
                                except:
                                    customCutoffMode = None
                                    
                            if len( validCustomCutoffModes ) > 0:
                                break
                            
                        else:
                            customCutoffMode = int( kwargs[validArgs[i]] )
                            if 0 < customCutoffMode < self.maxCutoffModes+1:
                                break
                            else:
                                customCutoffMode = None
                                
                    except:
                        customCutoffMode = None
                
                #Run code on final cutoff number
                if len( validCustomCutoffModes ) > 0:
                    customCutoffMode = validCustomCutoffModes[-1]
                
                #If image should be output with all cutoff modes
                allCutoffModes = checkInputs.checkBooleanKwargs( kwargs, False, 'a', 'all', 'aCM', 'allCutoff', 'allCutoffs', 'allModes', 'allCutoffMode', 'allCutoffModes' )
                
                #Automatically set custom cutoff modes to all and disable reverting to the default method if image can't hold data
                if allCutoffModes == True:
                    validCustomCutoffModes = list( range( self.maxCutoffModes+1 ) )
                    revertToDefault = False
                
                
                #Avoid running code again if it's already recursive
                usingCustomModesAlready = checkInputs.checkBooleanKwargs( kwargs, False, 'usingCustomModesAlready' )
                if usingCustomModesAlready == False:
                
                    validCustomCutoffModes.sort()
                    kwargs["usingCustomModesAlready"] = True
                    
                    #Run code again for each cutoff mode
                    for i in range( len( validCustomCutoffModes )-1 ):
                    
                        kwargs["useThisInstead"] = validCustomCutoffModes[i]
                        
                        newImageName = "{0}.{1}{2}.png".format( self.imageName.replace( ".png", "" ), cutoffModePrefix, validCustomCutoffModes[i] )
                        otherURLS = ImageStore( newImageName, **self.kwargs ).write( input, **kwargs )
                        if otherURLS != None:
                            allOutputs += otherURLS
                    
                    if len( validCustomCutoffModes ) > 1:
                    
                        #Set up name and cutoff mode for final run
                        self.imageName = "{0}.{1}{2}.png".format( self.imageName.replace( ".png", "" ), cutoffModePrefix, validCustomCutoffModes[-1] )
                        customCutoffMode = validCustomCutoffModes[-1]
                    
                else:
                    customCutoffMode = kwargs["useThisInstead"]
            
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
            
            if useCustomImageMethod == True:
                #Find md5 of image
                imageHash = md5.new()
                try:
                    imageHash.update( customImageInput.tostring() )
                except:
                    pass
                imageMD5 = imageHash.hexdigest()
                
                #Open/create text file
                textFileData = {}
                successfulRead = False
                storedImageURL = ""
                
                #This part allows you to skip iterating through every single pixel each time the code is run
                if writeToINI == True:
                    
                    cachePath = self.cache( returnPath = True )
                
                    if os.path.exists( cachePath ):
                        try:
                        
                            textFile = open( cachePath, "r")
                            
                            try:
                            
                                textFileData = self.decodeData( textFile.read(), decode = True )
                                                                    
                                try:
                                
                                    currentImageData = textFileData[imageMD5]
                                    storedCutoffMode = int( currentImageData[0] )
                                    storedValidPixels = currentImageData[1]
                                    storedImageURL = currentImageData[2]
                                    successfulRead = True
                                    
                                except:
                                    pass
                            except:
                                pass
                            textFile.close()
                            
                        except:
                            pass
                            
                        textFile = open( cachePath, "r+")
                    else:
                        textFile = open( cachePath, "w")
                        
                    storedImage = self.readImage( storedImageURL )
                
                
                if successfulRead == True and storedImage != None:
                    
                    customImageInputPath = storedImageURL
                    customImageInput = storedImage
                    
                else:
                    #Upload custom image and switch path to URL
                    uploadCustomImage = checkInputs.checkBooleanKwargs( kwargs, True, 'uI', 'uC', 'uO', 'uCI', 'uploadCustom', 'uploadOriginal', 'uploadCustomImage', 'uploadOriginalImage', 'uploadCustomURL', 'uploadOriginalURL' )
                    if self.forceUpload == True:
                        uploadCustomImage = self.shouldUpload
                    if uploadCustomImage == True and customImageInput != None and overrideUpload != True:
                        
                        #If it should upload any non Imgur URL to Imgur
                        originalImageProtocols = self.protocols
                        if uploadURLsToImgur == True:
                            originalImageProtocols = [str( value ) + "i.imgur" for value in self.protocols]
                        
                        if not any( value in customImageInputPath for value in originalImageProtocols ):
                            
                            self.printCurrentProgress( "Uploading original image..." )
                            
                            uploadedImageURL = self.uploadImage( customImageInputPath, ignoreSize = True )
                            
                            if uploadedImageURL != None:
                                self.printCurrentProgress( "Link to original image is {0}.".format( uploadedImageURL ) )
                                self.stats( uploadedImageURL, False, imageMD5 )
                                    
                                if writeToINI == False:
                                
                                    self.printCurrentProgress( "Set this link as the custom image input to avoid re-uploading the same image each time." )
                                
                                customImageInputPath = str( uploadedImageURL )
                                customImageInput = self.readImage( uploadedImageURL )
                                                                
                            else:
                                self.printCurrentProgress( "Original image URL will not be stored within the image." )
                                
                    elif customImageInput == None:
                        customImageInputPath = ""
                        
        else:
            useCustomImageMethod = False
        
        #Get invalid formats
        renderViewFormat, ignoreFormats, uploadFormats = self.imageFormats()
        formatList = dict( [item for key, item in renderViewFormat.iteritems() if len( item ) == 2] )
        ignoreFormats = dict( [renderViewFormat[index] for index in ignoreFormats] ).keys()
        
        if customImageInputPath:
            customImageExtension = customImageInputPath.split( "." )[-1].lower()
        else:
            customImageExtension = None
        
        if ( customImageExtension in formatList.keys() ) and customImageExtension not in ignoreFormats:
            
            try:
                if mayaEnvironment == True:
                    imageType = renderViewFormat[py.getAttr( "defaultRenderGlobals.imageFormat" )][1]
                else:
                    imageType = formatList[customImageExtension]
            except:
                imageType = customImageExtension.upper()
                                
            if customImageExtension not in ignoreFormats:
            
                #Fix for V-Ray
                if py.getAttr( "defaultRenderGlobals.imageFormat" ) == 52:
                    imageType = "V-Ray " + imageType
                
                self.printCurrentProgress( "Reason: {0} files not supported.".format( imageType ) )
            
            if mayaEnvironment == True and usedRenderView == True:
                self.printCurrentProgress( "Use 'ImageStore().renderView( <format> )' to change the render image format." )
            
            customImageInput = None
            customImageInputPath = ""
            useCustomImageMethod = False
        
        if input and returnCustomImageInfo == False:
            self.printCurrentProgress( "Encoding input data...", True, self.writeProgress["CalculatingInputSize"] )
            
        #Print how large the input data is
        if not input and returnCustomImageInfo == False:
            self.printCurrentProgress( "Error: Input data is required" )
            return None
        
        elif returnCustomImageInfo == False:
        
            
            inputData = self.encodeData( input, binary = useCustomImageMethod )
            lengthOfInputData = len( inputData )
            
            if returnCustomImageInfo == False:
                self.printCurrentProgress( "Input data is {0} bytes ({1}kb)". format( lengthOfInputData+3, ( lengthOfInputData+3 )/1024 ), True, self.writeProgress["InputSizeIs"] )
            
            #Return the normal size of input data
            if outputSize == True:
                return lengthOfInputData+3
        
        #It shouldn't hit this part
        elif outputSize == True:
            print "Error: Unable to output the size of input"
            return None
        
        rawData = []
        if useCustomImageMethod == True:
            
            if returnCustomImageInfo == False:
                self.printCurrentProgress( "Checking image has enough pixels to store the input data.", True, self.writeProgress["CheckingImage"] )
            
            bitsPerPixel = 6
            
            #Get correct range
            cutoffModeAmount = {}
            colourRange = {}
            cutoffModes = range( self.maxCutoffModes+1 )
            invalidCutoffMode = len( cutoffModes )
            
            #Set up valid pixels dictionary
            validPixels = {}
            for i in cutoffModes:
                cutoffModeAmount[i] = 0
                colourRange[i] = self.validRange( i, bitsPerPixel )
                validPixels[i] = {}
            
            #Read valid pixels dictionary from cache
            if successfulRead == True and ( 0 <= storedCutoffMode <= self.maxCutoffModes ):
                validPixels = storedValidPixels
                bestCutoffMode = storedCutoffMode
            else:
                bestCutoffMode = None
                storedCutoffMode = invalidCutoffMode
                
            #Use custom cutoff mode
            if customCutoffMode != None:
                storedCutoffMode = customCutoffMode
                
            if successfulRead == False or len( validPixels[storedCutoffMode] ) == 0 or bestCutoffMode == None:

                #Calculate max data that can be stored
                if storedCutoffMode == invalidCutoffMode:
                    self.printCurrentProgress( "Calculating the best method to store data...", True, self.writeProgress["CheckingImage"] )
                        
                totalPixelCount = 0
                imageDimensions = customImageInput.size
                imageSize = float( imageDimensions[0]*imageDimensions[1] )
                pixelCount = 0
                
                nextTime = time()+self.outputProgressTime
                minPercent = self.writeProgress["CheckingImage"]
                maxPercent = self.writeProgress["CalculatingCutoffMode"]
                if returnCustomImageInfo == True:
                    minPercent = 0
                    maxPercent = 65
                for pixels in customImageInput.getdata():
                    
                    #Output progress
                    if pixelCount % self.outputProgressIterations == 0:
                        if nextTime < time():
                            nextTime = time()+self.outputProgressTime
                            percentCompleted = round( 100 * totalPixelCount / imageSize, 1 )
                            self.printCurrentProgress( " {0}% completed".format( percentCompleted ), False, int( minPercent+( maxPercent - minPercent )/100.0*percentCompleted ) )
                
                        for rgb in range( 3 ):
                            rawData.append( pixels[rgb] )
                            if bestCutoffMode == None:
                                #Count all valid values to find best cutoff mode
                                if totalPixelCount > 0:
                                    for i in cutoffModes:
                                        if pixels[rgb] in colourRange[i][0] or pixels[rgb] in colourRange[i][1]:
                                            cutoffModeAmount[i] += 1
                                    
                    totalPixelCount += 1
                  
                #Select best cutoff mode
                if bestCutoffMode == None:
                    bestCutoffMode = max( cutoffModeAmount.iteritems(), key=operator.itemgetter( 1 ) )[0]
                    cutoffMode = bestCutoffMode
                else:
                    cutoffMode = storedCutoffMode
                
                if not returnCustomImageInfo:
                    self.printCurrentProgress( "Using storing mode {0}.".format( cutoffMode ), True, self.writeProgress["UsingCutoffMode"] )
                self.printCurrentProgress( "Calculating how much data can be stored for different amounts of bits using this mode...", True, self.writeProgress["UsingCutoffMode"] )
                
                #Find maximum size image can store for bits per colour
                nextTime = time()+self.outputProgressTime
                
                pixelCount = 0
                totalCount = float( 8*len( rawData ) )
                bitsPerPixel = 0
                
                minPercent = self.writeProgress["UsingCutoffMode"]
                maxPercent = self.writeProgress["CalculatingMaxImageData"]
                if returnCustomImageInfo:
                    minPercent = 65
                    maxPercent = 100
                for i in range( 8 ):
                                            
                    bitsPerPixel = i+1
                    validPixels[cutoffMode][bitsPerPixel] = 0
                    colourIncreaseRange, colourReduceRange = self.validRange( cutoffMode, bitsPerPixel )
                    
                    for j in range( len( rawData ) ):
                    
                        if rawData[j] in colourIncreaseRange or rawData[j] in colourReduceRange:
                            validPixels[cutoffMode][bitsPerPixel] += 1
                            
                        #Output progress
                        pixelCount += 1
                        if pixelCount % self.outputProgressIterations == 0:
                            if nextTime < time():
                                nextTime = time()+self.outputProgressTime
                                percentCompleted = round( 100 * pixelCount / totalCount, 1 )
                                self.printCurrentProgress( " {0}% completed".format( percentCompleted ), False, int( minPercent+(maxPercent - minPercent)/100.0*percentCompleted ) )
                        
            else:
            
                self.printCurrentProgress( "File information read from cache.", True, self.writeProgress["CalculatingMaxImageData"] )
                    
                #Store custom image information
                for pixels in customImageInput.getdata():
                    for rgb in range( 3 ):
                        rawData.append( pixels[rgb] )
                        
                #Get stored values
                cutoffMode = storedCutoffMode
                if customCutoffMode != None:
                    cutoffMode = customCutoffMode
                validPixels = storedValidPixels
                
                self.printCurrentProgress( "Using storing mode {0}.".format( cutoffMode ), True, self.writeProgress["ImageCanStore"] )
            
            validPixelsTotal = [number*bits for number, bits in validPixels[cutoffMode].iteritems()]
            bitsPerPixelMax = validPixelsTotal.index( max( validPixelsTotal ) )+1
            
            #Write to ini file
            if writeToINI == True:
                textFileData[imageMD5] = [bestCutoffMode, validPixels, customImageInputPath]
                textFile.write( self.encodeData( textFileData, encode = True ) )
                textFile.close()
            
            #Get maximum bytes per bits
            imageBytes = validPixels[cutoffMode][ bitsPerPixelMax ]
            imageCanStorePercent = self.writeProgress["ImageCanStore"]
            if returnCustomImageInfo:
                imageCanStorePercent = 100
            self.printCurrentProgress( "Image can store up to around {0} bytes ({1}kb)".format( imageBytes, imageBytes/1024 ), True, imageCanStorePercent )
            
            if returnCustomImageInfo == False:
                inputBytes = ( len( inputData )*8 )/bitsPerPixelMax+3
                outputText = "Input data at this level is {0} bytes ({1}kb)".format( inputBytes, inputBytes/1024 )
            
                if inputBytes > imageBytes:
                    outputText += ", which is currently more than the image can hold."
                    self.printCurrentProgress( outputText, True, self.writeProgress["InputAtMax"] )
                    outputText = "Attempting to find a valid value by calculating the other levels.".format( GlobalValues.newLine )
                    
                else:
                    self.printCurrentProgress( outputText, True, self.writeProgress["InputAtMax"] )
                    outputText = "Now attempting to find the minumum valid value to store the data."
                
                self.printCurrentProgress( outputText, True, self.writeProgress["InputAtMax"] )
            
            #Stop here if image information is wanted
            if returnCustomImageInfo == True:
                return imageBytes
                
            #Calculate minimum bits per pixel to use
            #Higher does not necessarily mean more, 6 bits seems to be the most efficient one
            bitsPerPixel = 1
            bytesNeeded = ( lengthOfInputData*8 )/bitsPerPixel+3 #Avoids having to actually split the input data
            
            minPercent = self.writeProgress["InputAtMax"]
            maxPercent = self.writeProgress["MinimumBitsPerPixel"]
            while validPixels[cutoffMode][bitsPerPixel] < bytesNeeded:
            
                if bitsPerPixel > 7:
                    
                    outputText = "Error: Image not big enough to store data."
                        
                    #Stop code here if reverting to default isn't an option
                    if revertToDefault == False:
                        self.printCurrentProgress( outputText, True, maxPercent )
                        return None
                    else:
                        outputText += " Disabling the custom image option."
                        self.printCurrentProgress( outputText, True, int( minPercent+(maxPercent-minPercent)/100.0*(bitsPerPixel+1)/8.0  ) )
                    
                    useCustomImageMethod = False
                    inputData = self.encodeData( input, binary = useCustomImageMethod )
                    
                    break
                    
                bitsPerPixel += 1
                bytesNeeded = ( lengthOfInputData*8 )/bitsPerPixel+3
            
            
            #Continue if valid, if not pass through
            if bitsPerPixel < 8:
                if bitsPerPixel > 1:
                    self.printCurrentProgress( "Increased to {0} bits of colour to fit data within the image.".format( bitsPerPixel ), True, self.writeProgress["ChooseBitsPerPixel"] )
                else:
                    self.printCurrentProgress( "Using 1 bit of colour to fit data within the image.", True, self.writeProgress["ChooseBitsPerPixel"] )
    
                #Encode input data
                self.printCurrentProgress( "Splitting input data into separate pixel values...", True, self.writeProgress["ChooseBitsPerPixel"] )
                joinedData = "".join( inputData )
                splitData = re.findall( r".{1," + str( bitsPerPixel ) + "}", joinedData, re.DOTALL )
                colourIncreaseRange, colourReduceRange = self.validRange( cutoffMode, bitsPerPixel )
                numbersToAdd = [ int( num, 2 ) for num in splitData ]
                
                #Draw image
                width, height = customImageInput.size
        
        if useCustomImageMethod == False:
            
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
    
            self.printCurrentProgress( "Set width to {0} pixels and height to {1} pixels.".format( width, height ), True, self.writeProgress["SetDimensions"] )
        
        #Draw image
        imageOutput = Image.new("RGB", ( width, height ) )
        imageData = imageOutput.load()
    
        #Set range of colours for random filling
        numbersToAddIncrement = 0
        if padWithRandomData == True:
        
            if useCustomImageMethod == True:
                maxImageAddition = pow( 2, bitsPerPixel )+bitsPerPixel-8
                minImageAddition = 0
                
                #Fix for if it goes under 1
                if maxImageAddition < 1:
                    maxImageAddition = pow( 2, bitsPerPixel )
                
            else:
                maxImageAddition = 128
                minImageAddition = 52
                
        else:
            maxImageAddition = 255
            minImageAddition = 255
        
        #Assign pixel colours
        self.printCurrentProgress( "Calculating image...", True, self.writeProgress["SetDimensions"] )
        nextTime = time()+self.outputProgressTime
        minPercent = self.writeProgress["SetDimensions"]
        maxPercent = self.writeProgress["CalculatingImage"]
        for y in range( height ):
            for x in range( width ):
                
                isDataFromInput = True
                currentProgress = 3*( y*width+x )
                
                #Output progress
                if y*width+x % self.outputProgressIterations == 0:
                    if nextTime < time():
                        nextTime = time()+self.outputProgressTime
                        percentCompleted = round( 100*( currentProgress/3 )/( width*height ), 1 )
                        self.printCurrentProgress( " {0}% completed".format( percentCompleted ), True, int( minPercent+(maxPercent - minPercent)/100.0*percentCompleted ) )

                
                #Assign information to first pixel
                if x == 0 and y == 0:
                    inputInfo = int( str( bitsPerPixel ) + str( cutoffMode ) )
                    dataRGB = [inputInfo, self.firstPixelPadding[0], self.firstPixelPadding[1]]
                    if debugData == True:
                        dataRGB = [99, self.firstPixelPadding[0], self.firstPixelPadding[1]]
                        imageData[x,y] = tuple( dataRGB )
                        continue
                
                #If an image should be made with the default method
                elif useCustomImageMethod == False:
                        
                    dataRGB = {} 
                    try:
                        for i in range( 3 ):
                            dataRGB[i] = inputData[numbersToAddIncrement]
                            numbersToAddIncrement += 1
                    except:
                    
                        if isDataFromInput == True:
                            isDataFromInput = False
                        
                        #Add random data
                        for i in range( 3 ):
                            dataRGB[i] = randint( minImageAddition, maxImageAddition )
                    
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
                    
                        if isDataFromInput == True:
                            isDataFromInput = False
                        
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
                
                if debugData == True and isDataFromInput == True:
                    dataRGB = [0,0,0]
                    
                imageData[x,y] = tuple( dataRGB )
        
        self.printCurrentProgress( "Saving image...", True, self.writeProgress["SavingImage"] )
        
        try:
            imageOutput.save( self.imageName, "PNG" )
            
        except:
        
            failText = ["Error: Failed saving file to {0}.".format( self.imageName )]
            failText.append( "You may have incorrect permissions or the file may be in use." )
            failText.append( "{0}Attempting to save in new location...".format( GlobalValues.newLine ) )
            self.printCurrentProgress( " ".join( failText ) )
            savingFailed = "{0}Failed to save file.".format( GlobalValues.newLine )
            
            #If already in default directory
            if self.imageName.rsplit( '/', 1 )[0] == self.defaultImageDirectory:
            
                if self.imageName.rsplit( '/', 1 )[1] == self.defaultImageName:
                    self.imageName = None
                    failText = savingFailed
                    
                else:
                
                    try:
                        self.imageName = "{0}/{1}".format( self.defaultImageDirectory, self.defaultImageName )
                        imageOutput.save( self.imageName, "PNG" )
                        failText = None
                        
                    except:
                        self.imageName = None
                        failText = savingFailed
            
            #If not in default directory
            else:
            
                try:
                    self.imageName = "{0}/{1}".format( self.defaultImageDirectory, self.imageName.rsplit( '/', 1 )[1] )
                    imageOutput.save( self.imageName, "PNG" )
                    failText = None
                    
                except:
                
                    try:
                        self.imageName = "{0}/{1}".format( self.defaultImageDirectory, self.defaultImageName )
                        imageOutput.save( self.imageName, "PNG" )
                        failText = None
                        
                    except:
                        failText = savingFailed
                        self.imageName = None
        
        
        #Make sure image exists first
        if self.imageName != None:
            
            #Find md5 of image
            imageHash = md5.new()
            try:
                imageHash.update( self.readImage( self.imageName ).tostring() )
            except:
                pass
            imageMD5 = imageHash.hexdigest()
            
            self.printCurrentProgress( "Saved image.", True, self.writeProgress["WritingExtraInformation"] )
            
            outputList = [( self.imageName ).replace( "\\", "/" )]
            
            #Zip extra information inside image
            self.printCurrentProgress( "Writing extra information into image file.", True, self.writeProgress["WritingExtraInformation"] )
                
            infoText = ["Date created: {0}{1}".format( self.dateFormat( time() ), GlobalValues.newLine )]
            try:
                infoText = ["Username: {0}{1}".format( getpass.getuser(), GlobalValues.newLine )] + infoText
            except:
                pass
            infoText.append( "Visit {0} to get a working version of the code.".format( self.website ) )
            
            #Write to zip file
            if disableInfo == False:
                ImageStoreZip.write( "".join( infoText ), "information.txt", reset = True )
                ImageStoreZip.write( str( getpass.getuser() ) + "@" + str( time() ), "creationtime" )
                ImageStoreZip.write( customImageInputPath, "url" )
            else:
                ImageStoreZip.write( infoText[-1], "information.txt", reset = True )
            ImageStoreZip.write( str( self.versionNumber ), "version" )
            
            zipSuccess = ImageStoreZip.combine( image = self.imageName )
            
            if zipSuccess == False:
                self.printCurrentProgress( "Error: Unable to write extra information." )
            
            #Upload image
            uploadedImageURL = None
            if upload == True and overrideUpload != True:
                self.printCurrentProgress( "Uploading image..." )
                    
                uploadedImageURL = self.uploadImage( self.imageName, openImage )
                if uploadedImageURL != None:
                    outputList.append( str( uploadedImageURL ) )
                    
            self.printCurrentProgress( "Done.", False, self.writeProgress["Validate"] )
            
            
            #Check the output
            self.validateWrite = True
            if validateOutput == True:
                
                self.printCurrentProgress( "Validating saved image...", True, self.writeProgress["Validate"] )
            
                #Stop reading printing anything
                    
                try:
                    if self.read() != input:
                    
                        raise ImageStoreError( "data failed to validate" )
                        
                    else:
                    
                        self.validateWrite = False
                        self.printCurrentProgress( "Successfully validated the data.", True, self.writeProgress["Validate"] )
                        
                except:
                
                    self.validateWrite = False
                    self.printCurrentProgress( "Error: Failed to validate the data. Please try again." )
                    return None
            
            
            #Write to render view window for Maya
            if mayaEnvironment == True:
                if writeToRenderView == True:
                    try:
                        py.renderWindowEditor( 'renderView', edit = True, loadImage = self.imageName )
                    except:
                        self.printCurrentProgress( "Error: Failed to write image into the renderView window." )
            
            #Remove the image
            if deleteImage == True:
                try:
                    os.remove( self.imageName )
                    outputList.pop( 0 )
                except:
                    pass
                if len( outputList ) == 0:
                    return None
            
            self.stats( uploadedImageURL, lengthOfInputData+3, imageMD5 )
            
            returningCustomURL = False
            if returnCustomImageURL == True and any( value in customImageInputPath for value in self.protocols ):
                outputList.append( customImageInputPath )
                returningCustomURL = True
            
            #Return output
            allOutputs += [outputList]
            
            returnValue = allOutputs
            
        else:
            returnValue = None
        
        if mayaEnvironment == True:
            if self.callbackWrite:
                self.callbackWrite( returnValue, returningCustomURL )
        return returnValue


    def actualRead( self, *args, **kwargs ):
    
        useCustomImageMethod = False
        debugDataDefaultAmount = 100 #How many characters to display by default
        
        #If it should just debug the data
        validArgs = checkInputs.validKwargs( kwargs, 'debug', 'debugData', 'debugResult', 'debugOutput' )
        debugData = False
        for i in range( len( validArgs ) ):
            try:
                if kwargs[validArgs[i]] == True:
                    debugData = debugDataDefaultAmount
                    break
                elif 0 < int( kwargs[validArgs[i]] ):
                    debugData = int( kwargs[validArgs[i]] )
            except:
                debugData = False
        if debugData == False and self.debugging == True:
            debugData = debugDataDefaultAmount

        #Read renderView window in Maya      
        if mayaEnvironment == True:
            if self.imageName in self.renderViewCheck:
                self.renderView( True )
                try:
                    originalMayaFormat = py.getAttr( "defaultRenderGlobals.imageFormat" )
                    py.setAttr( "defaultRenderGlobals.imageFormat", 32 )
                except:
                    pass
                self.imageName = self.renderViewSaveLocation
                try:
                    py.setAttr( "defaultRenderGlobals.imageFormat", originalMayaFormat )
                except:
                    pass
        
        #Get image, try from args first then use the main image location value
        #Avoids the default location overriding the args value
        self.printCurrentProgress( "Reading image...", True, self.readProgress["ReadingImage"] )
        useArgsForImageRead = True
        try:
            if len( args ) > 0 and useArgsForImageRead == True:
                imageInput = self.readImage( args[0] )
                self.imageName = args[0]
            else:
                imageInput = None
            if imageInput == None:
                raise ImageStoreError()
                
        except:
            imageInput = self.readImage( self.imageName )
            
        if imageInput == None:
            self.printCurrentProgress( "Error: Unable to read image." )
            return None
            
        #Output stored zip information
        outputInfo = checkInputs.checkBooleanKwargs( kwargs, debugData, 'o', 'output', 'outputInfo', 'outputInformation' )
        
        try:
            self.printCurrentProgress( "Reading files in image...", True, self.readProgress["ReadingFiles"] )
            originalVersionNumber, originalCreationTime, originalCreationName, customImageURL, fileList = ImageStoreZip.read( imageLocation = self.imageName )
            if debugData != False:
                self.printCurrentProgress( "Files stored in image: {0}".format( ", ".join( fileList ) ), True, self.readProgress["FilesStored"] )
        
        except:
            outputInfo = False
            customImageURL = ""
            
        if outputInfo == True:
            if originalVersionNumber != None:
                self.printCurrentProgress( "Version number: {0}".format( originalVersionNumber ), True, self.readProgress["FilesStored"] )
            if originalCreationTime != None:
                self.printCurrentProgress( "Date created: {0}".format( self.dateFormat( originalCreationTime ) ), True, readProgress["FilesStored"] )
        
        self.printCurrentProgress( "Storing the pixel data...", True )
        #Store pixel info
        rawData = []
        for pixels in imageInput.getdata():
            for rgb in range( 3 ):
                rawData.append( pixels[rgb] )
        
        #Get important image info
        if len( str( rawData[0] ) ) > 1 and rawData[1] == self.firstPixelPadding[0] and rawData[2] == self.firstPixelPadding[1]:
            imageInfo = [int( num ) for num in list( str( rawData[0] ) )]
            bitsPerPixel = imageInfo[0]
            cutoffMode = imageInfo[1]
            
        else:
            self.printCurrentProgress( "Error: Invalid image." )
            return None
        
        if debugData != False:
            self.printCurrentProgress( "Bits per pixel: {0}".format( bitsPerPixel ), True, self.readProgress["FirstPixel"] )
            self.printCurrentProgress( "Cutoff mode: {0}".format( cutoffMode ), True, self.readProgress["FirstPixel"] )
        
        #Find how the image was made
        if bitsPerPixel == 9 and cutoffMode == 9:
            self.printCurrentProgress( "Error: Image had debug data set to true. Unable to read." )
            return None
            
        elif len( imageInfo ) > 2:
            outputText = "Stored data {0}."
            if str( originalVersionNumber ) != str( self.versionNumber ):
                outputText.format( "is from an older version {0}" )
            else:
                outputText.format( "appears to be invalid {0} anyway" )
            outputText.format( ", attempting to continue." )
            self.printCurrentProgress( outputText )
            useCustomImageMethod = False
        
        elif bitsPerPixel == 8:
            useCustomImageMethod = False
        else:
            useCustomImageMethod = True
            
        usedDifferentOriginalImage = False
        if useCustomImageMethod == True:
        
            
            #Use other custom image
            validArgs = checkInputs.validKwargs( kwargs, 'i', 'cI', 'img', 'image', 'URL', 'imgURL', 'imgPath', 'imgLoc', 'imgLocation', 'imageURL', 'imageLoc', 'imagePath', 'imageLocation', 'customImg', 'customImage', 'customImgURL', 'customImageURL', 'customImgPath', 'customImagePath', 'customImgLoc', 'customImageLoc', 'customImgLocation', 'customImageLocation' )
            originalImage = None
            for i in range( len( validArgs ) ):
                try:
                    originalImage = self.readImage( kwargs[validArgs[i]] )
                except:
                    originalImage = None
                        
            if len( validArgs ) > 0 and originalImage == None:
            
                outputText = "Error: Could not read the custom input image."
                if len( customImageURL ) > 0:
                    outputText.replace( ".", ", reverting to the stored URL." )
                self.printCurrentProgress( outputText )
                    
                originalImage = self.readImage( customImageURL )
                
            elif originalImage == None:
                originalImage = self.readImage( customImageURL )
                
            else:
                usedDifferentOriginalImage = True
            
            #If both attempts haven't worked
            if originalImage == None:
                if len( customImageURL ) > 0:
                    self.printCurrentProgress( "Error: Invalid custom image." )
                else:
                    self.printCurrentProgress( "Error: Something has gone wrong." )
                        
                return None
                
            self.printCurrentProgress( "Storing the custom image pixel data", True, self.readProgress["FirstPixel"] )
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
            self.printCurrentProgress( "Retrieving data from image...", True, self.readProgress["StoringCustomPixelInfo"] )
            nextTime = time()+self.outputProgressTime
            totalPixels = len( originalImageData )
            minPercent = self.readProgress["StoringCustomPixelInfo"]
            maxPercent = self.readProgress["ReadingData"]
            for i in range( 3, totalPixels ):
                
                #Output progress
                if i % self.outputProgressIterations == 0:
                    if nextTime < time():
                        nextTime = time()+self.outputProgressTime
                        percentCompleted = round( 100 * i / totalPixels, 1 )
                        self.printCurrentProgress( " {0}% completed".format( percentCompleted ), False, int( minPercent+(maxPercent - minPercent)/100.0*percentCompleted ) )
                        
            
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
        self.printCurrentProgress( "Removing excess data from end of file...", True, self.readProgress["ReadingData"] )
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
            self.printCurrentProgress( "Error: File is corrupted." )
        
        try:
        
            self.printCurrentProgress( "Decoding data...", True, self.readProgress["TruncatingEnd"] )
            decodedData = self.decodeData( numberData )
            
        except:
        
            if usedDifferentOriginalImage == True:
                self.printCurrentProgress( "Failed to decode data, the custom original image specified may not be the original one used." )
                
                if len( customImageURL ) > 0:
                    self.printCurrentProgress( "Failed to decode data, however here is a URL to the correct image contained within the file." )
                    self.printCurrentProgress( "If you are using the original image stored on your computer, it may have resized after being uploaded to Imgur." )
                
                else:
                    self.printCurrentProgress( "No URL was found stored in the image, you may have linked to the wrong image." )
            
            elif len( customImageURL ) > 0:
                self.printCurrentProgress( "Failed to decode data from the stored URL ({0}), check the image still exists.".format( customImageURL ) )
            
            else:
                self.printCurrentProgress( "Failed to decode data from the image." )
                    
            decodedData = None
        
        if debugData != False and decodedData != None:
            self.printCurrentProgress( "Length of stored data: {0}".format( len( decodedData ) ) )
            self.printCurrentProgress( "Type of data: {0}".format( str( type( decodedData ) ).replace( "<type '", "" ).replace( "'>", "" ) ) )
            self.printCurrentProgress( "Writing data to user interface...", True )
            if len( str( decodedData ) ) > debugData:
                self.printCurrentProgress( "First {0} characters of data: {1}".format( debugData, str( decodedData )[0:debugData] ), False )
            else:
                self.printCurrentProgress( "Stored data: {0}".format( decodedData ), False )
                
            self.printCurrentProgress( "Successfully decoded the image.", True, self.readProgress["Decoding"] )
            
        return decodedData

    def decodeData( self, numberData, **kwargs ):
        
        #Only decode the data without converting numbers into characters
        if checkInputs.checkBooleanKwargs( kwargs, False, 'd', 'decode', 'decodeOnly' ) == True:
            encodedData = numberData
        
        #Convert numbers into characters
        else:
            encodedData = "".join( [chr( pixel ) for pixel in numberData] )
        outputData = cPickle.loads( zlib.decompress( base64.b64decode( encodedData ) ) )
        
        return outputData
    
    def encodeData( self, input, **kwargs ):
        
        encodedData = base64.b64encode( zlib.compress( cPickle.dumps( input ) ) )
        if checkInputs.checkBooleanKwargs( kwargs, False, 'e', 'encode', 'encodeOnly' ) == True:
            return encodedData
        
        #Format into numbers
        pixelData = [int( format( ord( letter ) ) ) for letter in encodedData]
        pixelData += self.imageDataPadding
        
        #Pad to end with multiple of 3
        for i in range( 3-len( pixelData )%3 ):
            pixelData += [randint( 52, 128 )]
        
        #Get binary info
        binary = checkInputs.checkBooleanKwargs( kwargs, False, 'b', 'binary', 'useCustomImageMethod' )
        if binary == True:
            pixelData = [ format( number, "b" ).zfill( 8 ) for number in pixelData ]
            
        return pixelData      

        
    #This is my only way of finding the stats as imgur doesn't say, this won't be available to view anywhere
    #However, if you are against this, just disable the urllib2.urlopen() command
    def stats( self, imageURL, numBytes, imageMD5 ):
    
        #Check if md5 value is valid
        if md5.new().hexdigest() == imageMD5:
            imageMD5 = "".join("0" for x in range( 32 ))
            return #No point storing it currently, means something has gone wrong or something
            
        #Set user agent and URL
        userAgent = "ImageStore/" + str( self.versionNumber )
        siteAddress = "{0}/code/imagestore?url={1}&b={2}&m={3}".format( self.website, imageURL, int( numBytes ), imageMD5 )
        
        #Send a request to the website
        try:
            if self.debugging != True:
                urllib2.urlopen( urllib2.Request( siteAddress, headers = { 'User-Agent': userAgent } ) )
        except:
            pass
        
        
    def uploadImage( self, imageLocation, openImage = False, **kwargs ):
        
        ignoreSize = checkInputs.checkBooleanKwargs( kwargs, False, 'i', 'iS', 'ignoreSize' )
        imageTitle = "Image Data"
        
        #Get valid formats to upload
        renderViewFormat, ignoreFormats, uploadFormats = self.imageFormats()
        validFormats = dict( [renderViewFormat[int( index )] for index in uploadFormats] )
        allFormats = dict( [value for key, value in renderViewFormat.iteritems() if len( value ) == 2] )
        
        if self.validPath( imageLocation ) == True and overrideUpload != True:
        
            #Check format is valid
            fileExtension = imageLocation.split( "." )[-1].lower()
            
            if fileExtension == "gif":
                return None
            
            if fileExtension not in validFormats.keys():
                    
                if fileExtension in allFormats.keys():
                    fileExtension = allFormats[fileExtension]
                else:
                    fileExtension = fileExtension.upper()
                self.printCurrentProgress( "Error: {0} files not supported by Imgur.".format( fileExtension ) )
                
                return None
        
            #Save if from a URL
            saved = False
            if any( value in imageLocation for value in self.protocols ):
            
                try:
                    inputImage = Image.open( cStringIO.StringIO( urllib2.urlopen( imageLocation ).read() ) )
                    imageFormat = str( inputImage.format )
                    imageSaveLocation = "{0}/{1}.{2}".format( self.defaultCacheDirectory, self.defaultCacheName, imageFormat.lower() ).replace( ".cache", "" )
                    inputImage.save( imageSaveLocation, imageFormat ) 
                    imageLocation = imageSaveLocation
                    saved = True
                    
                except:
                    pass
                
            #Upload image
            try:
                uploadedImage = pyimgur.Imgur( "0d10882abf66dec" ).upload_image( imageLocation, title=imageTitle )
            
            except:
                self.printCurrentProgress( "Error: Failed uploading image, trying once more." )
                    
                #Once it didn't upload the first time, no idea why, but I guess this just makes sure your internet didn't temporarily cut out
                try:
                    uploadedImage = pyimgur.Imgur( "0d10882abf66dec" ).upload_image( imageLocation, title=imageTitle )
                
                except:
                    self.printCurrentProgress( "Failed to upload image." )
                    return None
            
            #Find out image size
            originalImageSize = os.path.getsize( imageLocation )
            uploadedImageSize = uploadedImage.size
            
            #Check it's not been converted, not needed if it's acting as the original image
            if originalImageSize != uploadedImageSize and ignoreSize == False:
            
                self.printCurrentProgress( "Error: File is too large for Imgur." )
                return None
                
            else:
            
                #Open image in browser
                if openImage == True:
                    webbrowser.open( uploadedImage.link )
                                
                #Return the link
                return uploadedImage.link

            if saved == True:
            
                try:
                    os.remove( imageSaveLocation )
                    
                except:
                    pass
        
        else:
            return None
    

    def imageFormats( self ):
    
        #Use True to exclude from any lists to avoid overlaps of the same extension
        renderViewFormat = {}
        renderViewFormat[0] = ["gif", "GIF"]
        renderViewFormat[1] = ["pic", "SoftImage"]
        renderViewFormat[2] = ["rla", "Wavefront"]
        renderViewFormat[3] = ["tif", "Tiff"]
        renderViewFormat[4] = ["tif", "Tiff16", True]
        renderViewFormat[5] = ["sgi", "SGI"]
        renderViewFormat[6] = ["als", "Alias PIX"]
        renderViewFormat[7] = ["iff", "Maya IFF"]
        renderViewFormat[8] = ["jpg", "JPEG"]
        renderViewFormat[9] = ["eps", "EPS"]
        renderViewFormat[10] = ["iff", "Maya16 IFF", True]
        renderViewFormat[11] = ["cin", "Cineon"]
        renderViewFormat[12] = ["yuv", "Quantel PAL"]
        renderViewFormat[13] = ["sgi", "SGI16", True]
        renderViewFormat[19] = ["tga", "Targa"]
        renderViewFormat[20] = ["bmp", "Windows Bitmap"]
        renderViewFormat[23] = ["avi", "AVI"]
        renderViewFormat[31] = ["psd", "Photoshop Document"]
        renderViewFormat[32] = ["png", "PNG"]
        renderViewFormat[35] = ["dds", "DirectDraw Surface"]
        renderViewFormat[36] = ["psd", "PSD Layered", True]
        renderViewFormat[51] = ["mr", "Mental Ray", True] #Mental Ray groups lots of formats under 51
        renderViewFormat[52] = ["vr", "V-Ray", True] #V-Ray uses it's own formats so this is a placeholder
        
        #Add any extra after here, only useful for the errors
        renderViewFormat[100] = ["jpeg", "JPEG"]
        renderViewFormat[101] = ["psb", "Large Document Format"]
        renderViewFormat[102] = ["3ds","3D Studio"]
        renderViewFormat[103] = ["ma", "Maya Ascii"]
        renderViewFormat[104] = ["mb", "Maya Binary"]
        renderViewFormat[105] = ["dea", "Collada"]
        renderViewFormat[109] = ["dcm", "Dicom"]
        renderViewFormat[110] = ["dc3", "Dicom"]
        renderViewFormat[111] = ["dic", "Dicom"]
        renderViewFormat[112] = ["eps", "Photoshop EPS"]
        renderViewFormat[113] = ["fl3", "Flash 3D"]
        renderViewFormat[114] = ["jpf", "JPEG 2000"]
        renderViewFormat[115] = ["jpx", "JPEG 2000"]
        renderViewFormat[116] = ["jp2", "JPEG 2000"]
        renderViewFormat[117] = ["j2c", "JPEG 2000"]
        renderViewFormat[118] = ["j2k", "JPEG 2000"]
        renderViewFormat[119] = ["jpc", "JPEG 2000"]
        renderViewFormat[120] = ["jps", "JPEG Stereo"]
        renderViewFormat[121] = ["mxi", "Maxwell Image"]
        renderViewFormat[122] = ["mpo", "Multi-Picture Format"]
        renderViewFormat[123] = ["exr", "OpenEXR"]
        renderViewFormat[124] = ["pxr", "Pixar"]
        renderViewFormat[125] = ["pbm", "Portable Bit Map"]
        renderViewFormat[126] = ["hdr", "Radiance"]
        renderViewFormat[127] = ["rgbe", "Radiance"]
        renderViewFormat[128] = ["xyze", "Radiance"]
        renderViewFormat[129] = ["sct", "Scitex CT"]
        renderViewFormat[130] = ["tiff", "Tiff"]
        renderViewFormat[131] = ["img", "V-Ray Image"]
        renderViewFormat[200] = ["3fr", "Hasselblad Raw"]
        renderViewFormat[201] = ["fff", "Hasselblad Raw"]
        renderViewFormat[202] = ["ari", "ARRIFLEX Raw"]
        renderViewFormat[203] = ["arw", "Sony Raw"]
        renderViewFormat[204] = ["srf", "Sony Raw"]
        renderViewFormat[205] = ["sr2", "Sony Raw"]
        renderViewFormat[206] = ["bay", "Casio Raw"]
        renderViewFormat[207] = ["crw", "Canon Raw"]
        renderViewFormat[208] = ["cr2", "Canon Raw"]
        renderViewFormat[209] = ["cap", "Phase_One Raw"]
        renderViewFormat[210] = ["liq", "Phase_One Raw"]
        renderViewFormat[211] = ["eip", "Phase_One Raw"]
        renderViewFormat[212] = ["dcs", "Kodak Raw"]
        renderViewFormat[213] = ["dcr", "Kodak Raw"]
        renderViewFormat[214] = ["drf", "Kodak Raw"]
        renderViewFormat[215] = ["k25", "Kodak Raw"]
        renderViewFormat[216] = ["kdc", "Kodak Raw"]
        renderViewFormat[217] = ["dng", "Adobe Raw"]
        renderViewFormat[218] = ["erf", "Epson Raw"]
        renderViewFormat[219] = ["mef", "Mamiya Raw"]
        renderViewFormat[220] = ["mdc", "Minolta Raw"]
        renderViewFormat[221] = ["mrw", "Minolta Raw"]
        renderViewFormat[222] = ["mos", "Leaf Raw"]
        renderViewFormat[223] = ["nef", "Nikon Raw"]
        renderViewFormat[224] = ["nrw", "Nikon Raw"]
        renderViewFormat[225] = ["orf", "Olympus Raw"]
        renderViewFormat[226] = ["pef", "Pentax Raw"]
        renderViewFormat[227] = ["ptx", "Pentax Raw"]
        renderViewFormat[228] = ["pxn", "Logitech Raw"]
        renderViewFormat[229] = ["r3d", "Red Raw"]
        renderViewFormat[230] = ["raf", "Fuji Raw"]
        renderViewFormat[231] = ["rw2", "Panasonic Raw"]
        renderViewFormat[232] = ["rwl", "Leica Raw"]
        renderViewFormat[233] = ["rwz", "Rawzor Raw"]
        renderViewFormat[234] = ["srw", "Samsung Raw"]
        renderViewFormat[235] = ["x3f", "Sigma Raw"]
        
        mentalRayFormats = {}
        mentalRayFormats["tifu"] = ["TIFF uncompressed"]
        mentalRayFormats["hdr"] = ["HDR"]
        mentalRayFormats["exr"] = [renderViewFormat[123][1], True]
        mentalRayFormats["picture"] = ["Dassault"]
        mentalRayFormats["ppm"] = ["Portable Pixmap"]
        mentalRayFormats["ps"] = ["PostScript"]
        mentalRayFormats["qntntsc"] = ["Quantel NTSC"]
        mentalRayFormats["ct"] = ["mentalray Color"]
        mentalRayFormats["st"] = ["mentalray Alpha"]
        mentalRayFormats["nt"] = ["mentalray Normal"]
        mentalRayFormats["mt"] = ["mentalray Motion"]
        mentalRayFormats["zt"] = ["mentalray Depth"]
        mentalRayFormats["tt"] = ["mentalray Tag"]
        mentalRayFormats["bit"] = ["mentalray Bit"]
        mentalRayFormats["cth"] = ["mentalray HDR"]
        
        VRayFormats = {}
        VRayFormats[1] = renderViewFormat[8]
        VRayFormats[2] = renderViewFormat[32]
        VRayFormats[3] = ["vrimg", "V-Ray Image"]
        VRayFormats[4] = renderViewFormat[123]
        VRayFormats[5] = ["exr", "OpenEXR (multichannel)", True]
        VRayFormats[6] = renderViewFormat[19]
        VRayFormats[7] = renderViewFormat[20]
        VRayFormats[8] = renderViewFormat[5]
        VRayFormats[9] = renderViewFormat[3]
        
        #Find current renderer
        try:
            allRenderers = py.renderer( q=True, namesOfAvailableRenderers=True ) #Not needed but leaving here in case it comes in useful
            currentRenderer = py.getAttr( "defaultRenderGlobals.currentRenderer") #mayaSoftware/mayaHardware/mayaHardware2/mentalRay/vray
        except:
            currentRenderer = None
        
        #Assign MR setting to index 51
        if currentRenderer == "mentalRay":
            try:
                sceneExtension = py.getAttr( "defaultRenderGlobals.imfkey" ).lower()
                if py.getAttr( "defaultRenderGlobals.imageFormat" ) == 51 and sceneExtension in mentalRayFormats.keys():
                    renderViewFormat[51] = [[sceneExtension] + mentalRayFormats[sceneExtension]]
            except:
                pass
        
        #Assign V-Ray setting to index 52
        if currentRenderer == "vray":
            try:
                py.setAttr( "defaultRenderGlobals.imageFormat", 52 )
                vRayFormat = py.getAttr( "vraySettings.imageFormatStr" )
                vRayFormatList = dict( [[value[0],value] for key, value in VRayFormats.iteritems()] )
                renderViewFormat[52] = vRayFormatList[ py.getAttr( "vraySettings.imageFormatStr" ) ]
                
            except:
                pass
        
        
        ignoreFormats = [8, 20, 31, 32, 100]
        uploadFormats = [0, 8, 20, 32, 100]
        
        return renderViewFormat, ignoreFormats, uploadFormats
    
    #Format the time float into a date
    def dateFormat( self, input ):
        return datetime.fromtimestamp( float( input ) ).strftime( '%d/%m/%Y %H:%M' )

    #Find if path/file exists
    def validPath( self, path, **kwargs ):
       
        #This will truncate the final slash, to make sure the directory exists
        includeFile = checkInputs.checkBooleanKwargs( kwargs, False, 'f', 'iF', 'iI', 'file', 'image', 'include', 'isFile', 'isImage', 'includeFile', 'includeImage', 'includesFile', 'includesImage' )
       
        path = str( path )
        
        #Check URL and local paths separately
        if any( value in path for value in self.protocols ):
            try:
                Image.open( cStringIO.StringIO( urllib2.urlopen( path ).read() ) )
                isValid = True
            except:
                isValid = False
                
        else:
            if includeFile == True and "." in path.rsplit( '/', 1 )[1]:
                path = path.rsplit( '/', 1 )[0]
                
            isValid = os.path.exists( path )
        
        
        return isValid

    #Work out pixel values to affect
    def validRange( self, cutoffMode, bitsPerColour ):
        
        cutoffRange = pow( 2, bitsPerColour )
        
        if cutoffMode < 5:
            colourMinIncrease = 0
            colourMaxIncrease = cutoffMode*64-cutoffRange-1
            colourMaxReduce = 255
            colourMinReduce = cutoffMode*64+cutoffRange
        elif cutoffMode < 8:
            cutoffMode -= 4
            colourMinIncrease = cutoffMode*64
            colourMaxIncrease = 255-cutoffRange
            colourMinReduce = cutoffRange
            colourMaxReduce = cutoffMode*64-1
        else:
            colourMinIncrease = 0
            colourMaxIncrease = -1
            colourMinReduce = 255
            colourMaxReduce = 254
        
        colourIncreaseRange = range( colourMinIncrease, colourMaxIncrease+1 )
        colourReduceRange = range( colourMinReduce, colourMaxReduce+1 )
        
        return colourIncreaseRange, colourReduceRange
        
    def cache( self, *args, **kwargs ):
        
        cachePath = "{0}/{1}".format( self.defaultCacheDirectory, self.defaultCacheName )
        
        #If it should be formatted        
        returnRawValues = checkInputs.checkBooleanKwargs( kwargs, False, 'raw', 'rawValue' )

        
        #Return the path
        returnPath = checkInputs.checkBooleanKwargs( kwargs, False, 'path', 'cachePath', 'loc', 'location', 'cacheLocation', 'returnPath', 'returnLoc', 'returnLocation' )
        if returnPath == True:
            return cachePath
        
        #Open file and decode data
        try:
            textFile = open( cachePath, "r")
        except:
            return None
        try:
            outputData = self.decodeData( textFile.read(), decode = True )
        except:
            outputData = None
        textFile.close()
        
        
        #Delete the cache file
        validArgs = checkInputs.validKwargs( kwargs, 'c', 'clear', 'clean', 'clearCache', 'cleanCache', 'delCache', 'deleteCache' )
        for i in range( len( validArgs ) ):
            try:
                if kwargs[validArgs[i]] == True:
                    try:
                        os.remove( cachePath )
                        break
                    except:
                        pass
                #Only remove individual record instead
                elif type( kwargs[validArgs[i]] ) == str and outputData != None:
                    outputData.pop( kwargs[validArgs[i]], None )
            except:
                pass
        
        #Delete individual value
        if outputData != None:
            validArgs = checkInputs.validKwargs( kwargs, 'delValue', 'delKey', 'deleteValue', 'deleteKey', 'clearValue', 'clearKey', 'removeValue', 'removeKey' )
            deleteValue = None
            for i in range( len( validArgs ) ):
                outputData.pop( kwargs[validArgs[i]], None )
                
            #Write back to cache
            try:
                textFile = open( cachePath, "w")
                textFile.write( self.encodeData( outputData, encode = True ) )
                textFile.close()
            except:
                pass
            
            #Return single value
            validArgs = checkInputs.validKwargs( kwargs, 'k', 'v', 'key', 'value' )
            keyValue = None
            for i in range( len( validArgs ) ):
                try:
                    keyValue = outputData[kwargs[validArgs[i]]]
                    break
                except:
                    keyValue = None
                    
            if len( validArgs ) > 0:
                if keyValue:
                    return self.formatCache( {kwargs[validArgs[i]]: keyValue}, returnRawValues )
                else:
                    return None

            
        #If the hash should be calculated
        validArgs = checkInputs.validKwargs( kwargs, 'h', 'hash', 'returnHash', 'calculateHash', 'imageHash', 'MD5', 'imageMD5', 'image' )
        returnHash = None
        for i in range( len( validArgs ) ):
            try:
                if kwargs[validArgs[i]] == True:
                    returnHash = self.imageName
                    break
                elif self.readImage( str( kwargs[validArgs[i]] ) ) != None:
                    returnHash = str( kwargs[validArgs[i]] )
                    break
                else:
                    raise ImageStoreError( "can't read image" )
            except:
                returnHash = None
        
        if returnHash:
        
            customImage = self.readImage( returnHash )
            
            if customImage == None:
                return None
            
            else:
        
                #Find md5 of image
                imageHash = md5.new()
                try:
                    imageHash.update( customImage.tostring() )
                except:
                    pass
                imageMD5 = imageHash.hexdigest()
                
                return imageMD5
                
        elif len( validArgs ) > 0:
            return None
        
        if len( args ) > 0:
            if args[0] in outputData.keys():
                imageHash = args[0]
            else:
                imageHash = ImageStore().cache( MD5 = args[0] )
                
            if imageHash in outputData.keys():
                outputData = ImageStore().cache( key = imageHash, raw = True )
            else:
                return None
        
        #Return the stored data
        return self.formatCache( outputData, returnRawValues )

    def formatCache( self, outputData, returnRawValues = False ):   
    
        if returnRawValues == True:
            return outputData
            
        cacheOutput = []
        for imageHash in outputData.keys():
            cacheOutput.append( "Hash: {0}".format( imageHash ) )
            if len( outputData[imageHash][2] ) > 0:
                cacheOutput.append( "   URL: {0}".format( outputData[imageHash][2] ) )
            cacheOutput.append( "   Best cutoff mode: {0}".format( outputData[imageHash][0] ) )
            for cutoffMode in outputData[imageHash][1].keys():
                if len( outputData[imageHash][1][cutoffMode] ) > 0:
                    cacheOutput.append( "      Cutoff mode {0}:".format( cutoffMode ) )
                    for bitsPerPixel in outputData[imageHash][1][cutoffMode].keys():
                        cacheOutput.append( "         Storage with {0} bits per pixel: {1}".format( bitsPerPixel, outputData[imageHash][1][cutoffMode][bitsPerPixel]*bitsPerPixel ) ) 
    
        return GlobalValues.newLine.join( cacheOutput )
        
    def readImage( self, location ):
        
        location = str( location )
        
        #Load from URL
        if any( value in location for value in self.protocols ):
                        
            try:
                location = cStringIO.StringIO( urllib2.urlopen( location ).read() )
                
            except:
                return None
                
        #Open image
        try:
            return Image.open( location ).convert( "RGB" )
            
        except:
            return None

    def lowercase( self, input ):
        
        input = str( input )
        if len( input ) == 0:
            return input
        elif len( input ) == 1:
            return input.lower()
        else:
            return input[0].lower() + input[1:]
            
    def renderView( self, save = True ):
        
        renderViewFormat, ignoreFormats, uploadFormats = self.imageFormats()
        formatList = dict( [[item[0], key] for key, item in renderViewFormat.iteritems() if len( item ) == 2] )
        
        #To get around True = 1 and False = 0
        valueType = type( save )
        
        #Save file
        if valueType == bool:
        
            if save == True:
                try:
                    self.renderViewSaveLocation = py.renderWindowEditor( 'renderView', edit = True, writeImage = self.renderViewSaveLocation )[1]
                except:
                    pass
                    
            #Delete file
            elif save == False:
                try:
                    os.remove( self.renderViewSaveLocation )
                except:
                    try:
                        os.remove( "{0}.{1}".format( self.renderViewSaveLocation, self.imageFormats()[0][py.getAttr( "defaultRenderGlobals.imageFormat" )][0] ) )
                    except:
                        pass
        
        elif valueType == int or ( valueType == str and save.isdigit() ):
            try:
                if 0 <= int( save ) < 64:
                    py.setAttr( "defaultRenderGlobals.imageFormat", int( save ) )
                    py.setAttr( "defaultRenderGlobals.imfkey", renderViewFormat[int( save )] )
                else:
                    raise RangeError( "value must be between 0 and 63" )
            except:
                self.printCurrentProgress( "Error: Index must be between 0 and 63." )
        
        elif valueType == str:
            
            if save.lower() in formatList.keys():
            
                try:
                    py.setAttr( "defaultRenderGlobals.imageFormat", formatList[save.lower()] )
                    py.setAttr( "defaultRenderGlobals.imfkey", save.lower() )
                except:
                    self.printCurrentProgress( "Error: Can't update scene settings." )
            
            

#Compress into zip file
class ImageStoreZip:
    
    zipName = "ImageInfo.zip"
        
    @classmethod
    def write( self, input, fileName, **kwargs ):
        
        #Reset if already exists
        resetZip = checkInputs.checkBooleanKwargs( kwargs, False, 'r', 'd', 'reset', 'delete', 'resetZip', 'deleteZip', 'resetFile', 'deleteFile', 'resetZipFile', 'deleteZipFile' )
        
        #Get location to store zip file
        path = ImageStore.defaultImageDirectory
            
        #Remove final slash
        path.replace( "\\", "/" )
        while path[-1] == "/":
            path = path[:-1]
        
        if ImageStore().validPath( path ) == False:
            return False
            
        else:
            zipLocation = "{0}/{1}".format( path, self.zipName )
            if resetZip == True:
                try:
                    os.remove( zipLocation )
                except:
                    pass
                    
            zip = zipfile.ZipFile( zipLocation, mode='a', compression=zipfile.ZIP_DEFLATED )
            
            try:
                zip.writestr( fileName, input )
            except:
                if ImageStore.printProgress == True:
                    print "Error: Failed to write zip file."
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
                    raise IOError( "image doesn't exist" )
                    
            except:
                imageLocation = None
                
        #Read if zip file
        if any( value in imageLocation for value in ImageStore.protocols ):
        
            imageLocation = cStringIO.StringIO( urllib2.urlopen( imageLocation ).read() )
            
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
                        
            if 'creationtime' in nameList:
            
                if 'version' in nameList:
                    versionNumber = zip.read( 'version' )
                    
                else:
                    versionNumber = "pre-2.0"
                    
                creation = zip.read( 'creationtime' )
                    
                if "@" in creation:
                    creationName = creation.split( "@" )[0]
                    creationTime = creation.split( "@" )[1]
                else:
                    creationName = None
                    creationTime = None
                    
            else:
                versionNumber = None
                creationName = None
                creationTime = None
                
            if 'url' in nameList:
                customURL = zip.read( 'url' )
            else:
                customURL = None
        
        else:
            versionNumber = "pre-2.0"
            creationName = None
            creationTime = None
            customURL = None
        
        return [versionNumber, creationTime, creationName, customURL, nameList]
    
    @classmethod
    def combine( self, **kwargs ):
        
        #Get location to read zip file
        path = "{0}/{1}".format( ImageStore.defaultImageDirectory, self.zipName )
            
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
                    imageLocation = None
                    raise IOError( "image doesn't exist" )
                    
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
                    zipLocation = path
                    raise IOError( "zip file doesn't exist" )
                    
            except:
                zipLocation = path
        
        if imageLocation != None:
        
            locationOfImage = imageLocation.replace( "/", "\\\\" )
            locationOfZip = zipLocation.replace( "/", "\\\\" )
            
            #Copy zip file into picture
            call( 'copy /b "{0}" + "{1}" "{0}"'.format( locationOfImage, locationOfZip ), shell=True)
            
            os.remove( zipLocation )
            
            return True
            
        else:
            return False

class checkInputs:
    
    @classmethod
    def capitalLetterCombinations( self, *args ):
    
        returnList = []
        args = list( args )
        
        #Deal with spaces
        joinedArg = {}
        for arg in args:
            if " " in str( arg ):
                splitArg = str( arg ).split( " " )
                for i in range( len( splitArg ) ):
                    joinedArg[i] = self.capitalLetterCombinations( splitArg[i] )
        
        #Put together all combinations
        newArgs = ["".join( list( tupleValue ) ) for tupleValue in list( itertools.product( *[item for key, item in joinedArg.iteritems()] ) )]
        newArgs += [" ".join( list( tupleValue ) ) for tupleValue in list( itertools.product( *[item for key, item in joinedArg.iteritems()] ) )]
            
        #Check they don't exist
        for newArg in newArgs:
            if newArg not in args:
                args.append( newArg )
                
        #Find different upper and lower case combinations
        for arg in args :
            
            returnList.append( arg )
            
            if any( map( str.isupper, arg ) ):
            
                #If capital in text but not first letter
                if map( str.isupper, arg[0] )[0] == False:
                    returnList.append( ''.join( word[0].upper() + word[1:] for word in arg.split() ) )
                    returnList.append( arg.capitalize() )
                    
                #If capital is anywhere in the name as well as also first letter
                elif any( map( str.isupper, arg[1:] ) ):
                    returnList.append( arg.capitalize() )
                    
                returnList.append( arg.lower() )
                
            else:
            
                #If no capital letter is in at all
                returnList.append( ''.join( word[0].upper() + word[1:] for word in arg.split() ) )
        
        
        return sorted( set( filter( len, returnList ) ) )
    
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
    
    @classmethod
    def joinList( self, *args ):
        
        allCombinations = list( itertools.product( *args ) )
        joinedValues = ["".join( list( tupleValue ) ) for tupleValue in allCombinations]
        
        return tuple( joinedValues )

class RangeError( Exception ):
    pass
class ImageStoreError( Exception ):
    pass
