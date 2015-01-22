import pymel.core as py

def fileReading( save = False, readImage = False, *args ):
    if save == True:
        filePath = py.fileDialog2( fileFilter = "PNG Files (*.png)" )
    else:
        if readImage == True:
            filePath = py.fileDialog( directoryMask = "*.png;;*.jpg;;*.bmp;;*.psd;;*.jpeg" )
        else:
            filePath = py.fileDialog()
    return filePath


windowName = "ImageStore"
try:
    py.deleteUI( windowName + "UI" )
except:
    pass

windowWidth = 550.0
tabLayoutLines = "---------------------------"

mainWindow = py.window( windowName + "UI", title = windowName, resizeToFitChildren = True, minimizeButton = True, maximizeButton = False, sizeable = False, width = windowWidth )

with py.rowColumnLayout( numberOfColumns = 1 ):
    py.text( label="Image Store code, this is just text to fill the space", align = "left" )

with py.rowColumnLayout( numberOfColumns = 7 ):
    py.text( label="", width = windowWidth/100*1 )
    py.text( label="", width = windowWidth/100*50 )
    py.text( label="", width = windowWidth/100*1 )
    py.text( label="", width = windowWidth/100*25 )
    py.text( label="", width = windowWidth/100*1 )
    py.text( label="", width = windowWidth/100*21 )
    py.text( label="", width = windowWidth/100*1 )
    py.text( label="" )
    py.text( label=" Path to image:", align = "left" )
    py.text( label="" )
    py.text( label="" )
    py.text( label="" )
    py.text( label="" )
    py.text( label="" )
    py.text( label="" )
    py.textField( text = "C:/Test.png" )
    py.text( label="" )
    with py.rowColumnLayout( numberOfColumns = 2 ):
        py.button( label = "New Image", width = windowWidth/100*12.5, command = py.Callback( fileReading, True ) )
        py.button( label = "Browse", width = windowWidth/100*12.5, command = py.Callback( fileReading, False, True ) )
    py.text( label="" )
    py.button( label = "Check if valid", command = py.Callback( fileReading, "generate" ), backgroundColor = (0,255,0) )
    py.text( label="" )
    py.text( label="" )
    py.text( label="" )
    py.text( label="" )
    py.text( label="" )
    py.text( label="" )
    with py.rowColumnLayout( numberOfColumns = 2 ):
        py.checkBox( label="Exists", editable = False )
        py.checkBox( label="Writeable", editable = False )
    py.text( label="" )
    py.text( label="" )
    py.text( label=" Path to custom image:", align = "left" ) 
    py.text( label="" )
    py.text( label="" )
    py.text( label="" )
    py.text( label="" )
    py.text( label="" )
    py.text( label="" )
    py.textField( text = "http://images.peterhuntvfx.co.uk/music.jpg" )
    py.text( label="" )
    with py.rowColumnLayout( numberOfColumns = 2 ):
        py.button( label = "Browse", command = py.Callback( fileReading, "generate" ))
        py.button( label = "Use Render View", command = py.Callback( fileReading, "generate" ) )
    py.text( label="" )
    py.button( label = "Check if valid", command = py.Callback( fileReading, "generate" ), backgroundColor = (128,128,0) )
    py.text( label="" )
    py.text( label="" )
    py.checkBox( label="Use custom image" )
    py.text( label="" )
    py.text( label="" )
    py.text( label="" )
    with py.rowColumnLayout( numberOfColumns = 2 ):
        py.checkBox( label="Image", editable = False )
        py.checkBox( label="Cached", editable = False )
    py.text( label="" )
    py.text( label="" )
    py.setParent( ".." )


