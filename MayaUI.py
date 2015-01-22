import pymel.core as py
import os
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
    checkboxList = {}
    
    @classmethod
    def display( self ):

        if py.window( self.windowName, exists = True ):
            py.deleteUI( self.windowName, window = True )
        
        mainWindow = py.window( windowName, title = windowName, resizeToFitChildren = True, minimizeButton = True, maximizeButton = False, sizeable = False, width = self.windowWidth )
        
        with py.rowColumnLayout( numberOfColumns = 1 ):
            py.text( label = "Use this to store or read information within images. They can be uploaded anywhere and read from other computers.", align = "left" )
            py.text( label = "" )
        
        with py.rowColumnLayout( numberOfColumns = 7 ):
            py.text( label = "", width = windowWidth/100*1 )
            py.text( label = " Path to image:", width = windowWidth/100*50, align = "left" )
            py.text( label = "", width = windowWidth/100*1 )
            py.text( label = "", width = windowWidth/100*25 )
            py.text( label = "", width = windowWidth/100*1 )
            py.text( label = "", width = windowWidth/100*21 )
            py.text( label = "", width = windowWidth/100*1 )
            py.text( label = "" )
            self.textFieldList["ImagePath"] = py.textField( text = "{0}/{1}".format( ImageStore.defaultImageDirectory, ImageStore.defaultImageName ) )
            py.text( label = "" )
            
            with py.rowColumnLayout( numberOfColumns = 2 ):
                self.buttonList["NewImage"] = py.button( label = "New Image", width = windowWidth/100*12.5, command = py.Callback( self.fileReading, True, True, "textField", "textFieldList['ImagePath']", "buttonList['ValidateMainImage']" ) )
                self.buttonList["BrowseImage"] = py.button( label = "Browse", width = windowWidth/100*12.5, command = py.Callback( self.fileReading, False, True, "textField", "textFieldList['ImagePath']", "buttonList['ValidateMainImage']" ) )
                
            py.text( label = "" )
            self.buttonList["ValidateMainImage"] = py.button( label = "Check if valid", command = py.Callback( self.checkPathToImage ) )
            py.text( label = "" )
            py.text( label = "" )
            py.text( label = "" )
            py.text( label = "" )
            py.text( label = "" )
            py.text( label = "" )
            
            with py.rowColumnLayout( numberOfColumns = 2 ):
                self.checkboxList["ImagePathExists"] = py.checkBox( label="Exists", editable = False )
                self.checkboxList["ImagePathWriteable"] = py.checkBox( label="Writeable", editable = False )
                
            py.text( label = "" )
            py.text( label = "" )
            py.text( label=" Path to custom image:", align = "left" ) 
            py.text( label = "" )
            py.text( label = "" )
            py.text( label = "" )
            py.text( label = "" )
            py.text( label = "" )
            py.text( label = "" )
            self.textFieldList["CustomImagePath"] = py.textField( text = "http://images.peterhuntvfx.co.uk/music.jpg" )
            py.text( label = "" )
            
            with py.rowColumnLayout( numberOfColumns = 2 ):
                self.buttonList["BrowseCustomImage"] = py.button( label = "Browse", command = py.Callback( self.fileReading, False, True, "textField", "textFieldList['CustomImagePath']", "buttonList['ValidateCustomImage']" ))
                self.buttonList["UseRenderView"] = py.button( label = "Use Render View", command = py.Callback( self.useRenderView ) )
                
            py.text( label = "" )
            self.buttonList["ValidateCustomImage"] = py.button( label = "Check if valid", command = py.Callback( self.checkPathToCustomImage ) )
            py.text( label = "" )
            py.text( label = "" )
            self.checkboxList["DisableCustomImage"] = py.checkBox( label="Disable custom image", changeCommand = "UserInterface.disableCustomImage()" )
            
            py.text( label = "" )
            with py.rowColumnLayout( numberOfColumns = 2 ):
                py.button( label = "Browse", command = py.Callback( self.fileReading, False, True, "textField", "customImagePath" ), visible = False )
                with py.rowColumnLayout( numberOfColumns = 3 ):
                    self.buttonList["RenderView"] = {}
                    self.renderViewFormats = ["jpg", "png", "bmp"]
                    for i in range( 3 ):
                        self.buttonList["RenderView"][self.renderViewFormats[i]] = py.button( label = self.renderViewFormats[i].upper(), command = py.Callback( self.changeSceneSettings, self.renderViewFormats[i].lower() ) )
                    self.changeSceneSettings()
                    
            py.text( label = "" )
            
            with py.rowColumnLayout( numberOfColumns = 2 ):
                self.customImagePathIsImage = py.checkBox( label="Image", editable = False )
                self.customImagePathIsCached = py.checkBox( label="Cached", editable = False )
                
            py.text( label = "" )
            py.text( label = "" )
        
        py.showWindow()

    @classmethod
    def disableCustomImage( self ):
        
        #Fix due to an error happening on the first run of the code when the checkbox doesn't exist
        try:
            disabled = py.checkBox( self.checkboxList["DisableCustomImage"], query = True, value = True )
        except:
            disabled = False
            
        py.textField( self.textFieldList["CustomImagePath"], edit = True, enable = not disabled )
        py.button( self.buttonList["BrowseCustomImage"], edit = True, enable = not disabled )
        py.button( self.buttonList["UseRenderView"], edit = True, enable = not disabled )
        py.button( self.buttonList["ValidateCustomImage"], edit = True, enable = not disabled )
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
        if valid == True:
            py.button( self.buttonList["ValidateCustomImage"], edit = True, backgroundColor = ( 0, 1, 0 ) )
        else:
            py.button( self.buttonList["ValidateCustomImage"], edit = True, backgroundColor = ( 1, 0, 0 ) )
        
        #Read image
        if ImageStore().readImage( imageLocation ):
            py.checkBox( self.customImagePathIsImage, edit = True, value = True )
        else:
            py.checkBox( self.customImagePathIsCached, edit = True, value = False )
        
        #Read cache
        if ImageStore().cache( imageLocation ):
            py.checkBox( self.customImagePathIsCached, edit = True, value = True )
        else:
            py.checkBox( self.customImagePathIsCached, edit = True, value = False )
        
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
        imageLocation = py.textField( self.textFieldList["ImagePath"], query = True, text = True )
        
        #Check if image can be read
        print imageLocation
        if ImageStore().readImage( imageLocation ):
            py.checkBox( self.checkboxList["ImagePathExists"], edit = True, value = True )
            valid = True
        else:
            py.checkBox( self.checkboxList["ImagePathExists"], edit = True, value = False )
        
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
                
                
            py.checkBox( self.checkboxList["ImagePathWriteable"], edit = True, value = True )
            valid = True
            
        except:
            py.checkBox( self.checkboxList["ImagePathWriteable"], edit = True, value = False )
            
        if valid == True:
            py.button( self.buttonList["ValidateMainImage"], edit = True, backgroundColor = ( 0, 1, 0 ) )
        else:
            py.button( self.buttonList["ValidateMainImage"], edit = True, backgroundColor = ( 1, 0, 0 ) )
            

    @classmethod
    def fileReading( self, save = False, readImage = False, fieldType = None, fieldName = None, correspondingButton = None ):
        
        #Set filter options
        filetypeFilter = "All Files (*.*)"
        if readImage == True:
            filetypeFilter = "PNG Files (*.png)"
            if save == False:
                filetypeFilter = "All Image Files (*.png *.jpg *.bmp *.psd *.jpeg);;PNG Files(*.png);;JPG Files(*.jpg *.jpeg);;BMP Files (*.bmp);;PSD Files (*.psd)"
        
        filePath = py.fileDialog2( fileFilter = filetypeFilter, fileMode = not save )[0]
        
        #Send path to text box
        if filePath:
            command = "py.{0}( self.{1}, edit = True, text = '{2}' )".format( fieldType, fieldName, filePath )
            try:
                exec( command )
            except:
                pass

        #Check if image is valid
        if correspondingButton:
            command = "py.button( self.{0}, query = True, command = True )()".format( correspondingButton )
            try:
                exec( command )
            except:
                pass
            
        
UserInterface.display()
