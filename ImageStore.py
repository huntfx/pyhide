from PIL import Image
import cPickle
import base64

class ImageStore:

    def __init__( self, imageName="ImageDataStore" ):
        self.imageDataPadding = [116, 64, 84, 123, 93, 73, 106]
        self.imageName = imageName

    def __repr__( self ):
        return "Use this to store or read data from an image.\nUsage:\n - ImageStore().write(input), ImageStore().read()\nYou can also define the name and location of the image.\n - ImageStore( 'C:\filename )'"
    
    def write( self, input, widthRatio=0.52 ):
        
        encodedData = base64.b64encode( cPickle.dumps( input ) )
        pixelData = [int( format( ord( letter ) ) ) for letter in encodedData]
        pixelData += imageDataPadding
        #Pad to end with multiple of 3
        for i in range( 3-len( pixelData ) ):
            rawData += [255]
        
        #Set image info
        minimumWidth = 8
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
            #Make sure it is divisable by 3
            width /= 3
            width *= 3
            height = int( round( pow( width, 1/( 1/( 1-ratioWidth )-1 ) ), -1 ) )
                
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
                    dataR = rd.randint( 52, 128 )
                    dataG = rd.randint( 52, 128 )
                    dataB = rd.randint( 52, 128 )
                imageData[x,y] = ( dataR, dataG, dataB )
        
        #Save image
        imageOutput.save( str( self.imageName ) + ".png", "PNG" )
        return "Saved file: " + str( self.imageName ) + ".png"

    def read( self ):
        
        #Read image
        try:
            imageInput = Image.open( str( self.imageName ) + ".png" )
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
                while rawData[i+j] == imageDataPadding[j]:
                    j += 1
                    if j == len( imageDataPadding ):
                        rawData = rawData[0:i]
                        break
                if j == len( imageDataPadding ):
                    break
        except:
            print "File is probably corrupted."
        
        #Decode data    
        encodedData = "".join( [chr( pixel ) for pixel in rawData] )
        outputData = cPickle.loads( base64.b64decode( encodedData ) )
        
        return outputData