with py.tabLayout( width = windowWidth ):
    
    with py.columnLayout( "Main" ):
        
        with py.frameLayout( label = "Write", collapsable = True, collapse = False, width = windowWidth/100*99.5 ):
            with py.rowColumnLayout( numberOfColumns = 3 ):
                with py.rowColumnLayout( numberOfColumns = 1, width = windowWidth/100*49 ):
                    py.text( label="   Input data:", align="left", width = windowWidth/100*45.2 )
                    py.textField( text = "Store this text in an image" )
                    with py.rowColumnLayout( numberOfColumns = 3 ):
                        py.radioCollection()
                        py.radioButton( label = "Convert input to string or integer", width = windowWidth/100*35.2, select = True )
                        py.text( label="" )
                        py.button( label = "Validate", visible = False )
                    with py.rowColumnLayout( numberOfColumns = 3 ):
                        py.radioButton( label = "Use input as code", width = windowWidth/100*35.2 )
                        py.text( label="" )
                        py.button( label = "Validate" )
                    with py.rowColumnLayout( numberOfColumns = 5 ):
                        py.radioButton( label = "Input is file path", width = windowWidth/100*26 )
                        py.text( label="" )
                        py.button( label = "Browse" )
                        py.text( label="" )
                        py.button( label = "Validate" )
                py.text( label="", width = windowWidth/100*1 )
                with py.rowColumnLayout( numberOfColumns = 1, width = windowWidth/100*49 ):
                    py.text( label="   Upload:", align="left" )
                    py.checkBox( label = "Upload output image" )
                    py.checkBox( label = "Open uploaded image in browser" )
                    py.checkBox( label = "Upload custom image (recommended)", value = True )
                    py.text( label="" )
                    py.text( label="   Set ratio of width to height:", align="left" )
                    py.floatSliderGrp( field = True )
            
        with py.frameLayout( label = "Read", collapsable = True, collapse = False, width = windowWidth/100*99.5 ):
            with py.rowColumnLayout( numberOfColumns = 3 ):
                with py.rowColumnLayout( numberOfColumns = 1, width = windowWidth/100*49 ):
                    py.radioCollection()
                    with py.rowColumnLayout( numberOfColumns = 3 ):
                        py.radioButton( label = "Return all data", select = True )
                        py.textField( width = windowWidth/100*10, visible = False )
                        py.text( label="" )
                    with py.rowColumnLayout( numberOfColumns = 3 ):
                        py.radioButton( label = "Return " )
                        py.textField( text = 100, width = windowWidth/100*10 )
                        py.text( label=" characters of data" )
                    py.text( label="" )
                    py.checkBox( label = "Use custom image path instead of stored URL" )
                py.text( label="", width = windowWidth/100*1 )
                with py.rowColumnLayout( numberOfColumns = 1, width = windowWidth/100*49 ):
                    py.checkBox( label = "Set as variable" )
                    py.textField( width = windowWidth/100*35 )
                    py.text( label="" )
                    py.checkBox( label = "Save as file" )
                    with py.rowColumnLayout( numberOfColumns = 3 ):
                        py.textField( width = windowWidth/100*35 )
                        py.text( label="" )
                        py.button( label = "Browse" )
                
                
        '''
        py.text( label="" )
        with py.rowColumnLayout( numberOfColumns = 5 ):
            py.text( label="", width = windowWidth/100*1 )
            py.text( label="{0}write{0}".format( tabLayoutLines ), enable = False, width = windowWidth/100*48 )
            py.text( label="", width = windowWidth/100*1 )
            py.text( label="{0}read{0}".format( tabLayoutLines ), enable = False, width = windowWidth/100*48 )
            py.text( label="", width = windowWidth/100*1 )
            py.text( label="" )
            with py.rowColumnLayout( numberOfColumns = 1 ):
                py.text( label="", width = windowWidth/100*45.2 )
                py.text( label="   Input data:", align="left" )
                py.textField( text = "Store this text in an image" )
                with py.rowColumnLayout( numberOfColumns = 3 ):
                    py.radioCollection()
                    py.radioButton( label = "Convert input to string or integer", width = windowWidth/100*35.2, select = True )
                    py.text( label="" )
                    py.button( label = "Validate", visible = False )
                with py.rowColumnLayout( numberOfColumns = 3 ):
                    py.radioButton( label = "Use input as code", width = windowWidth/100*35.2 )
                    py.text( label="" )
                    py.button( label = "Validate" )
                with py.rowColumnLayout( numberOfColumns = 5 ):
                    py.radioButton( label = "Read file from path", width = windowWidth/100*26 )
                    py.text( label="" )
                    py.button( label = "Browse" )
                    py.text( label="" )
                    py.button( label = "Validate" )
                py.text( label="" )
                py.checkBox( label = "Validate output image" )
                py.text( label="" )
                py.text( label="   Upload:", align="left" )
                py.checkBox( label = "Upload output image" )
                py.checkBox( label = "Open uploaded image in browser" )
                py.checkBox( label = "Upload custom image (recommended)", value = True )
                py.text( label="" )
                py.text( label="   Set ratio of width to height:", align="left" )
                py.floatSliderGrp( field = True )
            py.text( label="" )
            
            with py.rowColumnLayout( numberOfColumns = 1 ):
                py.text( label="", width = windowWidth/100*45.2 )
                py.checkBox( label = "Use custom image path instead of stored URL" )
                py.text( label="" )
                py.checkBox( label = "Display advanced information" )
                #py.scrollField( height = 40, width = windowWidth/100*47, enable = False, text = "Version Number:<br>Date Created:" )
                py.scrollField( height = 120, width = windowWidth/100*47, enable = False, text = "Version Number:<br>Date Created:<br><br>Bits Per Pixel:<br>Cutoff Mode:<br>Type of Data:<br>Length of Data:" )
                py.text( label="" )
                py.checkBox( label = "Set as variable" )
                py.textField( width = windowWidth/100*35 )
                py.text( label="" )
                py.checkBox( label = "Save as file" )
                with py.rowColumnLayout( numberOfColumns = 3 ):
                    py.textField( width = windowWidth/100*35 )
                    py.text( label="" )
                    py.button( label = "Browse" )
            py.text( label="" )
        '''
    with py.columnLayout( "Advanced" ):
        
        with py.frameLayout( label = "Write", collapsable = True, collapse = False, width = windowWidth/100*99.5 ):
            py.checkBox( label = "Validate output image" )
            py.checkBox( label = "Cancel if custom image is too small (otherwise the custom image will be automatically disabled)" )
            py.checkBox( label = "Save extra information into file    ", value = True )
            
        with py.frameLayout( label = "Cutoff Modes", collapsable = True, collapse = True, width = windowWidth/100*99.5 ):
            with py.rowColumnLayout( numberOfColumns = 1 ):
                #py.text( label = "{0}{0}cutoff modes{0}{0}".format( tabLayoutLines[:-2] ), enable = False, width = windowWidth )
                #py.text( label = "" )
                py.text( label = "   Cutoff modes define if the values should be added or subtracted based on the brightness of the pixel.", align = "left" )
                #py.text( label = "" )
            with py.rowColumnLayout( numberOfColumns = 5 ):
                py.text( label="", width = windowWidth/100*1 )
                with py.rowColumnLayout( numberOfColumns = 1, width = windowWidth/100*48 ):
                    py.checkBox( label = "Use all cutoff modes" )
                    py.text( label = "" )
                    py.text( label="   Select cutoff mode(s):", align="left", width = windowWidth/100*45.2 )
                    py.textField()
                    with py.rowColumnLayout( numberOfColumns = 16 ):
                        py.text( label = " 0 " )
                        py.checkBox( label = "" )
                        py.text( label = "  1 " )
                        py.checkBox( label = "" )
                        py.text( label = "  2 " )
                        py.checkBox( label = "" )
                        py.text( label = "  3 " )
                        py.checkBox( label = "" )
                        py.text( label = "  4 " )
                        py.checkBox( label = "" )
                        py.text( label = "  5 " )
                        py.checkBox( label = "" )
                        py.text( label = "  6 " )
                        py.checkBox( label = "" )
                        py.text( label = "  7 " )
                        py.checkBox( label = "" )
                    py.text( label = "" )
                    py.text( label="   File suffix used for saving multiple images:", align="left" )
                    with py.rowColumnLayout( numberOfColumns = 3, width = windowWidth/100*45.2 ):
                        py.textField( text = "C:/Test.", editable=False, width = windowWidth/100*27 )
                        py.textField( text = "m", width = windowWidth/100*12.7 )
                        py.textField( text = ".png", editable=False, width = windowWidth/100*5.5 )                
                    
                py.text( label="", width = windowWidth/100*1 )
                with py.rowColumnLayout( numberOfColumns = 1, width = windowWidth/100*48 ):
                    py.scrollField( wordWrap = True, height = 140, width = windowWidth/100*47, enable = False, text = "0: Move towards 0<br>1: Move towards 64<br>2: Move towards 128<br>3: Move towards 192<br>4: Move towards 255<br>5: Move away from 64<br>6: Move away from 128<br>7: Move away from 192" )
        
        with py.frameLayout( label = "Cache", collapsable = True, collapse = True, width = windowWidth/100*99.5 ):
            #with py.rowColumnLayout( numberOfColumns = 1 ):
            #    py.text( label = "{0}{0}cache{0}{0}".format( tabLayoutLines[:-2] ), enable = False, width = windowWidth )
            #    py.text( label = "" )
            with py.rowColumnLayout( numberOfColumns = 5 ):
                py.text( label="", width = windowWidth/100*1 )
                with py.rowColumnLayout( numberOfColumns = 1, width = windowWidth/100*48):
                    py.checkBox( label="Write information to cache file", value = True )
                    py.text( label = "" )
                    py.button( label = "Get MD5 hash of Custom Image", width = windowWidth/100*47 )
                    py.textField( text = "aek42mrwns9rew84mbfsn2", editable = False )
                    py.text( label = "" )
                    py.button( label = "Return Entire Cache Contents", width = windowWidth/100*47 )
                    
                py.text( label="", width = windowWidth/100*1 )
                with py.rowColumnLayout( numberOfColumns = 1, width = windowWidth/100*48):
                    
                    py.text( label = "", height = 8 )
                    py.text( label = "" )
                    py.text( label = "   Delete MD5 hash from cache:", align = "left" )
                    with py.rowColumnLayout( numberOfColumns = 3 ):
                        py.textField( width = windowWidth/100*35 )
                        py.text( label = "" )
                        py.button( label = "Delete", width = windowWidth/100*8 )
                    py.text( label = "" )
                    py.text( label = "   Return information for MD5 hash:", align = "left" )
                    with py.rowColumnLayout( numberOfColumns = 3 ):
                        py.textField( width = windowWidth/100*35 )
                        py.text( label = "" )
                        py.button( label = "Return", width = windowWidth/100*8 )
                        
                        
                py.text( label="", width = windowWidth/100*1 )
                
            py.text( label = "" )
            with py.frameLayout( label = "Cache Output", collapsable = True, collapse = True, width = windowWidth/100*99 ):
                cacheContents = 'Hash: 5a9c056738eda82ec764034a5e937534\r\n   URL: http://i.imgur.com/dQ6ikNW.jpg\r\n   Best cutoff mode: 2\r\n      Cutoff mode 2:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7776000\r\n         Storage with 6 bits per pixel: 9331188\r\n         Storage with 7 bits per pixel: 0\r\n         Storage with 8 bits per pixel: 0\r\nHash: 90383fe494bcc909208a8f7180fb1ddf\r\n   URL: http://i.imgur.com/iyiZLWY.jpg\r\n   Best cutoff mode: 4\r\n      Cutoff mode 1:\r\n         Storage with 1 bits per pixel: 6873833\r\n         Storage with 2 bits per pixel: 13671512\r\n         Storage with 3 bits per pixel: 20274759\r\n         Storage with 4 bits per pixel: 26373476\r\n         Storage with 5 bits per pixel: 30850355\r\n         Storage with 6 bits per pixel: 1340268\r\n         Storage with 7 bits per pixel: 874566\r\n         Storage with 8 bits per pixel: 0\r\n      Cutoff mode 2:\r\n         Storage with 1 bits per pixel: 6903676\r\n         Storage with 2 bits per pixel: 13790976\r\n         Storage with 3 bits per pixel: 20636049\r\n         Storage with 4 bits per pixel: 27366664\r\n         Storage with 5 bits per pixel: 33777420\r\n         Storage with 6 bits per pixel: 39124698\r\n         Storage with 7 bits per pixel: 0\r\n         Storage with 8 bits per pixel: 0\r\n      Cutoff mode 3:\r\n         Storage with 1 bits per pixel: 6909086\r\n         Storage with 2 bits per pixel: 13812058\r\n         Storage with 3 bits per pixel: 20697966\r\n         Storage with 4 bits per pixel: 27546844\r\n         Storage with 5 bits per pixel: 34284945\r\n         Storage with 6 bits per pixel: 40131732\r\n         Storage with 7 bits per pixel: 44770915\r\n         Storage with 8 bits per pixel: 0\r\n      Cutoff mode 4:\r\n         Storage with 1 bits per pixel: 6839972\r\n         Storage with 2 bits per pixel: 13659864\r\n         Storage with 3 bits per pixel: 20466672\r\n         Storage with 4 bits per pixel: 27270872\r\n         Storage with 5 bits per pixel: 34043285\r\n         Storage with 6 bits per pixel: 40722372\r\n         Storage with 7 bits per pixel: 46820354\r\n         Storage with 8 bits per pixel: 0\r\n      Cutoff mode 5:\r\n         Storage with 1 bits per pixel: 4133910\r\n         Storage with 2 bits per pixel: 6535900\r\n         Storage with 3 bits per pixel: 7324761\r\n         Storage with 4 bits per pixel: 6679252\r\n         Storage with 5 bits per pixel: 4767280\r\n         Storage with 6 bits per pixel: 2347302\r\n         Storage with 7 bits per pixel: 2049439\r\n         Storage with 8 bits per pixel: 0\r\n      Cutoff mode 6:\r\n         Storage with 1 bits per pixel: 4133910\r\n         Storage with 2 bits per pixel: 6535900\r\n         Storage with 3 bits per pixel: 7324761\r\n         Storage with 4 bits per pixel: 6679252\r\n         Storage with 5 bits per pixel: 4767280\r\n         Storage with 6 bits per pixel: 2347302\r\n         Storage with 7 bits per pixel: 0\r\n         Storage with 8 bits per pixel: 0\r\n      Cutoff mode 7:\r\n         Storage with 1 bits per pixel: 4133910\r\n         Storage with 2 bits per pixel: 6535900\r\n         Storage with 3 bits per pixel: 7324761\r\n         Storage with 4 bits per pixel: 6679252\r\n         Storage with 5 bits per pixel: 4767280\r\n         Storage with 6 bits per pixel: 2347302\r\n         Storage with 7 bits per pixel: 689080\r\n         Storage with 8 bits per pixel: 0\r\nHash: 9d656ee4d1dd6c8b104a00ba62e09909\r\n   Best cutoff mode: 3\r\n      Cutoff mode 3:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7776000\r\n         Storage with 6 bits per pixel: 9331200\r\n         Storage with 7 bits per pixel: 8920737\r\n         Storage with 8 bits per pixel: 0\r\nHash: 4ed87077f656bfe3f4539d4c6bd82cf6\r\n   URL: C:/Program Files/Autodesk/Maya2014/RenderViewTemp.psd\r\n   Best cutoff mode: 3\r\n      Cutoff mode 3:\r\n         Storage with 1 bits per pixel: 72\r\n         Storage with 2 bits per pixel: 144\r\n         Storage with 3 bits per pixel: 216\r\n         Storage with 4 bits per pixel: 288\r\n         Storage with 5 bits per pixel: 360\r\n         Storage with 6 bits per pixel: 432\r\n         Storage with 7 bits per pixel: 70\r\n         Storage with 8 bits per pixel: 0\r\nHash: f21744859db48fefbc55db605763b0e1\r\n   URL: http://i.imgur.com/tagkf1w.jpg\r\n   Best cutoff mode: 2\r\n      Cutoff mode 2:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7776000\r\n         Storage with 6 bits per pixel: 9331188\r\n         Storage with 7 bits per pixel: 0\r\n         Storage with 8 bits per pixel: 0\r\nHash: eece27b30736f3ddd634aae72186d429\r\n   URL: http://i.imgur.com/O3MiqH2.jpg\r\n   Best cutoff mode: 3\r\n      Cutoff mode 3:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7776000\r\n         Storage with 6 bits per pixel: 9331200\r\n         Storage with 7 bits per pixel: 8920982\r\n         Storage with 8 bits per pixel: 0\r\nHash: f8bf386a0c3484d46cc25710a601b82a\r\n   URL: http://i.imgur.com/rlxRtRc.jpg\r\n   Best cutoff mode: 2\r\n      Cutoff mode 2:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7776000\r\n         Storage with 6 bits per pixel: 9331188\r\n         Storage with 7 bits per pixel: 0\r\n         Storage with 8 bits per pixel: 0\r\nHash: dd7061d4183d48951489f8a6b0146285\r\n   URL: http://i.imgur.com/WWNVGiy.jpg\r\n   Best cutoff mode: 3\r\n      Cutoff mode 3:\r\n         Storage with 1 bits per pixel: 72\r\n         Storage with 2 bits per pixel: 144\r\n         Storage with 3 bits per pixel: 216\r\n         Storage with 4 bits per pixel: 288\r\n         Storage with 5 bits per pixel: 360\r\n         Storage with 6 bits per pixel: 432\r\n         Storage with 7 bits per pixel: 63\r\n         Storage with 8 bits per pixel: 0\r\nHash: 6902ebb71d183f38dbbff029974e82ae\r\n   URL: http://i.imgur.com/zGwIfBZ.jpg\r\n   Best cutoff mode: 2\r\n      Cutoff mode 2:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7776000\r\n         Storage with 6 bits per pixel: 9331188\r\n         Storage with 7 bits per pixel: 0\r\n         Storage with 8 bits per pixel: 0\r\nHash: 39f4fed0e72ded02921c2ca416dcf851\r\n   URL: http://i.imgur.com/YAX3Bsh.png\r\n   Best cutoff mode: 3\r\n      Cutoff mode 3:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7776000\r\n         Storage with 6 bits per pixel: 9331200\r\n         Storage with 7 bits per pixel: 10886358\r\n         Storage with 8 bits per pixel: 0\r\nHash: 218190c2a7301b21d2a460cdb083a0bb\r\n   URL: http://i.imgur.com/HTlV5qU.png\r\n   Best cutoff mode: 3\r\n      Cutoff mode 3:\r\n         Storage with 1 bits per pixel: 75\r\n         Storage with 2 bits per pixel: 150\r\n         Storage with 3 bits per pixel: 225\r\n         Storage with 4 bits per pixel: 300\r\n         Storage with 5 bits per pixel: 375\r\n         Storage with 6 bits per pixel: 450\r\n         Storage with 7 bits per pixel: 56\r\n         Storage with 8 bits per pixel: 0\r\nHash: 492bea8824b20c9d88fefcf903e007c9\r\n   URL: http://i.imgur.com/k7lLK8R.jpg\r\n   Best cutoff mode: 3\r\n      Cutoff mode 3:\r\n         Storage with 1 bits per pixel: 72\r\n         Storage with 2 bits per pixel: 144\r\n         Storage with 3 bits per pixel: 216\r\n         Storage with 4 bits per pixel: 288\r\n         Storage with 5 bits per pixel: 360\r\n         Storage with 6 bits per pixel: 432\r\n         Storage with 7 bits per pixel: 77\r\n         Storage with 8 bits per pixel: 0\r\nHash: 412e251a89f2fe729737b1d94d6c6260\r\n   Best cutoff mode: 3\r\n      Cutoff mode 3:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7776000\r\n         Storage with 6 bits per pixel: 9331200\r\n         Storage with 7 bits per pixel: 8920429\r\n         Storage with 8 bits per pixel: 0\r\nHash: 681eba84998fbe1b0ea9f03067596f26\r\n   URL: http://i.imgur.com/p1Z7KDl.jpg\r\n   Best cutoff mode: 3\r\n      Cutoff mode 3:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7776000\r\n         Storage with 6 bits per pixel: 9331200\r\n         Storage with 7 bits per pixel: 10886358\r\n         Storage with 8 bits per pixel: 0\r\nHash: a1e0feb70771a3722e40803f8f8957db\r\n   URL: http://i.imgur.com/OGSQ0Lo.jpg\r\n   Best cutoff mode: 4\r\n      Cutoff mode 4:\r\n         Storage with 1 bits per pixel: 170615\r\n         Storage with 2 bits per pixel: 341210\r\n         Storage with 3 bits per pixel: 511755\r\n         Storage with 4 bits per pixel: 681972\r\n         Storage with 5 bits per pixel: 849835\r\n         Storage with 6 bits per pixel: 1000032\r\n         Storage with 7 bits per pixel: 1065176\r\n         Storage with 8 bits per pixel: 0\r\nHash: b2a6f38bd78fbbb3e5728d0c22724209\r\n   URL: http://i.imgur.com/LvRCW7A.png\r\n   Best cutoff mode: 0\r\n      Cutoff mode 0:\r\n         Storage with 1 bits per pixel: 478095\r\n         Storage with 2 bits per pixel: 954210\r\n         Storage with 3 bits per pixel: 1427643\r\n         Storage with 4 bits per pixel: 1895556\r\n         Storage with 5 bits per pixel: 2349435\r\n         Storage with 6 bits per pixel: 2781828\r\n         Storage with 7 bits per pixel: 3047415\r\n         Storage with 8 bits per pixel: 0\r\nHash: 4be7f4f4cb5eb750a3c79a83ca671b48\r\n   URL: http://i.imgur.com/ZKv03zx.png\r\n   Best cutoff mode: 2\r\n      Cutoff mode 2:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7775995\r\n         Storage with 6 bits per pixel: 9331188\r\n         Storage with 7 bits per pixel: 0\r\n         Storage with 8 bits per pixel: 0\r\nHash: 3989b36fbb8bbe39804fac2f2da85968\r\n   URL: http://i.imgur.com/KUFENiC.jpg\r\n   Best cutoff mode: 2\r\n      Cutoff mode 2:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7776000\r\n         Storage with 6 bits per pixel: 9331188\r\n         Storage with 7 bits per pixel: 0\r\n         Storage with 8 bits per pixel: 0\r\nHash: af85411ef5142bd64afc19d5cfe56f9d\r\n   Best cutoff mode: 3\r\n      Cutoff mode 3:\r\n         Storage with 1 bits per pixel: 75\r\n         Storage with 2 bits per pixel: 150\r\n         Storage with 3 bits per pixel: 225\r\n         Storage with 4 bits per pixel: 300\r\n         Storage with 5 bits per pixel: 375\r\n         Storage with 6 bits per pixel: 450\r\n         Storage with 7 bits per pixel: 56\r\n         Storage with 8 bits per pixel: 0\r\nHash: 2aa11b32b8334d36d959e06bd0279c30\r\n   URL: http://i.imgur.com/gl9RRhq.png\r\n   Best cutoff mode: 4\r\n      Cutoff mode 4:\r\n         Storage with 1 bits per pixel: 75\r\n         Storage with 2 bits per pixel: 150\r\n         Storage with 3 bits per pixel: 225\r\n         Storage with 4 bits per pixel: 300\r\n         Storage with 5 bits per pixel: 375\r\n         Storage with 6 bits per pixel: 450\r\n         Storage with 7 bits per pixel: 518\r\n         Storage with 8 bits per pixel: 0\r\nHash: 3340e460bac942b371373670e49a6cf7\r\n   URL: http://i.imgur.com/kc9YLaP.png\r\n   Best cutoff mode: 3\r\n      Cutoff mode 3:\r\n         Storage with 1 bits per pixel: 108\r\n         Storage with 2 bits per pixel: 216\r\n         Storage with 3 bits per pixel: 324\r\n         Storage with 4 bits per pixel: 432\r\n         Storage with 5 bits per pixel: 540\r\n         Storage with 6 bits per pixel: 648\r\n         Storage with 7 bits per pixel: 140\r\n         Storage with 8 bits per pixel: 0\r\nHash: 591aa7b8cfbb7f2a0df4e39aed363818\r\n   URL: http://i.imgur.com/nhyNT9o.png\r\n   Best cutoff mode: 2\r\n      Cutoff mode 2:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7776000\r\n         Storage with 6 bits per pixel: 9331200\r\n         Storage with 7 bits per pixel: 0\r\n         Storage with 8 bits per pixel: 0\r\nHash: bcaec093bb276cde6b2e17835ec1ae9d\r\n   URL: http://i.imgur.com/iyiZLWY.jpg\r\n   Best cutoff mode: 4\r\n      Cutoff mode 4:\r\n         Storage with 1 bits per pixel: 6839972\r\n         Storage with 2 bits per pixel: 13659864\r\n         Storage with 3 bits per pixel: 20466672\r\n         Storage with 4 bits per pixel: 27270872\r\n         Storage with 5 bits per pixel: 34043285\r\n         Storage with 6 bits per pixel: 40722372\r\n         Storage with 7 bits per pixel: 46820354\r\n         Storage with 8 bits per pixel: 0\r\nHash: 7c8527244bdc22f8e099221e343f1a56\r\n   Best cutoff mode: 3\r\n      Cutoff mode 3:\r\n         Storage with 1 bits per pixel: 75\r\n         Storage with 2 bits per pixel: 150\r\n         Storage with 3 bits per pixel: 225\r\n         Storage with 4 bits per pixel: 300\r\n         Storage with 5 bits per pixel: 375\r\n         Storage with 6 bits per pixel: 450\r\n         Storage with 7 bits per pixel: 70\r\n         Storage with 8 bits per pixel: 0\r\nHash: 13673718fb38f2049ffa8e23cb5b9d82\r\n   URL: http://i.imgur.com/ydFhcDG.png\r\n   Best cutoff mode: 2\r\n      Cutoff mode 2:\r\n         Storage with 1 bits per pixel: 921600\r\n         Storage with 2 bits per pixel: 1843200\r\n         Storage with 3 bits per pixel: 2764800\r\n         Storage with 4 bits per pixel: 3686400\r\n         Storage with 5 bits per pixel: 4608000\r\n         Storage with 6 bits per pixel: 5529600\r\n         Storage with 7 bits per pixel: 0\r\n         Storage with 8 bits per pixel: 0\r\nHash: cf4e7de438ae4b5d59f3a688aac1405b\r\n   URL: http://i.imgur.com/LexgiK7.png\r\n   Best cutoff mode: 3\r\n      Cutoff mode 3:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7776000\r\n         Storage with 6 bits per pixel: 9331200\r\n         Storage with 7 bits per pixel: 10886358\r\n         Storage with 8 bits per pixel: 0\r\nHash: c1482abf1092c3581aad37adc902a685\r\n   URL: http://i.imgur.com/xMYe644.png\r\n   Best cutoff mode: 2\r\n      Cutoff mode 2:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7775995\r\n         Storage with 6 bits per pixel: 9331188\r\n         Storage with 7 bits per pixel: 0\r\n         Storage with 8 bits per pixel: 0\r\nHash: f71936d1f02af09a7eb6453f68b87eef\r\n   URL: C:/Program Files/Autodesk/Maya2014/RenderViewTemp.psd\r\n   Best cutoff mode: 3\r\n      Cutoff mode 3:\r\n         Storage with 1 bits per pixel: 72\r\n         Storage with 2 bits per pixel: 144\r\n         Storage with 3 bits per pixel: 216\r\n         Storage with 4 bits per pixel: 288\r\n         Storage with 5 bits per pixel: 360\r\n         Storage with 6 bits per pixel: 432\r\n         Storage with 7 bits per pixel: 70\r\n         Storage with 8 bits per pixel: 0\r\nHash: fd8f1ca54362636c80897b69515394d5\r\n   URL: http://i.imgur.com/CxNkNyf.png\r\n   Best cutoff mode: 2\r\n      Cutoff mode 2:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7775995\r\n         Storage with 6 bits per pixel: 9331188\r\n         Storage with 7 bits per pixel: 0\r\n         Storage with 8 bits per pixel: 0\r\nHash: 83d8cd3fec5967056fdbe78db620865a\r\n   URL: http://i.imgur.com/zz1peKp.jpg\r\n   Best cutoff mode: 2\r\n      Cutoff mode 2:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7776000\r\n         Storage with 6 bits per pixel: 9331188\r\n         Storage with 7 bits per pixel: 0\r\n         Storage with 8 bits per pixel: 0\r\nHash: d2c78293bb945d1dd0dd3bd89d0aa201\r\n   URL: http://i.imgur.com/dbUwcB2.png\r\n   Best cutoff mode: 3\r\n      Cutoff mode 3:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7776000\r\n         Storage with 6 bits per pixel: 9331200\r\n         Storage with 7 bits per pixel: 10886358\r\n         Storage with 8 bits per pixel: 0\r\nHash: 163c084c74848835494197e12e7efec3\r\n   URL: http://i.imgur.com/wYUOE0R.jpg\r\n   Best cutoff mode: 3\r\n      Cutoff mode 3:\r\n         Storage with 1 bits per pixel: 72\r\n         Storage with 2 bits per pixel: 144\r\n         Storage with 3 bits per pixel: 216\r\n         Storage with 4 bits per pixel: 288\r\n         Storage with 5 bits per pixel: 360\r\n         Storage with 6 bits per pixel: 432\r\n         Storage with 7 bits per pixel: 63\r\n         Storage with 8 bits per pixel: 0\r\nHash: ad626169197c6bf441918686e54f8b6a\r\n   URL: http://i.imgur.com/kmqbtkr.jpg\r\n   Best cutoff mode: 2\r\n      Cutoff mode 2:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7776000\r\n         Storage with 6 bits per pixel: 9331188\r\n         Storage with 7 bits per pixel: 0\r\n         Storage with 8 bits per pixel: 0\r\nHash: 14af176543d012ec5d7ecdcc968bf002\r\n   URL: http://i.imgur.com/Wkl7tW2.jpg\r\n   Best cutoff mode: 3\r\n      Cutoff mode 3:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7776000\r\n         Storage with 6 bits per pixel: 9331200\r\n         Storage with 7 bits per pixel: 8920947\r\n         Storage with 8 bits per pixel: 0\r\nHash: 5a8b2ab3c81f68f8605ba26376e31d60\r\n   URL: http://i.imgur.com/Ian5I6c.png\r\n   Best cutoff mode: 2\r\n      Cutoff mode 2:\r\n         Storage with 1 bits per pixel: 1555200\r\n         Storage with 2 bits per pixel: 3110400\r\n         Storage with 3 bits per pixel: 4665600\r\n         Storage with 4 bits per pixel: 6220800\r\n         Storage with 5 bits per pixel: 7775995\r\n         Storage with 6 bits per pixel: 9331188\r\n         Storage with 7 bits per pixel: 0\r\n         Storage with 8 bits per pixel: 0'
                newReplace = cacheContents.replace( "\r\n", "<br>" ).replace( "<br> ", "<br>&nbsp;" )
                while cacheContents != newReplace:
                    cacheContents = newReplace
                    newReplace = cacheContents.replace( "&nbsp; ", "&nbsp;&nbsp;" )
                
                py.scrollField( height = 200, text = cacheContents )
                    
                
        with py.frameLayout( label = "Other", collapsable = True, collapse = True, width = windowWidth/100*99.5 ):
            #with py.rowColumnLayout( numberOfColumns = 1 ):
            #    py.text( label = "" )
            #    py.text( label = "{0}{0}other{0}{0}".format( tabLayoutLines[:-2] ), enable = False, width = windowWidth )
            #    py.text( label = "" )
            py.checkBox( label = "Upload non Imgur URLs to Imgur", value = True )

    
    with py.columnLayout( "Debug" ):
        '''
        -return input size (b)
    	-return image size hold info (b)
    	
        
        '''
        with py.frameLayout( label = "Write", collapsable = True, collapse = True, width = windowWidth/100*99.5 ):
            with py.rowColumnLayout( numberOfColumns = 5 ):
                py.text( label="", width = windowWidth/100*1 )
                with py.rowColumnLayout( numberOfColumns = 1, width = windowWidth/100*48):
                    py.checkBox( label="Return URL to custom image after uploading", value = False )
                py.text( label="", width = windowWidth/100*1 )
                with py.rowColumnLayout( numberOfColumns = 1, width = windowWidth/100*48):
                    py.checkBox( label="Enable debug write mode", value = False )
                py.text( label="", width = windowWidth/100*1 )
        
        with py.frameLayout( label = "Size", collapsable = True, collapse = True, width = windowWidth/100*99.5 ):
            with py.rowColumnLayout( numberOfColumns = 5 ):
                py.text( label="", width = windowWidth/100*1 )
                with py.rowColumnLayout( numberOfColumns = 1, width = windowWidth/100*48):
                    py.text( label = "" )
                    py.button( label = "Calculate size of input value", width = windowWidth/100*48 )
                py.text( label="", width = windowWidth/100*1 )
                with py.rowColumnLayout( numberOfColumns = 1, width = windowWidth/100*48):
                    
                    py.text( label = "   Calculate how much data an image can hold:", align = "left" )
                    with py.rowColumnLayout( numberOfColumns = 3 ):
                        py.textField( width = windowWidth/100*35 )
                        py.text( label = "" )
                        py.button( label = "Read", width = windowWidth/100*8 )
                py.text( label="", width = windowWidth/100*1 )
            with py.rowColumnLayout( numberOfColumns = 3 ):
                py.text( label = "", width = windowWidth/100*1 )
                py.textField( text = "427753 bytes (427kb) to 75253753 bytes at 1 bit per colour", width = windowWidth/100*96, editable = False )
                py.text( label = "", width = windowWidth/100*1 )
                        


