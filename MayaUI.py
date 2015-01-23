import pymel.core as py
import os, math
import ImageStore
reload( ImageStore )
from ImageStore import ImageStore


class UserInterface:
    
    
    windowName = "ImageStore"
    windowWidth = 550.0
    tabLayoutLines = "---------------------------"
    
    buttonList = {}
    textList = {}
    textFieldList = {}
    checkBoxList = {}
    radioButtonList = {}
    floatSliderGrpList = {}
    scrollFieldList = {}
    frameLayoutList = {}
    
    @classmethod
    def display( self ):

        if py.window( self.windowName, exists = True ):
            py.deleteUI( self.windowName, window = True )
        
        mainWindow = py.window( self.windowName, title = self.windowName, resizeToFitChildren = True, minimizeButton = True, maximizeButton = False, sizeable = False, width = self.windowWidth, restoreCommand = "UserInterface.changeSceneSettings()" )
        
        with py.rowColumnLayout( numberOfColumns = 1 ):
            py.text( label = "Use this to store or read information within images. They can be uploaded anywhere and read from other computers.", align = "left" )
            py.text( label = "" )
        
        with py.rowColumnLayout( numberOfColumns = 7 ):
            py.text( label = "", width = self.windowWidth/100*1 )
            py.text( label = " Path to image:", width = self.windowWidth/100*50, align = "left" )
            py.text( label = "", width = self.windowWidth/100*1 )
            py.text( label = "", width = self.windowWidth/100*25 )
            py.text( label = "", width = self.windowWidth/100*1 )
            self.textList["ValidateMainImage"] = py.text( label = "0", width = self.windowWidth/100*21 )
            py.text( label = "", width = self.windowWidth/100*1 )
            py.text( label = "" )
            self.textFieldList["MainImagePath"] = py.textField( text = "{0}/{1}".format( ImageStore.defaultImageDirectory, ImageStore.defaultImageName ), annotation = "Choose a path to save the file to, or a path or URL to read a file from" )
            py.text( label = "" )
            
            with py.rowColumnLayout( numberOfColumns = 2 ):
                self.buttonList["NewImage"] = py.button( label = "New Image", width = self.windowWidth/100*12.5, command = py.Callback( self.fileReading, True, True, "textField", "MainImagePath", "ValidateMainImage" ), annotation = "Save a new image" )
                self.buttonList["BrowseImage"] = py.button( label = "Browse", width = self.windowWidth/100*12.5, command = py.Callback( self.fileReading, False, True, "textField", "MainImagePath", "ValidateMainImage" ), annotation = "Open an existing image" )
                
            py.text( label = "" )
            self.buttonList["ValidateMainImage"] = py.button( label = "Check if valid", command = py.Callback( self.checkPathToImage ), annotation = "Check if the image exists or if it's possible to write to the location" )
            py.text( label = "" )
            py.text( label = "" )
            py.text( label = "" )
            py.text( label = "" )
            py.text( label = "" )
            py.text( label = "" )
            
            with py.rowColumnLayout( numberOfColumns = 2 ):
                self.checkBoxList["ImagePathExists"] = py.checkBox( label = "Exists", editable = False )
                self.checkBoxList["ImagePathWriteable"] = py.checkBox( label = "Writeable", editable = False )
                
            py.text( label = "" )
            py.text( label = "" )
            
            self.textList["CustomImagePath"] = py.text( label = " Path to custom image (optional):", align = "left" ) 
            py.text( label = "" )
            py.text( label = "" )
            py.text( label = "" )
            self.textList["ValidateCustomImage"] = py.text( label = "0" )
            py.text( label = "" )
            py.text( label = "" )
            self.textFieldList["CustomImagePath"] = py.textField( text = "http://images.peterhuntvfx.co.uk/music.jpg", annotation = "Choose a path or URL to an image (optional)" )
            py.text( label = "" )
            
            with py.rowColumnLayout( numberOfColumns = 2 ):
                self.buttonList["BrowseCustomImage"] = py.button( label = "Browse", command = py.Callback( self.fileReading, False, True, "textField", "CustomImagePath", "ValidateCustomImage" ), annotation = "Open an image" )
                self.buttonList["UseRenderView"] = py.button( label = "Use Render View", command = py.Callback( self.useRenderView ), annotation = "Use the image currently in the Render View window" )
                
            py.text( label = "" )
            self.buttonList["ValidateCustomImage"] = py.button( label = "Check if valid", command = py.Callback( self.checkPathToCustomImage ), annotation = "Check if the file can be read as an image, and if any information exists in the cache" )
            
            py.text( label = "" )
            py.text( label = "" )
            self.checkBoxList["DisableCustomImage"] = py.checkBox( label = "Disable custom image", changeCommand = py.Callback( self.disableCustomImage ), annotation = "Disable the custom image features" )
            
            py.text( label = "" )
            with py.rowColumnLayout( numberOfColumns = 2 ):
                py.button( label = "Browse", command = py.Callback( self.fileReading, False, True, "textField", "customImagePath" ), visible = False )
                
                
                with py.rowColumnLayout( numberOfColumns = 3 ):
                    self.buttonList["RenderView"] = {}
                    self.renderViewFormats = ["jpg", "png", "bmp"]
                    imageFormatsDict = dict( [[item[0], item[1]] for key, item in ImageStore().imageFormats()[0].iteritems() if len( item ) == 2] )
                    for i in range( 3 ):
                        
                        self.buttonList["RenderView"][self.renderViewFormats[i]] = py.button( label = self.renderViewFormats[i].upper(), command = py.Callback( self.changeSceneSettings, self.renderViewFormats[i].lower() ), annotation = "Set the scene to use {0} files".format( imageFormatsDict[self.renderViewFormats[i].lower()] ) )
                    self.changeSceneSettings()
                    
            py.text( label = "" )
            
            with py.rowColumnLayout( numberOfColumns = 2 ):
                self.checkBoxList["CustomImageIsImage"] = py.checkBox( label = "Image", editable = False )
                self.checkBoxList["CustomImageIsCached"] = py.checkBox( label = "Cached", editable = False )
                
            py.text( label = "" )
        
        with py.tabLayout( width = self.windowWidth ):
    
            with py.columnLayout( "Main" ):
                
                with py.frameLayout( label = "Write", collapsable = True, collapse = False, width = self.windowWidth/100*99.5 ):
                    with py.rowColumnLayout( numberOfColumns = 3 ):
                        with py.rowColumnLayout( numberOfColumns = 1, width = self.windowWidth/100*49 ):
                            
                            py.text( label = "   Input data:", align = "left", width = self.windowWidth/100*45.2 )
                            self.textFieldList["InputData"] = py.textField( text = "Store this text in an image", changeCommand = py.Callback( self.validateInput ), annotation = "Write anything to store in an image" )
                            
                            inputRadioAnnotation = "Choose how to treat the input data"
                            with py.rowColumnLayout( numberOfColumns = 3 ):
                                py.radioCollection()
                                self.radioButtonList["InputIsText"] = py.radioButton( label = "Convert input to string or integer", width = self.windowWidth/100*35.2, select = True, annotation = inputRadioAnnotation )
                                py.text( label = "" )
                                self.buttonList["ValidateInputHidden"] = py.button( label = "Validate", visible = False ) #Just for the spacing
                            with py.rowColumnLayout( numberOfColumns = 3 ):
                                self.radioButtonList["InputIsCode"] = py.radioButton( label = "Use input as code", width = self.windowWidth/100*35.9, onCommand = py.Callback( self.validateInput, "code" ), annotation = inputRadioAnnotation )
                                py.text( label = "" )
                                self.buttonList["ValidateInputCode"] = py.button( label = "Validate", command = py.Callback( self.validateInput, "code" ), annotation = "Check if the input can be parsed as code", width = self.windowWidth/100*9 )
                            with py.rowColumnLayout( numberOfColumns = 5 ):
                                self.radioButtonList["InputIsFile"] = py.radioButton( label = "Input is file path", width = self.windowWidth/100*26, onCommand = py.Callback( self.validateInput, "file" ), annotation = inputRadioAnnotation )
                                py.text( label = "" )
                                py.button( label = "Browse", command = py.Callback( self.validateInput, "browse" ), annotation = "Choose a file to store", width = self.windowWidth/100*9 )
                                py.text( label = "" )
                                self.buttonList["ValidateInputFile"] = py.button( label = "Validate", command = py.Callback( self.validateInput, "file" ), annotation = "Check if the file can be read", width = self.windowWidth/100*9 )
        
                        py.text( label = "", width = self.windowWidth/100*1 )
                        with py.rowColumnLayout( numberOfColumns = 1, width = self.windowWidth/100*49 ):
                            py.text( label = "   Upload:", align="left" )
                            self.checkBoxList["UploadMainImage"] = py.checkBox( label = "Upload output image", changeCommand = py.Callback( self.uploadCheckBox ) )
                            self.checkBoxList["OpenMainImage"] = py.checkBox( label = "Open uploaded image in browser" )
                            self.checkBoxList["UploadCustomImage"] = py.checkBox( label = "Upload custom image (recommended)", value = True )
                            py.text( label = "" )
                            py.text( label = "   Set ratio of width to height:", align="left" )
                            self.floatSliderGrpList["Ratio"] = py.floatSliderGrp( field = True, minValue = 0.2, maxValue = 0.8, fieldMinValue = 0.0001, fieldMaxValue = 0.9999, precision = 4, value = math.log( 1920 ) / math.log( 1920*1080 ) )
        
        
                with py.frameLayout( label = "Read", collapsable = True, collapse = False, width = self.windowWidth/100*99.5 ):
                    with py.rowColumnLayout( numberOfColumns = 3 ):
                        with py.rowColumnLayout( numberOfColumns = 1, width = self.windowWidth/100*49 ):
                            py.radioCollection()
                            with py.rowColumnLayout( numberOfColumns = 3 ):
                                self.radioButtonList["ReturnAll"] = py.radioButton( label = "Return all data", select = True )
                                py.textField( width = self.windowWidth/100*10, visible = False )
                                py.text( label = "" )
                            with py.rowColumnLayout( numberOfColumns = 3 ):
                                returnSomeDataCommand = py.Callback( self.returnSomeData )
                                self.radioButtonList["ReturnSome"] = py.radioButton( label = "Return " )
                                self.textFieldList["ReturnSome"] = py.textField( text = 100, width = self.windowWidth/100*10, receiveFocusCommand = returnSomeDataCommand, changeCommand = returnSomeDataCommand, enterCommand = returnSomeDataCommand )
                                py.text( label = " characters of data" )
                        py.text( label = "", width = self.windowWidth/100*1 )
                        with py.rowColumnLayout( numberOfColumns = 1, width = self.windowWidth/100*49 ):
                            self.checkBoxList["SaveAsFile"] = py.checkBox( label = "Save as file", changeCommand = py.Callback( self.saveOutputAsFile ) )
                            with py.rowColumnLayout( numberOfColumns = 3 ):
                                self.textFieldList["SaveAsFile"] = py.textField( width = self.windowWidth/100*35 )
                                py.text( label = "" )
                                self.buttonList["SaveAsFile"] = py.button( label = "Browse", command = py.Callback( self.fileReading, True, False, "textField", "SaveAsFile" ) )
                                
                    with py.rowColumnLayout( numberOfColumns = 3, width = self.windowWidth/100*99.5 ):
                        py.text( label = "", width = self.windowWidth/100*1 )
                        py.checkBox( label = "Use custom image path instead of stored URL (enable if custom image URL was not saved to the image)" )
                        py.text( label = "", width = self.windowWidth/100*1 )
        
            with py.columnLayout( "Advanced" ):
                
                with py.frameLayout( label = "Write", collapsable = True, collapse = False, width = self.windowWidth/100*99.5 ):
                    with py.rowColumnLayout( numberOfColumns = 3 ):
                        py.text( label = "", width = self.windowWidth/100*1 )
                        with py.rowColumnLayout( numberOfColumns = 1, width = self.windowWidth/100*99.5 ):
                            self.checkBoxList["Validate"] = py.checkBox( label = "Validate output image", value = True )
                            self.checkBoxList["Revert"] = py.checkBox( label = "Cancel if custom image is too small (otherwise the custom image will just be disabled)" )
                            self.checkBoxList["SaveInformation"] = py.checkBox( label = "Save extra information into file (recommended)", value = True )
                        py.text( label = "", width = self.windowWidth/100*1 )
                        
                with py.frameLayout( label = "Cutoff Modes", collapsable = True, collapse = True, width = self.windowWidth/100*99.5 ):
                    
                    with py.rowColumnLayout( numberOfColumns = 1 ):
                        py.text( label = "   Cutoff modes define if the values should be added or subtracted based on the brightness of the pixel.", align = "left" )
                        
                    with py.rowColumnLayout( numberOfColumns = 5 ):
                        py.text( label="", width = self.windowWidth/100*1 )
                        with py.rowColumnLayout( numberOfColumns = 1, width = self.windowWidth/100*48 ):
                            self.checkBoxList["AllCutoffModes"] = py.checkBox( label = "Use all cutoff modes", changeCommand = py.Callback( self.addNewCutoffMode, *range( 8 ) ) )
                            self.textList["CutoffModesTemporary"] = py.text( label = "", visible = False )
                            py.text( label="   Select cutoff mode(s):", align="left", width = self.windowWidth/100*45.2 )
                            self.textFieldList["CutoffModes"] = py.textField( enterCommand = py.Callback( self.addNewCutoffMode ), changeCommand = py.Callback( self.addNewCutoffMode ) )
                            
                            with py.rowColumnLayout( numberOfColumns = 16 ):
                                self.checkBoxList["CutoffMode"] = {}
                                self.textList["CutoffMode"] = {}
                                for i in range( 8 ):
                                    textLabel = "  {0} ".format( i )
                                    if i == 0:
                                        textLabel = textLabel[1:]
                                    self.textList["CutoffMode"][i] = py.text( label = textLabel )
                                    self.checkBoxList["CutoffMode"][i] = py.checkBox( label = "", changeCommand = py.Callback( self.addNewCutoffMode, i ) )
                                    
                            py.text( label = "" )
                            py.text( label="   File suffix used for saving multiple images:", align="left" )
                            with py.rowColumnLayout( numberOfColumns = 3, width = self.windowWidth/100*45.2 ):
                                self.textFieldList["MultipleImagesName"] = py.textField( text = "{0}/{1}.".format( ImageStore().defaultImageDirectory, ".".join( ImageStore().defaultImageName.split( "." )[:-1] ) ), editable=False, width = self.windowWidth/100*31 )
                                self.textFieldList["MultipleImagesPrefix"] = py.textField( text = "m", width = self.windowWidth/100*8.7 )
                                self.textFieldList["MultipleImagesSuffix"] = py.textField( text = ".png", editable=False, width = self.windowWidth/100*5.5 )                
                            
                        py.text( label="", width = self.windowWidth/100*1 )
                        with py.rowColumnLayout( numberOfColumns = 1, width = self.windowWidth/100*48 ):
                            py.scrollField( wordWrap = True, height = 135, width = self.windowWidth/100*47, enable = False, text = "0: Move towards 0<br>1: Move towards 64<br>2: Move towards 128<br>3: Move towards 192<br>4: Move towards 255<br>5: Move away from 64<br>6: Move away from 128<br>7: Move away from 192" )
        
                with py.frameLayout( label = "Cache", collapsable = True, collapse = True, width = self.windowWidth/100*99.5 ):
                    
                    with py.rowColumnLayout( numberOfColumns = 5 ):
                        py.text( label="", width = self.windowWidth/100*1 )
                        
                        with py.rowColumnLayout( numberOfColumns = 1, width = self.windowWidth/100*48):
                            self.checkBoxList["WriteCache"] = py.checkBox( label="Write information to cache file", value = True )
                            py.text( label = "" )
                            py.button( label = "Get MD5 hash of Custom Image", width = self.windowWidth/100*47, command = py.Callback( self.getImageMD5 ) )
                            self.textFieldList["CustomImageHash"] = py.textField( editable = False )
                            py.text( label = "" )
                            py.button( label = "Return Entire Cache Contents", width = self.windowWidth/100*47, command = py.Callback( self.getAllCacheInfo ) )
                            
                        py.text( label="", width = self.windowWidth/100*1 )
                        with py.rowColumnLayout( numberOfColumns = 1, width = self.windowWidth/100*48):
                            
                            py.text( label = "", height = 8 )
                            py.text( label = "" )
                            
                            py.text( label = "   Delete MD5 hash from cache:", align = "left" )
                            with py.rowColumnLayout( numberOfColumns = 3 ):
                                self.textFieldList["ImageMD5Delete"] = py.textField( width = self.windowWidth/100*35 )
                                py.text( label = "" )
                                py.button( label = "Delete", width = self.windowWidth/100*8, command = py.Callback( self.deleteCacheKey ) )
                            py.text( label = "" )
                            
                            py.text( label = "   Return information for MD5 hash:", align = "left" )
                            with py.rowColumnLayout( numberOfColumns = 3 ):
                                self.textFieldList["ImageMD5Return"] = py.textField( width = self.windowWidth/100*35 )
                                py.text( label = "" )
                                py.button( label = "Return", width = self.windowWidth/100*8, command = py.Callback( self.getImageMD5Info ) )
                                
                                
                        py.text( label="", width = self.windowWidth/100*1 )
                        
                    py.text( label = "" )
                    
                    with py.frameLayout( label = "Cache Output", collapsable = True, collapse = True, width = self.windowWidth/100*99 ) as self.frameLayoutList["CacheOutput"]:
                        self.scrollFieldList["CacheOutput"] = py.scrollField( height = 200 )
            
                with py.frameLayout( label = "Other", collapsable = True, collapse = True, width = self.windowWidth/100*99.5 ):
                    with py.rowColumnLayout( numberOfColumns = 3 ):
                        py.text( label = "", width = self.windowWidth/100*1 )
                        with py.rowColumnLayout( numberOfColumns = 1, width = self.windowWidth/100*99.5 ):
                            py.checkBox( label = "Upload non Imgur URLs to Imgur", value = True )
                        py.text( label = "", width = self.windowWidth/100*1 )
            
            with py.columnLayout( "Debug" ):
                
                with py.frameLayout( label = "Write", collapsable = True, collapse = False, width = self.windowWidth/100*99.5 ):
                    with py.rowColumnLayout( numberOfColumns = 5 ):
                        py.text( label="", width = self.windowWidth/100*1 )
                        with py.rowColumnLayout( numberOfColumns = 1, width = self.windowWidth/100*48):
                            self.checkBoxList["ReturnCustomURL"] = py.checkBox( label="Return URL to custom image after uploading", value = True )
                        py.text( label="", width = self.windowWidth/100*1 )
                        with py.rowColumnLayout( numberOfColumns = 1, width = self.windowWidth/100*48):
                            self.checkBoxList["DebugData"] = py.checkBox( label="Enable debug write mode" )
                        py.text( label="", width = self.windowWidth/100*1 )
                
                with py.frameLayout( label = "Size", collapsable = True, collapse = False, width = self.windowWidth/100*99.5 ):
                    with py.rowColumnLayout( numberOfColumns = 5 ):
                        py.text( label="", width = self.windowWidth/100*1 )
                        with py.rowColumnLayout( numberOfColumns = 1, width = self.windowWidth/100*30):
                            py.text( label = "" )
                            py.button( label = "Calculate size of input value", width = self.windowWidth/100*30, command = py.Callback( self.calculateSizeOfInput ) )
                        py.text( label="", width = self.windowWidth/100*1 )
                        with py.rowColumnLayout( numberOfColumns = 1, width = self.windowWidth/100*66):
                            
                            py.text( label = "   Calculate how much data an image can hold:", align = "left" )
                            with py.rowColumnLayout( numberOfColumns = 5 ):
                                self.textFieldList["CalculateImageSize"] = py.textField( width = self.windowWidth/100*46 )
                                py.text( label = "" )
                                py.button( label = "Browse", width = self.windowWidth/100*8, command = py.Callback( self.fileReading, False, True, "textField", "CalculateImageSize" ), annotation = "Open an image" )
                                py.text( label = "" )
                                py.button( label = "Read", width = self.windowWidth/100*8, command = py.Callback( self.calculateSizeOfImage ) )
                        py.text( label="", width = self.windowWidth/100*1 )
                    with py.rowColumnLayout( numberOfColumns = 3 ):
                        py.text( label = "", width = self.windowWidth/100*1 )
                        self.textFieldList["DebugSizeInput"] = py.textField( width = self.windowWidth/100*96, editable = False )
                        py.text( label = "", width = self.windowWidth/100*1 )
                        py.text( label = "", width = self.windowWidth/100*1 )
                        self.textFieldList["DebugSizeImage"] = py.textField( width = self.windowWidth/100*96, editable = False )
                        py.text( label = "", width = self.windowWidth/100*1 )
                        
                 
        with py.rowColumnLayout( numberOfColumns = 5 ):
            py.text( label="", width = self.windowWidth/100*1 )
            py.button( label = "Write Image", width = self.windowWidth/100*49, command = py.Callback( self.writeImage ) )
            py.text( label = "", width = self.windowWidth/100*1 )
            py.button( label = "Read Image", width = self.windowWidth/100*49 )
            py.text( label = "", width = self.windowWidth/100*1 )      
            
            
        with py.rowColumnLayout( numberOfColumns = 1 ):
            with py.frameLayout( label = "Write Output", collapsable = True, collapse = True, visible = True, width = self.windowWidth/100*101 ) as self.frameLayoutList["OutputWrite"]:
                
                with py.rowColumnLayout( numberOfColumns = 5 ):
                    py.text( label="", width = self.windowWidth/100*1 )
                    
                    with py.rowColumnLayout( numberOfColumns = 1, width = self.windowWidth/100*48 ):
                        py.text( label="   Path:", align = "left", width = self.windowWidth/100*45.2 )
                        self.scrollFieldList["OutputPath"] = py.scrollField( height = 65, editable = False )
                
                
                    py.text( label="", width = self.windowWidth/100*1 )
                    with py.rowColumnLayout( numberOfColumns = 1, width = self.windowWidth/100*48 ):
                        py.text( label="   URL:", align = "left", width = self.windowWidth/100*45.2 )
                        self.textFieldList["OutputURL"] = py.textField( editable = False )
                        py.text( label = "" )
                        py.text( label="   Custom Image URL:", align = "left", width = self.windowWidth/100*45.2 )
                        self.textFieldList["OutputCustomURL"] = py.textField( editable = False )
                        
                    py.text( label="", width = self.windowWidth/100*1 )
                    
            with py.frameLayout( label = "Read Output", collapsable = True, collapse = True, visible = True, width = self.windowWidth/100*101, ann = "Test" ):
                py.scrollField( height = 260, editable = False, wordWrap = True, text = str( range( 1000 ) ) ) 
            
        self.setFinalValues()
        py.showWindow()
    
    @classmethod
    def writeImage( self ):
        
        kwargs = {}
        imagePath = py.textField( self.textFieldList["MainImagePath"], query = True, text = True )
        
        customImagePath = py.textField( self.textFieldList["CustomImagePath"], query = True, text = True )
        disableCustomImage = py.checkBox( self.checkBoxList["DisableCustomImage"], query = True, value = True )
        
        #Make sure custom image is valid
        if py.text( self.textList["ValidateCustomImage"], query = True, label = True ) != "1":
            py.button( self.buttonList["ValidateCustomImage"], query = True, command = True )()
        if py.text( self.textList["ValidateCustomImage"], query = True, label = True ) == "1":
            kwargs["CustomImagePath"] = customImagePath
        
        inputData = self.validateInput( None, True )
        kwargs["Input"] = "test"
        
        kwargs["Upload"] = py.checkBox( self.checkBoxList["UploadMainImage"], query = True, value = True )
        kwargs["OpenUploadedImage"] = py.checkBox( self.checkBoxList["OpenMainImage"], query = True, value = True )
        kwargs["UploadCustomImage"] = py.checkBox( self.checkBoxList["UploadCustomImage"], query = True, value = True )
        
        kwargs["SizeRatio"] = py.floatSliderGrp( self.floatSliderGrpList["Ratio"], query = True, value = True )
        
        kwargs["ValidateOutput"] = py.checkBox( self.checkBoxList["Validate"], query = True, value = True )
        kwargs["Revert"] = py.checkBox( self.checkBoxList["Revert"], query = True, value = True ) 
        kwargs["DisableInformation"] = not py.checkBox( self.checkBoxList["SaveInformation"], query = True, value = True )
        
        cutoffModes = py.textField( self.textFieldList["CutoffModes"], query = True, text = True )
        if cutoffModes:
            kwargs["cutoffModes"] = tuple( cutoffModes )
        
        cutoffPrefix = py.textField( self.textFieldList["MultipleImagesPrefix"], query = True, text = True )
        if cutoffPrefix:
            kwargs["cutoffModePrefix"] = cutoffPrefix
            
        kwargs["WriteToCache"] = py.checkBox( self.checkBoxList["WriteCache"], query = True, value = True )
        
        kwargs["returnCustomImageURL"] = py.checkBox( self.checkBoxList["ReturnCustomURL"], query = True, value = True )
        kwargs["debugOutput"] = py.checkBox( self.checkBoxList["DebugData"], query = True, value = True )
        
        outputLocations = ImageStore( imagePath ).write( **kwargs )
        print outputLocations
        imagePaths = []
        imageURLs = []
        customURL = []
        if outputLocations:
            for i in range( len( outputLocations ) ):
                currentImagePath = outputLocations[i]
                imagePaths.append( currentImagePath[0] )
                if len( currentImagePath ) == 3 or ( len( currentImagePath ) == 2 and kwargs["returnCustomImageURL"] == False ):
                    imageURLs.append( currentImagePath[1] )
                elif len( currentImagePath ) > 1:
                    customURL.append( currentImagePath[-1] )
        if len( imagePaths ) == 0:
            imagePaths.append( "Image wasn't saved" )
        
        py.scrollField( self.scrollFieldList["OutputPath"], edit = True, text = "<br>".join( imagePaths ) )
        py.textField( self.textFieldList["OutputURL"], edit = True, text = ", ".join( imageURLs ) )
        py.textField( self.textFieldList["OutputCustomURL"], edit = True, text = ", ".join( list( set( customURL ) ) ) )
        py.frameLayout( self.frameLayoutList["OutputWrite"], edit = True, collapse = False )
    
    @classmethod
    def calculateSizeOfInput( self ):
        
        input = self.validateInput( None, True )
        
        if input:
            inputSize = ImageStore().write( input, inputSize = True )
        else:
            inputSize = 0
        
        if inputSize > 0:
            content = "Input data is {0} bytes ({1}kb), going up to {2} bytes ({3}kb) when using 1 bit per colour".format( inputSize, int( inputSize )/1024, inputSize*8, int( inputSize*8 )/1024 )
        else:
            content = "Input data is invalid"
        
        py.textField( self.textFieldList["DebugSizeInput"], edit = True, text = content )
        
        
    @classmethod
    def calculateSizeOfImage( self ):
        
        imageLocation = ImageStore().getImageLocation( py.textField( self.textFieldList["CalculateImageSize"], query = True, text = True ) )
        content = None
        if imageLocation:
            
            imageSize = ImageStore().write( customImage = imageLocation, getImageSize = True )
            
            if imageSize:
                content = "Image can store up to around {0} bytes ({1}kb)".format( imageSize, int( imageSize )/1024 )
                
        if not content:
            content = "Unable to read image"
        py.textField( self.textFieldList["DebugSizeImage"], edit = True, text = content )
        ImageStore().renderView( False )
        
    @classmethod
    def deleteCacheKey( self ):
        
        imageHash = py.textField( self.textFieldList["ImageMD5Delete"], query = True, text = True )
        if imageHash:
            ImageStore().cache( deleteKey = imageHash )
        
    @classmethod
    def updateCacheOutput( self, cacheContents, individualValue = False ):
        
        #Format text for html
        if cacheContents:
            newReplace = cacheContents.replace( "\r\n", "<br>" ).replace( "<br> ", "<br>&nbsp;" )
            while cacheContents != newReplace:
                cacheContents = newReplace
                newReplace = cacheContents.replace( "&nbsp; ", "&nbsp;&nbsp;" )
        else:
            if individualValue == True:
                newReplace = "No cache data found matching the input"
            else:
                newReplace = "No cache data found"
        
        #Write to the scroll field
        py.frameLayout( self.frameLayoutList["CacheOutput"], edit = True, collapse = False )
        py.scrollField( self.scrollFieldList["CacheOutput"], edit = True, text = newReplace )
    
    @classmethod
    def getAllCacheInfo( self ):
        
        #Return all values to cache output
        self.updateCacheOutput( ImageStore().cache() )
    
    @classmethod
    def getImageMD5Info( self ):
        
        #Return a single image to the cache output
        imageHash = py.textField( self.textFieldList["ImageMD5Return"], query = True, text = True )
        self.updateCacheOutput( ImageStore().cache( key = imageHash ), True )
    
    
    @classmethod
    def getImageMD5( self ):
        
        #Get hash of currently selected image
        imageLocation = ImageStore().getImageLocation( py.textField( self.textFieldList["CustomImagePath"], query = True, text = True ) )
        imageHash = ImageStore().cache( MD5 = imageLocation )
        if not imageHash:
            imageHash = "Unable to read image"
        py.textField( self.textFieldList["CustomImageHash"], edit = True, text = imageHash )
        ImageStore().renderView( False )
    
    @classmethod
    def addNewCutoffMode( self, *args ):
        
        #Sort out text
        newArgs = []
        currentText = py.textField( self.textFieldList["CutoffModes"], query = True, text = True )
        splitText = currentText.split( "." )
        splitText = ";".join( splitText ).split( " " )
        splitText = ";".join( splitText ).split( "," )
        splitText = ";".join( splitText ).split( "." )
        splitText = ";".join( splitText ).split( ":" )
        splitText = ";".join( splitText ).split( ";" )
        allNumbers = [int( num ) for num in splitText if num.isdigit()]
        
        #If returning from deselecting the cutoff modes
        if len( args ) > 0:
            if args[0] == "return":
                args = tuple( list( args )[1:] )
                
                for i in range( 8 ):
                    if i in args:
                        enabled = True
                    else:
                        enabled = False
                        
                    py.checkBox( self.checkBoxList["CutoffMode"][i], edit = True, enable = True, value = enabled )
                
        #If checkbox is ticked
        enableValue = True
        if len( args ) == 1:
            enableValue = py.checkBox( self.checkBoxList["CutoffMode"][args[0]], query = True, value = True )
            allNumbers = [num for num in allNumbers if num != args[0]]
        
        #If all cutoff modes is ticked
        if len( args ) == 8:
            enableValue = py.checkBox( self.checkBoxList["AllCutoffModes"], query = True, value = True )
            
            #Store values in hidden text field
            if enableValue:
                py.text( self.textList["CutoffModesTemporary"], edit = True, label = ",".join( [str( num ) for num in allNumbers] ) )
            else:
                newArgs = ["return"] + [int( num ) for num in py.text( self.textList["CutoffModesTemporary"], query = True, label = True ).split( "," ) if num.isdigit()]
                
            py.textField( self.textFieldList["CutoffModes"], edit = True, enable = not enableValue )
            
            for i in range( 8 ):
                py.checkBox( self.checkBoxList["CutoffMode"][i], edit = True, editable = not enableValue )
                py.text( self.textList["CutoffMode"][i], edit = True, enable = not enableValue )
                
            allNumbers = []
        
        #Add number to list
        for i in range( len( args ) ):
            py.checkBox( self.checkBoxList["CutoffMode"][args[i]], edit = True, value = enableValue )
            if int( args[i] ) not in allNumbers and enableValue == True:
                allNumbers.append( args[i] )
        
        allNumbers = list( set( allNumbers ) )
        allNumbers.sort()
        
        py.textField( self.textFieldList["CutoffModes"], edit = True, text = ", ".join( [str( num ) for num in allNumbers if num in range( 8 )] ) )
        
        if len( newArgs ) > 0:
            self.addNewCutoffMode( *newArgs )
    
    @classmethod
    def saveOutputAsFile( self ):
        
        #Enable controls if checkbox is ticked
        enableSaveFile = py.checkBox( self.checkBoxList["SaveAsFile"], query = True, value = True )
        py.textField( self.textFieldList["SaveAsFile"], edit = True, editable = enableSaveFile )
        py.button( self.buttonList["SaveAsFile"], edit = True, enable = enableSaveFile )
    
    @classmethod
    def returnSomeData( self ):
        
        #Select radio button if text or textField is clicked on
        py.radioButton( self.radioButtonList["ReturnSome"], edit = True, select = True )
    
    @classmethod
    def uploadCheckBox( self ):
        
        #Disable open image in browser checkbox if upload is not selected
        uploadImage = py.checkBox( self.checkBoxList["UploadMainImage"], query = True, value = True )
        py.checkBox( self.checkBoxList["OpenMainImage"], edit = True, editable = uploadImage )

    @classmethod
    def validButton( self, buttonName, valid ):
        
        try:
            if valid == True:
                py.button( self.buttonList[buttonName], edit = True, backgroundColor = ( 0, 1, 0 ), label = "Valid" )
                try:
                    py.text( self.textList[buttonName], edit = True, label = "1" )
                except:
                    pass
            elif valid == False:
                py.button( self.buttonList[buttonName], edit = True, backgroundColor = ( 1, 0, 0 ), label = "Invalid" )
                try:
                    py.text( self.textList[buttonName], edit = True, label = "0" )
                except:
                    pass
        
        except:
            pass

    @classmethod
    def validateInput( self, inputType = None, returnOnly = False ):
        
        input = py.textField( self.textFieldList["InputData"], query = True, text = True )
        
        #If the string is changed, validate based on current radio button selection
        if not inputType:
            radioButtonList = {}
            radioButtonList[None] = py.radioButton( self.radioButtonList["InputIsText"], query = True, select = True ) 
            radioButtonList["code"] = py.radioButton( self.radioButtonList["InputIsCode"], query = True, select = True )
            radioButtonList["file"] = py.radioButton( self.radioButtonList["InputIsFile"], query = True, select = True )
            inputType = [key for key, value in radioButtonList.iteritems() if value == True][0]
        
        #Check if it can be executed as code
        if inputType == "code":
            if not returnOnly:
                py.radioButton( self.radioButtonList["InputIsCode"], edit = True, select = True )
            try:
                input = eval( input )
                self.validButton( "ValidateInputCode", True )
            except:
                self.validButton( "ValidateInputCode", False )
                input = None
        
        #Check if it can be read
        if inputType in ["browse", "file"]:
            if inputType == "browse":
                inputType = self.fileReading( False, False, "textField", "InputData", "ValidateInputFile" )
                
            if inputType == "file":
                try:
                    with open( input ) as fileName:
                        content = fileName.read()
                    self.validButton( "ValidateInputFile", True )
                    input = content
                except:
                    self.validButton( "ValidateInputFile", False )
                    input = None
            
            if inputType and not returnOnly:
                py.radioButton( self.radioButtonList["InputIsFile"], edit = True, select = True )
        
        return input
            
    
    @classmethod
    def setFinalValues( self ):
        mainImageCheck = py.button( self.buttonList['ValidateMainImage'], query = True, command = True )
        customImageCheck = py.button( self.buttonList['ValidateCustomImage'], query = True, command = True )
        py.textField( self.textFieldList["MainImagePath"], edit = True, changeCommand = py.Callback( mainImageCheck ), enterCommand = py.Callback( mainImageCheck ) )
        py.textField( self.textFieldList["CustomImagePath"], edit = True, changeCommand = py.Callback( customImageCheck ), enterCommand = py.Callback( customImageCheck ) )
        self.saveOutputAsFile()
        self.uploadCheckBox()
        
    @classmethod
    def disableCustomImage( self ):
        
        #Fix due to an error happening on the first run of the code when the checkbox doesn't exist
        try:
            disabled = py.checkBox( self.checkBoxList["DisableCustomImage"], query = True, value = True )
        except:
            disabled = False
            
        py.textField( self.textFieldList["CustomImagePath"], edit = True, enable = not disabled )
        py.button( self.buttonList["BrowseCustomImage"], edit = True, enable = not disabled )
        py.button( self.buttonList["UseRenderView"], edit = True, enable = not disabled )
        py.button( self.buttonList["ValidateCustomImage"], edit = True, enable = not disabled )
        py.text( self.textList["CustomImagePath"], edit = True, enable = not disabled )
        validateBackgroundColour = py.button( self.buttonList["ValidateCustomImage"], query = True, backgroundColor = True )
        newBackgroundColour = []
        for i in range( 3 ):
            #Calculate new background color
            if sum( validateBackgroundColour ) > 0:
                if disabled == True:
                    newBackgroundColour.append( validateBackgroundColour[i]/2 )
                else:
                    newBackgroundColour.append( validateBackgroundColour[i]*2 )
            py.button( self.buttonList["RenderView"][self.renderViewFormats[i]], edit = True, enable = not disabled )  
        if sum( validateBackgroundColour ) > 0:
            py.button( self.buttonList["ValidateCustomImage"], edit = True, backgroundColor = newBackgroundColour )


    @classmethod
    def checkPathToCustomImage( self ):
        
        #Get image information
        imageLocation = ImageStore().getImageLocation( py.textField( self.textFieldList["CustomImagePath"], query = True, text = True ) )
        imageHash = ImageStore( imageLocation ).cache( MD5 = True )
        
        #Test custom image
        valid = ImageStore( cleanTemporaryFiles = False ).write( testCustomImage = True, customImageLocation = imageLocation )

        if valid == True or py.textField( self.textFieldList["CustomImagePath"], query = True, text = True ) == "":
            self.validButton( "ValidateCustomImage", True )
        else:
            self.validButton( "ValidateCustomImage", False )
        
        #Read image
        if ImageStore().readImage( imageLocation ):
            py.checkBox( self.checkBoxList["CustomImageIsImage"], edit = True, value = True )
        else:
            py.checkBox( self.checkBoxList["CustomImageIsCached"], edit = True, value = False )
        
        #Read cache
        if ImageStore().cache( imageLocation ):
            py.checkBox( self.checkBoxList["CustomImageIsCached"], edit = True, value = True )
        else:
            py.checkBox( self.checkBoxList["CustomImageIsCached"], edit = True, value = False )
        
        ImageStore().renderView( False )

    
    @classmethod
    def useRenderView( self ):
        py.textField( self.textFieldList["CustomImagePath"], edit = True, text = "RenderView" )
        py.button( self.buttonList["ValidateCustomImage"], query = True, command = True )()


    @classmethod
    def changeSceneSettings( self, imageFormat = None ):
        if imageFormat:
            ImageStore().renderView( imageFormat )
        renderViewFormat, ignoreFormats, uploadFormats = ImageStore().imageFormats()
        currentFormat = renderViewFormat[py.getAttr( "defaultRenderGlobals.imageFormat" )][0]
        
        lightBackground = 0.3
        darkBackground = 0.2
        for i in range( 3 ):
            if currentFormat == self.renderViewFormats[i]:
                py.button( self.buttonList["RenderView"][currentFormat], edit = True, backgroundColor = ( lightBackground, lightBackground, lightBackground ) )
            else:
                py.button( self.buttonList["RenderView"][self.renderViewFormats[i]], edit = True, backgroundColor = ( darkBackground, darkBackground, darkBackground ) )

        
       
        
    @classmethod
    def checkPathToImage( self ):
        
        
        valid = False
        imageLocation = py.textField( self.textFieldList["MainImagePath"], query = True, text = True )
        
        #Update multiple images text box
        imageLocationPrefix = imageLocation
        if len( imageLocationPrefix ) > 4:
            if "." in imageLocationPrefix[-5:]:
                imageLocationPrefix = ".".join( imageLocationPrefix.split( "." )[:-1] )
            
        py.textField( self.textFieldList["MultipleImagesName"], edit = True, text = imageLocationPrefix + "." )
        
        #Check if image can be read
        if ImageStore().readImage( imageLocation ):
            py.checkBox( self.checkBoxList["ImagePathExists"], edit = True, value = True )
            valid = True
        else:
            py.checkBox( self.checkBoxList["ImagePathExists"], edit = True, value = False )
        
        #Check if image location can be written to
        content = None
        
        #Attempt to read
        try:
            with open( imageLocation ) as fileName:
                content = fileName.read()
        except:
            pass
        
        try:
            with open( imageLocation, "w" ) as fileName:
                if content:
                    fileName.write( content )
                else:
                    fileName.write( "test" )
            
            #Remove if it didn't exist to start with
            if not content:
                try:
                    os.remove( imageLocation )
                except:
                    pass
                
                
            py.checkBox( self.checkBoxList["ImagePathWriteable"], edit = True, value = True )
            valid = True
            
        except:
            py.checkBox( self.checkBoxList["ImagePathWriteable"], edit = True, value = False )
            
        if valid == True:
            self.validButton( "ValidateMainImage", True )
        else:
            self.validButton( "ValidateMainImage", False )
            

    @classmethod
    def fileReading( self, save = False, readImage = False, fieldType = None, fieldName = None, correspondingButton = None, updateIfNone = False ):
        
        #Set filter options
        filetypeFilter = "All Files (*.*)"
        if readImage == True:
            filetypeFilter = "PNG Files (*.png)"
            if save == False:
                filetypeFilter = "All Image Files (*.png *.jpg *.bmp *.psd *.jpeg);;PNG Files(*.png);;JPG Files(*.jpg *.jpeg);;BMP Files (*.bmp);;PSD Files (*.psd)"
        
        filePath = py.fileDialog2( fileFilter = filetypeFilter, fileMode = not save )
        
        #Send path to text box
        if filePath:
            command = "py.{0}( self.{1}, edit = True, text = '{2}' )".format( fieldType, "{0}List['{1}']".format( fieldType, fieldName ), filePath[0] )
            try:
                exec( command )
            except:
                pass

        #Check if image is valid
        if correspondingButton and ( updateIfNone or filePath ):
            command = "py.button( self.buttonList['{0}'], query = True, command = True )()".format( correspondingButton )
            try:
                exec( command )
            except:
                pass
        
        return filePath
            
        
UserInterface.display()
