from decimal import Decimal
from PIL import Image
import random as rd
import re
import cPickle
class ImageStore:

    def __init__( self, imageName="ImageDataStore" ):
        self.imageName = imageName

    def __repr__( self ):
        return "Use this to store or read data from an image.\n - ImageStore().write(input), ImageStore().read()\nYou can also define the name and location of the image.\n - ImageStore( 'C:\filename )'"
        
    def binaryConversion( self, input, **kwargs ):
        #Set up sequence order
        sequenceNumber = "0123456789"
        sequenceLetter = "abcdefghijklmnopqrstuvwxyz"
        sequenceSymbols = "=_%~:;?!+-<>{}()[]|£$&/^#"
        sequenceText = """, "'.\r\n*`@"""
        sequence = list( sequenceNumber ) + list( sequenceLetter ) + list( sequenceLetter.upper() ) + list( sequenceSymbols ) + list( sequenceText )
        #Check input values
        try:
            newBase = kwargs[ "new" ]
            if newBase == True or str( newBase ).lower() == "max":
                newBase = len( sequence )
        except:
            newBase = 2
        try:
            currentBase = kwargs[ "current" ]
        except:
            currentBase = len( sequence )  
        #Pickle results
        if currentBase == len( sequence ):
            input = cPickle.dumps( input )
        else:
            input = str( input )
        #Only run code once if there is no decimal point
        decimalNumber = 0
        originalNumberList = list( input )
        convertedIntegers = []
        for i in range( len( originalNumberList ) ):
            originalValue = originalNumberList[i]
            convertedIntegers.append( [index for index, x in enumerate( sequence[0:currentBase] ) if x == originalValue][0] )
            decimalNumber += convertedIntegers[-1]*currentBase**( len( originalNumberList )-i-1 )
        #Calculate how many integers the final number should have
        decimalRemainder = decimalNumber
        multiples = 0
        while decimalRemainder >= newBase:
            decimalRemainder /= newBase
            multiples += 1  
        #Convert to integer values of new base
        outputNumbers = []
        for i in range( multiples + 1 ):
            outputNumbers.append( decimalNumber / newBase ** ( multiples-i ) )
            decimalNumber -= outputNumbers[-1] * newBase ** ( multiples-i )
        output = ""
        #Convert to letters
        for i in range( len( outputNumbers ) ):
            output += str( sequence[ int( outputNumbers[i] ) ] )
        #Unpickle results
        if newBase == len( sequence ):
            return cPickle.loads( output )
        else:
            return output
        
    def write( self, input ):
        #Convert to binary
        convertedData = self.binaryConversion( input )
        #Split to 8 bytes
        byteData = re.findall( r'.{1,8}', convertedData, re.DOTALL )
        #Work out how many bytes are needed to fill the final colour
        remainingBytesAtEnd = str( self.binaryConversion( 8-len( byteData[-1] ), current=10 ) )
        #Add 'remaining bytes at end' to start of the list
        while len( remainingBytesAtEnd ) < 8:
            remainingBytesAtEnd = '0' + remainingBytesAtEnd
        while len( byteData[-1] ) < 8:
            byteData[-1] += '0'
        byteData = [remainingBytesAtEnd] + byteData
        #Pad with 9x white values
        for i in range( 9 ):
            byteData.append( '11111111' )
        #Make sure total amount is divisble by 3 and pad with full black
        remainderBy3 = len( byteData )%3
        for i in range( 3-remainderBy3 ):
            byteData.append( '00000000' )
        colourData = [ int( self.binaryConversion( bytes, current=2, new=10 ) ) for bytes in byteData ]
        
        #Sort out image
        minimumWidth = 6
        minimumHeight = int( round( pow( minimumWidth, 1/( 1/0.48-1 ) ) ) )
        ratioWidth = 0.52 #0.52 is close to 16:9 resolutions
        currentPixels = len( colourData )/3
        #Calculate width and height to use
        if currentPixels <= minimumWidth * minimumHeight:
            #Set to minimum values
            width = minimumWidth
            height = minimumHeight
        else:
            #Calculate based on ratio
            width = int( round( pow( currentPixels, ratioWidth ), -1 ) )
            #Make sure it is divisable by 3
            width /= 3
            width *= 3
            height = int( round( pow( width, 1/( 1/( 1-ratioWidth )-1 ) ), -1 ) )+5
            
        #Draw image
        imageOutput = Image.new("RGB", ( width, height ) )
        imageData = imageOutput.load()
        
        #Assign pixel colours
        for y in range( height-1 ):
            for x in range( width ):
                currentProgress = 3*( y*width+x )
                try:
                    dataR = colourData[currentProgress+0]
                    dataG = colourData[currentProgress+1]
                    dataB = colourData[currentProgress+2]
                except:
                    dataR = rd.randint( 0, 255 )
                    dataG = rd.randint( 0, 255 )
                    dataB = rd.randint( 0, 255 )
                imageData[x,y] = ( dataR, dataG, dataB )
        
        #Save image
        imageOutput.save( str( self.imageName ) + ".png", "PNG" )

    def read( self ):
        #Read image
        try:
            imageInput = Image.open( str( self.imageName ) + ".png" )
        except:
            return "No image found."
        rawData = []
        for pixels in imageInput.getdata():
            rawData.append( pixels[0] )
            rawData.append( pixels[1] )
            rawData.append( pixels[2] )
        #Convert back
        binaryData = [ self.binaryConversion( num, current=10, new=2 ) for num in rawData ]
        #Pad out values again as 0's were truncated
        for i in range( len( binaryData ) ):
            while len( binaryData[i] ) < 8:
                binaryData[i] = "0" + binaryData[i]
        joinedData = "".join( binaryData )
        #Get padding value
        padding = int( self.binaryConversion( joinedData[:8], current=2, new=10 ) )
        #Remove end values
        endingValue = ""
        for i in range( 9 ):
            endingValue += "11111111"
        endingValue += "00000000"
        #Truncate parts off
        originalBinaryData = joinedData[8:].split( endingValue )[0]
        #Fix for if padding is 0
        if padding > 0:
            originalBinaryData = originalBinaryData[0:-padding]
        
        return self.binaryConversion( originalBinaryData, current=2, new=True )