with py.rowColumnLayout( numberOfColumns = 5 ):
    py.text( label="", width = windowWidth/100*1 )
    py.button( label = "Write Image", width = windowWidth/100*49 )
    py.text( label = "", width = windowWidth/100*1 )
    py.button( label = "Read Image", width = windowWidth/100*49 )
    py.text( label = "", width = windowWidth/100*1 )
with py.rowColumnLayout( numberOfColumns = 3 ):
    py.text( label="", width = windowWidth/100*1 )
    py.text( label = "Current stage: Waiting for input", width = windowWidth/100*98.5 )
    py.text( label="", width = windowWidth/100*1 )
    py.text( label="" )
    py.progressBar( progress = 0 )
    py.text( label="" )
    
    
with py.rowColumnLayout( numberOfColumns = 1 ):
    with py.frameLayout( label = "Write Output", collapsable = True, collapse = True, visible = True, width = windowWidth/100*101 ):
        #with py.rowColumnLayout( numberOfColumns = 1 ):
        #    py.text( label = "" )
        #    py.text( label = "{0}{0}output{0}{0}".format( tabLayoutLines[:-1] ), enable = False, width = windowWidth )
        #    py.text( label = "" )
        
        with py.rowColumnLayout( numberOfColumns = 5 ):
            py.text( label="", width = windowWidth/100*1 )
            
            with py.rowColumnLayout( numberOfColumns = 1, width = windowWidth/100*48 ):
                py.text( label="   Path:", align = "left", width = windowWidth/100*45.2 )
                py.textField( text = "C:/test.png", editable = False )
        
        
            py.text( label="", width = windowWidth/100*1 )
            with py.rowColumnLayout( numberOfColumns = 1, width = windowWidth/100*48 ):
                py.text( label="   URL:", align = "left", width = windowWidth/100*45.2 )
                py.textField( text = "http://website.com/test.png", editable = False )
                
            py.text( label="", width = windowWidth/100*1 )
            py.text( label="" )
            py.text( label="" )
            py.text( label="" )
            py.text( label="" )
            py.text( label="" )
            py.text( label="" )
            
            with py.rowColumnLayout( numberOfColumns = 1, width = windowWidth/100*48 ):
                py.text( label="" )
                py.text( label="" )
                
            py.text( label="" )
            
            with py.rowColumnLayout( numberOfColumns = 1, width = windowWidth/100*48 ):
                py.text( label="   Custom Image URL:", align = "left", width = windowWidth/100*45.2 )
                py.textField( text = "C:/test.png", editable = False )
            py.text( label="" )
            
    with py.frameLayout( label = "Read Output", collapsable = True, collapse = True, visible = True, width = windowWidth/100*101, ann = "Test" ):
        py.scrollField( height = 260, editable = False, wordWrap = True, text = str( range( 1000 ) ) )



py.showWindow()
